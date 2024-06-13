import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import telebot
import os
import json
import argparse

# Файл для хранения данных пользователей
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def fetch_exchange_rates():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=31)
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
        plt.title('USD Exchange Rate Over the Last Two Weeks')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('usd_exchange_rate.jpg')
        plt.close()

        return 'usd_exchange_rate.jpg'
    else:
        return None

def send_exchange_rate(bot):
    users = load_users()
    file_path = fetch_exchange_rates()
    if file_path:
        for user in users:
            with open(file_path, 'rb') as photo:
                bot.send_photo(user, photo)

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Telegram bot for sending exchange rate charts.')
    parser.add_argument('--token', type=str, required=True, help='Telegram bot token')
    args = parser.parse_args()

    # Создание и настройка бота
    bot = telebot.TeleBot(args.token)

    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.chat.id
        users = load_users()
        if user_id not in users:
            users.append(user_id)
            save_users(users)
            bot.reply_to(message, 'Вы подписаны на ежедневную рассылку курсов валют.')
        else:
            bot.reply_to(message, 'Вы уже подписаны на рассылку.')

    @bot.message_handler(commands=['stop'])
    def stop(message):
        user_id = message.chat.id
        users = load_users()
        if user_id in users:
            users.remove(user_id)
            save_users(users)
            bot.reply_to(message, 'Вы отписаны от ежедневной рассылки курсов валют.')
        else:
            bot.reply_to(message, 'Вы не подписаны на рассылку.')

    # Запускаем бота для обработки команд /start и /stop
    bot.polling(none_stop=False, interval=0, timeout=20)

    # Отправляем курсы валют всем пользователям
    send_exchange_rate(bot)

if __name__ == '__main__':
    main()
