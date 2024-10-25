import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import telebot
import argparse

def fetch_exchange_rates():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    api_url = f"https://api.nbp.pl/api/exchangerates/tables/a/{start_date_str}/{end_date_str}/"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        dates = []
        usd_rates = []
        eur_rates = []
        latest_usd = None
        latest_eur = None
        latest_date = None

        for record in data:
            effective_date = record['effectiveDate']
            usd_rate = next((rate['mid'] for rate in record['rates'] if rate['code'] == 'USD'), None)
            eur_rate = next((rate['mid'] for rate in record['rates'] if rate['code'] == 'EUR'), None)
            if usd_rate and eur_rate:
                dates.append(effective_date)
                usd_rates.append(usd_rate)
                eur_rates.append(eur_rate)
                latest_usd = usd_rate
                latest_eur = eur_rate
                latest_date = effective_date

        plt.figure(figsize=(10, 5))
        plt.plot(dates, usd_rates, marker='o', linestyle='-', color='b', label='USD')
        plt.plot(dates, eur_rates, marker='o', linestyle='-', color='g', label='EUR')
        plt.xlabel('Date')
        plt.ylabel('Exchange Rate')
        plt.title('USD and EUR Exchange Rates Over the Last Month')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('exchange_rates.jpg')
        plt.close()

        return 'exchange_rates.jpg', latest_date, latest_usd, latest_eur
    else:
        return None, None, None, None

def send_exchange_rate(bot, chat_id):
    file_path, latest_date, latest_usd, latest_eur = fetch_exchange_rates()
    if file_path:
        message = f"Курсы валют на {latest_date}:\nUSD: {latest_usd} PLN\nEUR: {latest_eur} PLN"
        bot.send_message(chat_id, message)

        with open(file_path, 'rb') as photo:
            bot.send_photo(chat_id, photo)

def main():
    parser = argparse.ArgumentParser(description='Telegram bot for sending exchange rate charts.')
    parser.add_argument('--token', type=str, required=True, help='Telegram bot token')
    parser.add_argument('--chat_id', type=str, required=True, help='Telegram chat ID')
    args = parser.parse_args()

    bot = telebot.TeleBot(args.token)
    send_exchange_rate(bot, args.chat_id)

if __name__ == '__main__':
    main()
