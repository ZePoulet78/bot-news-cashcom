FROM python:3.9.21-slim-bookworm

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot_crypto_discord.py"]
