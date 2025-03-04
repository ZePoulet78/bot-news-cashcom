import os
import discord
import asyncio
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))

RSS_FEEDS = [
    "https://www.cointribune.com/feed",
    "https://news.bitcoin.com/feed/",
    "https://cryptonaute.fr/feed/",
]

KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "xrp", "ripple", "crypto", "blockchain",
    "trading", "bull run", "bear market", "halving", "mining", "DeFi", "NFT",
    "SEC", "Trump", "Biden", "inflation", "Fed", "régulation", "geopolitique", "guerre"
]

sent_articles = set()

def fetch_rss_articles():
    new_articles = []
    today = datetime.now(timezone.utc).date() 

    for feed in RSS_FEEDS:
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6]).date()  
                if pub_date == today:  # Comparer avec la date du jour
                    if any(keyword.lower() in entry.title.lower() or keyword.lower() in entry.summary.lower() for keyword in KEYWORDS):
                        if entry.link not in sent_articles:
                            sent_articles.add(entry.link)
                            new_articles.append((entry.title, entry.link))
    return new_articles

def scrape_tradingview():
    url = "https://www.tradingview.com/news/"
    response = requests.get(url)
    new_articles = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("div", class_="tv-widget-news__item")

        for article in articles:
            title = article.find("span", class_="tv-widget-news__headline").text.strip()
            link = "https://www.tradingview.com" + article.find("a")["href"]

            if any(keyword.lower() in title.lower() for keyword in KEYWORDS) and link not in sent_articles:
                sent_articles.add(link)
                new_articles.append((title, link))
    return new_articles

def scrape_investing():
    url = "https://www.investing.com/news/cryptocurrency-news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    new_articles = []
    today = datetime.now().strftime("%b %d")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article", class_="js-article-item")

        for article in articles:
            title = article.find("a", class_="title").text.strip()
            link = "https://www.investing.com" + article.find("a")["href"]

            date_tag = article.find("span", class_="date")
            if date_tag and today in date_tag.text:  # Vérifie si la date correspond à aujourd'hui
                if any(keyword.lower() in title.lower() for keyword in KEYWORDS) and link not in sent_articles:
                    sent_articles.add(link)
                    new_articles.append((title, link))
    return new_articles

class RSSBot(discord.Client):
    async def on_ready(self):
        print(f'✅ Connecté en tant que {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        while True:
            articles = fetch_rss_articles() + scrape_tradingview() + scrape_investing()
            for title, link in articles:
                await channel.send(f"📰 **{title}**\n🔗 {link}")
            await asyncio.sleep(1800)

intents = discord.Intents.default()
client = RSSBot(intents=intents)
client.run(TOKEN)
