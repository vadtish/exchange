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
        for record in data:
            effective_date = record['effectiveDate']
            usd_rate = next((rate['mid'] for rate in record['rates'] if rate['code'] == 'USD'), None)
            if usd_rate:
                dates.append(effective_date)
                usd_rates.append(usd_rate)

        plt.figure(figsize=(10, 5))
        plt.plot(dates, usd_rates, marker='o', linestyle='-', color='b')
        plt.xlabel('Date')
        plt.ylabel('USD Exchange Rate')
        plt.title('USD Exchange rate in a month')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('usd_exchange_rate.jpg')
        plt.close()

        return 'usd_exchange_rate.jpg'
    else:
        return None

def send_exchange_rate(bot, chat_id):
    file_path = fetch_exchange_rates()
    if file_path:
        with open(file_path, 'rb') as photo:
            bot.send_photo(chat_id, photo)

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Telegram bot for sending exchange rate charts.')
    parser.add_argument('--token', type=str, required=True, help='Telegram bot token')
    parser.add_argument('--chat_id', type=str, required=True, help='Telegram chat ID')
    args = parser.parse_args()

    # Создание и настройка бота
    bot = telebot.TeleBot(args.token)

    # Отправка курсов валют в указанный чат
    send_exchange_rate(bot, args.chat_id)

if __name__ == '__main__':
    main()
