import requests
import time
import os

BOT_TOKEN = "8509158944:AAEuA56g35ueD2-3vh92ejH6laXfuS6GC64"
CHAT_ID = 1987110638

MAX_COINS = 5
SENT_FILE = "sent_tokens.txt"
MIN_MARKET_CAP = 1_000_000   # ✅ minimum 1 million


def load_sent_tokens():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_token(token_id):
    with open(SENT_FILE, "a") as f:
        f.write(token_id + "\n")


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    })


def get_telegram_group(coin_id):
    try:
        data = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}",
            timeout=15
        ).json()
        tg = data["links"]["telegram_channel_identifier"]
        if tg:
            return f"https://t.me/{tg}"
    except:
        pass
    return None


def main():
    sent_tokens = load_sent_tokens()

    coins = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params={
            "vs_currency": "usd",
            "order": "market_cap_asc",
            "per_page": 50,
            "page": 1
        },
        timeout=15
    ).json()

    sent_now = 0

    for c in coins:
        if sent_now >= MAX_COINS:
            break

        coin_id = c["id"]
        if coin_id in sent_tokens:
            continue

        cap = c["market_cap"] or 0
        if cap < MIN_MARKET_CAP:          # ✅ market cap filter
            continue

        tg_link = get_telegram_group(coin_id)
        if not tg_link:
            continue

        name = c["name"]
        symbol = c["symbol"].upper()

        # 🔹 MESSAGE 1: TOKEN INFO
        send_message(
            f"🪙 {name} (${symbol})\n"
            f"💰 Market Cap: ${cap}\n"
            f"🔗 CoinGecko: https://www.coingecko.com/en/coins/{coin_id}\n"
            f"💬 Telegram Group: {tg_link}\n\n"
            f"📌 Status: NOT LISTED ON BICONOMY"
        )
        time.sleep(2)

        # 🔹 MESSAGE 2: OUTREACH
        send_message(
            f"Greetings,\n\n"
            f"This is Dominic from Biconomy CEX’s official Listing Business Development team.\n"
            f"Biconomy is a top-tier centralized exchange listed on CoinMarketCap and CoinGecko.\n\n"
            f"We believe ${symbol} could be a strong fit for Biconomy.\n\n"
            f"• High liquidity & active traders\n"
            f"• Fast listing process\n"
            f"• Strong marketing support\n"
            f"• IEO / Launchpad opportunities\n\n"
            f"Please let us know the best contact to proceed."
        )
        time.sleep(3)

        save_token(coin_id)
        sent_tokens.add(coin_id)
        sent_now += 1


if __name__ == "__main__":
    main()
