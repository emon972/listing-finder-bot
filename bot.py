import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def get_biconomy_symbols():
    try:
        url = "https://www.biconomy.com/api/market/coins"
        data = requests.get(url).json()
        return [c['symbol'].lower() for c in data['data']]
    except:
        return []

def get_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_asc",
        "per_page": 20,
        "page": 1
    }
    return requests.get(url, params=params).json()

def coin_details(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    d = requests.get(url).json()
    return {
        "website": d['links']['homepage'][0],
        "twitter": d['links']['twitter_screen_name'],
        "telegram": d['links']['telegram_channel_identifier']
    }

def run():
    send("🤖 Listing Finder Bot Running (GitHub)")
    biconomy = get_biconomy_symbols()
    coins = get_coins()

    for coin in coins:
        if coin['symbol'].lower() not in biconomy:
            details = coin_details(coin['id'])
            if not details['telegram']:
                continue

            msg = f"""
📌 COIN NOT ON BICONOMY

Name: {coin['name']}
Symbol: {coin['symbol'].upper()}
Market Cap: ${coin['market_cap']}

🌐 Website: {details['website']}
🐦 Twitter: https://twitter.com/{details['twitter']}
💬 Telegram: https://t.me/{details['telegram']}

🔗 CoinGecko:
https://www.coingecko.com/en/coins/{coin['id']}
"""
            send(msg)
            time.sleep(10)

run()
