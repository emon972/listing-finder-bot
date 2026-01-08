import requests
import time
import os

# ================= CONFIG =================
BOT_TOKEN = "8509158944:AAEuA56g35ueD2-3vh92ejH6laXfuS6GC64"
CHAT_ID = 1987110638

CMC_API_KEY = "9b0b885a4f3c4cc998a4a10c0b911bd0"

MAX_COINS = 5
MIN_MARKET_CAP = 250_000
SENT_FILE = "sent_tokens.txt"
# =========================================


# ---------- STORAGE ----------
def load_sent_tokens():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(x.strip().lower() for x in f.readlines())


def save_token(symbol):
    with open(SENT_FILE, "a") as f:
        f.write(symbol.lower() + "\n")


# ---------- TELEGRAM ----------
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    })


# ---------- COINGECKO FULL COINS ----------
def get_coingecko_coins():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_asc",
                "per_page": 100,
                "page": 1
            },
            timeout=15
        ).json()
        return r
    except:
        return []


def get_coingecko_telegram(coin_id):
    try:
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}",
            timeout=15
        ).json()
        tg = r["links"]["telegram_channel_identifier"]
        if tg:
            return f"https://t.me/{tg}"
    except:
        pass
    return None


# ---------- COINMARKETCAP ----------
def get_cmc_tokens():
    try:
        r = requests.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",
            headers={"X-CMC_PRO_API_KEY": CMC_API_KEY},
            params={
                "start": 1,
                "limit": 100,
                "convert": "USD",
                "sort": "market_cap",
                "sort_dir": "asc"
            },
            timeout=15
        ).json()
        return r.get("data", [])
    except:
        return []


# ---------- DEXSCREENER ----------
def dex_activity_ok(symbol):
    try:
        r = requests.get(
            "https://api.dexscreener.com/latest/dex/search",
            params={"q": symbol},
            timeout=15
        ).json()

        for p in r.get("pairs", []):
            liq = p.get("liquidity", {}).get("usd", 0)
            vol = p.get("volume", {}).get("h24", 0)
            price = p.get("priceChange", {}).get("h24", 0)

            if liq >= 10_000 and vol >= 5_000 and abs(price) >= 1:
                return True
    except:
        pass
    return False


# ---------- MAIN ----------
def main():
    send_message("✅ Bot workflow started")

    sent = load_sent_tokens()
    sent_now = 0

    cmc = get_cmc_tokens()
    cg = get_coingecko_coins()

    # merge both sources
    combined = []

    for c in cmc:
        combined.append({
            "name": c["name"],
            "symbol": c["symbol"],
            "mc": c["quote"]["USD"]["market_cap"],
            "id": c["slug"],
            "src": "CMC"
        })

    for c in cg:
        combined.append({
            "name": c["name"],
            "symbol": c["symbol"].upper(),
            "mc": c["market_cap"] or 0,
            "id": c["id"],
            "src": "CG"
        })

    for c in combined:
        if sent_now >= MAX_COINS:
            break

        symbol = c["symbol"]
        name = c["name"]
        mc = c["mc"]
        coin_id = c["id"]

        if mc < MIN_MARKET_CAP:
            continue

        if symbol.lower() in sent:
            continue

        tg = get_coingecko_telegram(coin_id)
        if not tg:
            continue

        if not dex_activity_ok(symbol):
            continue

        # -------- TOKEN INFO --------
        send_message(
            f"🪙 {name} (${symbol})\n"
            f"💰 Market Cap: ${int(mc):,}\n"
            f"📊 Source: {c['src']}\n"
            f"📈 Dex: https://dexscreener.com/search?q={symbol}\n"
            f"💬 Telegram: {tg}\n\n"
            f"📌 Status: NOT LISTED ON BICONOMY"
        )
        time.sleep(2)

        # -------- OUTREACH --------
        send_message(
            f"Greetings,\n\n"
            f"This is Dominic from Biconomy CEX’s official Listing Business Development team.\n"
            f"We believe ${symbol} could be a strong fit for Biconomy.\n\n"
            f"• High liquidity\n"
            f"• Fast listing\n"
            f"• Marketing & Launchpad support\n\n"
            f"Please let us know the best contact to proceed."
        )
        time.sleep(3)

        save_token(symbol)
        sent.add(symbol.lower())
        sent_now += 1


if __name__ == "__main__":
    main()
