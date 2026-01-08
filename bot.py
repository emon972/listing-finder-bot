import requests

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

    message = "📌 **BICONOMY LISTING OPPORTUNITIES**\n( Auto • Every 5 Minutes )\n\n"

    count = 0
    for c in coins:
        if count >= MAX_COINS:
            break

        name = c["name"]
        symbol = c["symbol"].upper()
        cap = c["market_cap"]

        message += (
            f"🪙 {name} (${symbol})\n"
            f"💰 Market Cap: ${cap}\n"
            f"🔗 https://www.coingecko.com/en/coins/{c['id']}\n\n"
            f"📨 Outreach Message:\n"
            f"Greetings,\n\n"
            f"This is Dominic from Biconomy CEX’s official Listing Business Development team.\n"
            f"Biconomy is a top-tier centralized exchange listed on CoinMarketCap & CoinGecko, "
            f"serving 15M+ users globally.\n\n"
            f"We believe ${symbol} could be a strong fit for Biconomy.\n\n"
            f"• High liquidity & active traders\n"
            f"• Fast & transparent listing\n"
            f"• Strong marketing (AMA, banners, KOLs)\n"
            f"• IEO / Launchpad support\n\n"
            f"Please let us know the best contact to proceed.\n"
            f"———————————————\n\n"
        )

        count += 1

    send_message(message)


if __name__ == "__main__":
    main()
