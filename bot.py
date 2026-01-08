import requests
import time

# ================= TELEGRAM =================
BOT_TOKEN = "PASTE_YOUR_NEW_BOT_TOKEN_HERE"
CHAT_ID = "1987110638"

MAX_COINS = 5  # প্রতি run এ সর্বোচ্চ কয়টা coin পাঠাবে


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload)
    if r.status_code != 200:
        raise Exception(r.text)


# ================= BICONOMY =================
def get_biconomy_symbols():
    try:
        url = "https://www.biconomy.com/api/market/coins"
        data = requests.get(url, timeout=10).json()
        return set(c["symbol"].lower() for c in data["data"])
    except:
        return set()


# ================= COINGECKO =================
def get_coingecko_markets():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_asc",
        "per_page": 30,
        "page": 1
    }
    return requests.get(url, params=params, timeout=10).json()


def get_coingecko_details(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        d = requests.get(url, timeout=10).json()
        return {
            "telegram": d["links"]["telegram_channel_identifier"],
            "twitter": d["links"]["twitter_screen_name"],
            "website": d["links"]["homepage"][0]
        }
    except:
        return None


# ================= MAIN LOGIC =================
def run():
    biconomy_symbols = get_biconomy_symbols()
    sent = 0

    coins = get_coingecko_markets()

    for coin in coins:
        if sent >= MAX_COINS:
            break

        symbol = coin["symbol"].lower()
        if symbol in biconomy_symbols:
            continue

        details = get_coingecko_details(coin["id"])
        if not details:
            continue

        if not details["telegram"]:
            continue  # Telegram group না থাকলে skip

        message = f"""
📌 NOT LISTED ON BICONOMY

🪙 Name: {coin['name']}
🔤 Symbol: {coin['symbol'].upper()}
💰 Market Cap: ${coin['market_cap']}

🌐 Website: {details['website']}
🐦 Twitter: https://twitter.com/{details['twitter']}
💬 Telegram: https://t.me/{details['telegram']}

🔗 CoinGecko:
https://www.coingecko.com/en/coins/{coin['id']}
"""

        send_message(message)
        sent += 1
        time.sleep(1)


run()
