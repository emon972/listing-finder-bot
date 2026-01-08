import requests
import time
import os

BOT_TOKEN = "8509158944:AAEuA56g35ueD2-3vh92ejH6laXfuS6GC64"
CHAT_ID = 1987110638

MAX_COINS = 5
SENT_FILE = "sent_tokens.txt"
MIN_MARKET_CAP = 500_000


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    })
    print("Telegram response:", r.text)


def get_telegram_group(coin_id):
    try:
        d = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}",
            timeout=15
        ).json()
        tg = d["links"]["telegram_channel_identifier"]
        if tg:
            return f"https://t.me/{tg}"
    except Exception as e:
        print("TG fetch error:", e)
    return None


def main():
    send_message("✅ Bot workflow started")
    time.sleep(2)

    sent_tokens = set()
    if os.path.exists(SENT_FILE):
        sent_tokens = set(open(SENT_FILE).read().splitlines())

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

    print("Coins fetched:", len(coins))

    sent_now = 0
    for c in coins:
        if sent_now >= MAX_COINS:
            break

        coin_id = c["id"]
        cap = c["market_cap"] or 0

        if cap < MIN_MARKET_CAP or coin_id in sent_tokens:
            continue

        tg = get_telegram_group(coin_id)
        if not tg:
            continue

        send_message(
            f"{c['name']} (${c['symbol'].upper()})\n"
            f"Market Cap: ${cap}\n"
            f"Telegram: {tg}"
        )

        sent_tokens.add(coin_id)
        open(SENT_FILE, "a").write(coin_id + "\n")
        sent_now += 1
        time.sleep(3)


if __name__ == "__main__":
    main()
