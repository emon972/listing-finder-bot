import requests
import csv
import os
import time

# ================= CONFIG =================
BOT_TOKEN = "PASTE_YOUR_NEW_BOT_TOKEN_HERE"
CHAT_ID = "1987110638"

MAX_COINS = 5

# Market cap range (good response projects)
MIN_MARKET_CAP = 300_000
MAX_MARKET_CAP = 20_000_000

SENT_FILE = "sent_coins.txt"
CSV_FILE = "output.csv"


# ================= TELEGRAM =================
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


# ================= STORAGE =================
def load_sent():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(line.strip() for line in f)


def save_sent(coin_id):
    with open(SENT_FILE, "a") as f:
        f.write(coin_id + "\n")


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
        "per_page": 50,
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


# ================= ACTIVE TELEGRAM =================
def is_active_telegram(username):
    try:
        r = requests.get(f"https://t.me/{username}", timeout=10)
        return r.status_code == 200
    except:
        return False


# ================= RESPONSE SCORE =================
def response_score(details):
    score = 0
    if details.get("telegram"):
        score += 3
    if details.get("twitter"):
        score += 2
    if details.get("website"):
        score += 2
    return score


# ================= CSV =================
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Name", "Symbol", "Market Cap",
                "Website", "Twitter", "Telegram", "CoinGecko"
            ])


def write_csv(row):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)


# ================= MAIN =================
def run():
    init_csv()

    sent_coins = load_sent()
    biconomy = get_biconomy_symbols()
    markets = get_coingecko_markets()

    # ---- PRIORITY FILTER ----
    filtered = []
    for coin in markets:
        market_cap = coin["market_cap"] or 0
        if market_cap < MIN_MARKET_CAP or market_cap > MAX_MARKET_CAP:
            continue

        details = get_coingecko_details(coin["id"])
        if not details or not details.get("telegram"):
            continue

        if not is_active_telegram(details["telegram"]):
            continue

        coin["details"] = details
        coin["score"] = response_score(details)
        filtered.append(coin)

    # High response first
    filtered.sort(key=lambda x: x["score"], reverse=True)

    sent = 0
    for coin in filtered:
        if sent >= MAX_COINS:
            break

        coin_id = coin["id"]
        symbol = coin["symbol"].lower()
        details = coin["details"]

        if coin_id in sent_coins:
            continue
        if symbol in biconomy:
            continue

        token_symbol = coin["symbol"].upper()

        # 1️⃣ Token info message
        info_message = f"""
📌 LISTING OPPORTUNITY (Not on Biconomy)

🪙 {coin['name']} ({token_symbol})
💰 Market Cap: ${coin['market_cap']}

🌐 Website: {details['website']}
🐦 Twitter: https://twitter.com/{details['twitter']}
💬 Telegram: https://t.me/{details['telegram']}

🔗 https://www.coingecko.com/en/coins/{coin_id}
"""
        send_message(info_message)
        time.sleep(1)

        # 2️⃣ Listing outreach message
        outreach_message = f"""
Greetings,

This is Dominic from Biconomy CEX’s official Listing Business Development team.
Biconomy is a top-tier centralized exchange listed on both CoinMarketCap and CoinGecko, serving 15M+ users with strong global reach.

We are currently expanding our listings and believe that ${token_symbol} could be a strong fit for our platform.

Biconomy offers:
• High liquidity with active global traders
• Fast and transparent listing process
• Strong marketing support (AMAs, banners, KOL campaigns)
• IEO / Launchpad opportunities

We would be happy to connect and explore potential collaboration.
Please let us know the best contact to proceed.

Looking forward to your response.
"""
        send_message(outreach_message)

        write_csv([
            coin["name"],
            token_symbol,
            coin["market_cap"],
            details["website"],
            f"https://twitter.com/{details['twitter']}",
            f"https://t.me/{details['telegram']}",
            f"https://www.coingecko.com/en/coins/{coin_id}"
        ])

        save_sent(coin_id)
        sent += 1
        time.sleep(1)


run()
