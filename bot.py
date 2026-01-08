import requests
import time
import os

BOT_TOKEN = "8509158944:AAEuA56g35ueD2-3vh92ejH6laXfuS6GC64"
CHAT_ID = 1987110638

MAX_COINS = 5
MIN_MARKET_CAP = 250_000
SENT_FILE = "sent_tokens.txt"


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
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": True
        }
    )


# ---------- COINGECKO ----------
def get_coins():
    try:
        return requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_asc",
                "per_page": 100,
                "page": 1
            },
            timeout=20
        ).json()
    except:
        return []


def get_telegram(coin_id):
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


# ---------- DEXSCREENER ----------
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

            # relaxed but useful filter
            if liq >= 3000 and vol >= 2000:
                return True
    except:
        pass
    return False


# ---------- MAIN ----------
def main():
    send_message("✅ Bot workflow started")

    sent = load_sent_tokens()
    coins = get_coins()
    sent_now = 0

    for c in coins:
        if sent_now >= MAX_COINS:
            break

        symbol = c["symbol"].upper()
        name = c["name"]
        mc = c["market_cap"]
        coin_id = c["id"]

        if not mc or mc < MIN_MARKET_CAP:
            continue

        if symbol.lower() in sent:
            continue

        tg = get_telegram(coin_id)
        if not tg:
            continue

        if not dex_ok(symbol):
            continue

        # ---- MESSAGE 1 ----
        send_message(
            f"🪙 {name} (${symbol})\n"
            f"💰 Market Cap: ${int(mc):,}\n"
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
