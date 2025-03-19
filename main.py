import requests
import time
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import telebot
import argparse


def retry_request(func, *args, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            return func(*args, timeout=60)  
        except requests.exceptions.ReadTimeout:
            print(f"Попытка {attempt + 1}: Таймаут, жду {delay} сек...")
            time.sleep(delay)
        except Exception as e:
            print(f"Ошибка: {e}")
            break

def fetch_exchange_rates():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    api_url = f"https://api.nbp.pl/api/exchangerates/tables/a/{start_date_str}/{end_date_str}/"
    
    session = requests.Session()  
    session.timeout = 60 
    
    try:
        response = session.get(api_url, timeout=60)  
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Ошибка: Таймаут при запросе к API")
        return None, None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        return None, None, None, None

    if response.status_code == 200:
        data = response.json()
        dates, usd_rates, eur_rates = [], [], []
        latest_usd, latest_eur, latest_date = None, None, None

        for record in data:
            effective_date = record['effectiveDate']
            usd_rate = next((rate['mid'] for rate in record['rates'] if rate['code'] == 'USD'), None)
            eur_rate = next((rate['mid'] for rate in record['rates'] if rate['code'] == 'EUR'), None)
            if usd_rate and eur_rate:
                dates.append(effective_date)
                usd_rates.append(usd_rate)
                eur_rates.append(eur_rate)
                latest_usd, latest_eur, latest_date = usd_rate, eur_rate, effective_date

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

        retry_request(bot.send_message, chat_id, message)

        with open(file_path, 'rb') as photo:
            retry_request(bot.send_photo, chat_id, photo)

def main():
    parser = argparse.ArgumentParser(description='Telegram bot for sending exchange rate charts.')
    parser.add_argument('--token', type=str, required=True, help='Telegram bot token')
    parser.add_argument('--chat_id', type=str, required=True, help='Telegram chat ID')
    args = parser.parse_args()

    bot = telebot.TeleBot(args.token, parse_mode="HTML")  # Без timeout
    send_exchange_rate(bot, args.chat_id)

if __name__ == '__main__':
    main()
