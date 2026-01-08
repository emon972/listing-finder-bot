import requests
import time

BOT_TOKEN = "8509158944:AAEuA56g35ueD2-3vh92ejH6laXfuS6GC64"
CHAT_ID = 1987110638

MAX_COINS = 5


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    })


def get_telegram_group(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        data = requests.get(url, timeout=15).json()
        tg = data["links"]["telegram_channel_identifier"]
        if tg:
            return f"https://t.me/{tg}"
    except:
        pass
    return None


def main():
    coins = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params={
            "vs_currency": "usd",
            "order": "market_cap_asc",
            "per_page": 20,
            "page": 1
        },
        timeout=15
    ).json()

    sent = 0

    for c in coins:
        if sent >= MAX_COINS:
            break

        tg_link = get_telegram_group(c["id"])
        if not tg_link:
            continue  # telegram group mandatory

        name = c["name"]
        symbol = c["symbol"].upper()
        cap = c["market_cap"]

        # 🔹 MESSAGE 1: TOKEN INFO
        token_info = (
            f"🪙 {name} (${symbol})\n"
            f"💰 Market Cap: ${cap}\n"
            f"🔗 CoinGecko: https://www.coingecko.com/en/coins/{c['id']}\n"
            f"💬 Telegram Group: {tg_link}\n\n"
            f"📌 Status: NOT LISTED ON BICONOMY"
        )

        send_message(token_info)
        time.sleep(2)

        # 🔹 MESSAGE 2: OUTREACH (COPY READY)
        outreach = (
            f"Greetings,\n\n"
            f"This is Dominic from Biconomy CEX’s official Listing Business Development team.\n"
            f"Biconomy is a top-tier centralized exchange listed on CoinMarketCap and CoinGecko, "
            f"serving 15M+ users with strong global reach.\n\n"
            f"We are currently expanding our listings and believe that ${symbol} "
            f"could be a strong fit for our platform.\n\n"
            f"Biconomy offers:\n"
            f"• High liquidity with active global traders\n"
            f"• Fast and transparent listing process\n"
            f"• Strong marketing support (AMAs, banners, KOL campaigns)\n"
            f"• IEO / Launchpad opportunities\n\n"
            f"We would be happy to connect and explore potential collaboration.\n"
            f"Please let us know the best contact to proceed.\n\n"
            f"Looking forward to your response."
        )

        send_message(outreach)
        time.sleep(3)

        sent += 1


if __name__ == "__main__":
    main()
