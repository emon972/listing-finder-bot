import requests
import time
import os

# ---------------- CONFIG ----------------
BOT_TOKEN = "8509158944:AAEuA56g35ueD2-3vh92ejH6laXfuS6GC64"
CHAT_ID = 1987110638

CMC_API_KEY = "9b0b885a4f3c4cc998a4a10c0b911bd0"

MAX_COINS = 5
MIN_MARKET_CAP = 250_000
SENT_FILE = "sent_tokens.txt"

# ---------------- STORAGE ----------------
def load_sent_tokens():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(x.strip().lower() for x in f.readlines())

def save_token(symbol):
    with open(SENT_FILE, "a") as f:
        f.write(symbol.lower() + "\n")

# ---------------- TELEGRAM ----------------
def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": True
        },
        timeout=15
    )

# ---------------- COINGECKO ----------------
def get_coingecko():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_asc",
                "per_page": 150,
                "page": 1
            },
            timeout=20
        ).json()
        return r
    except:
        return []

def get_cg_telegram(coin_id):
    try:
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}",
            timeout=20
        ).json()
        tg = r["links"]["telegram_channel_identifier"]
        if tg:
            return f"https://t.me/{tg}"
    except:
        pass
    return None

# ---------------- COINMARKETCAP ----------------
def cmc_marketcap(symbol):
    try:
        r = requests.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
            headers={"X-CMC_PRO_API_KEY": CMC_API_KEY},
            params={"symbol": symbol},
            timeout=20
        ).json()

        data = r["data"][symbol]["quote"]["USD"]
        return data["market_cap"], data["volume_24h"]
    except:
        return None, None

# ---------------- DEXSCREENER ----------------
def dex_ok(symbol):
    try:
        r = requests.get(
            "https://api.dexscreener.com/latest/dex/search",
            params={"q": symbol},
            timeout=15
        ).json()

        for p in r.get("pairs", []):
            liq = p.get("liquidity", {}).get("usd", 0)
            vol = p.get("volume", {}).get("h24", 0)

            if liq >= 3000 and vol >= 2000:
                return True
    except:
        pass
    return False

# ---------------- MAIN ----------------
def main():
    sent = load_sent_tokens()
    coins = get_coingecko()
    sent_now = 0

    for c in coins:
        if sent_now >= MAX_COINS:
            break

        symbol = c["symbol"].upper()
        name = c["name"]
        cg_mc = c.get("market_cap", 0)
        coin_id = c["id"]

        if symbol.lower() in sent:
            continue

        # ---- CG MarketCap check ----
        if not cg_mc or cg_mc < MIN_MARKET_CAP:
            continue

        # ---- CMC confirm ----
        cmc_mc, cmc_vol = cmc_marketcap(symbol)
        if not cmc_mc or cmc_mc < MIN_MARKET_CAP or cmc_vol < 50_000:
            continue

        # ---- Telegram mandatory ----
        tg = get_cg_telegram(coin_id)
        if not tg:
            continue

        # ---- DEX Trading check ----
        if not dex_ok(symbol):
            continue

        # ---- MESSAGE 1 ----
        send_message(
            f"🪙 {name} (${symbol})\n"
            f"💰 Market Cap: ${int(cmc_mc):,}\n"
            f"📊 CoinGecko: https://www.coingecko.com/en/coins/{coin_id}\n"
            f"📈 Dex: https://dexscreener.com/search?q={symbol}\n"
            f"💬 Telegram: {tg}\n\n"
            f"📌 Status: NOT LISTED ON BICONOMY"
        )
        time.sleep(2)

        # ---- MESSAGE 2 ----
        send_message(
            f"Greetings,\n\n"
            f"This is Dominic from Biconomy CEX’s official Listing Business Development team.\n"
            f"We believe ${symbol} could be a strong fit for Biconomy.\n\n"
            f"• Active trading\n"
            f"• Fast listing\n"
            f"• Marketing support\n\n"
            f"Please share the best contact to proceed."
        )
        time.sleep(3)

        save_token(symbol)
        sent.add(symbol.lower())
        sent_now += 1

if __name__ == "__main__":
    main()
