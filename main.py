import os
from dotenv import load_dotenv
from telethon import TelegramClient
from datetime import datetime, timedelta

from service import search_messages

load_dotenv('.env')

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
username = os.getenv('TELEGRAM_USERNAME')

client = TelegramClient(username, api_id, api_hash, system_version="4.16.30-vxCUSTOM")

tg_channels = ['@zakazyfreelance']
tg_keywords = ['python', 'дизайн']


async def main(channels, keywords):
    for channel in channels:

        offset_file = f'offset_{channel}.txt'
        offset_date = datetime.now() - timedelta(days=365)

        try:
            with open(offset_file, 'r') as file:
                offset_data = file.read().strip()

                if offset_data:  # Проверка, что строка не пустая
                    offset_date = datetime.strptime(offset_data, '%Y-%m-%d %H:%M:%S')

        except FileNotFoundError:
            pass

        await search_messages(channel, keywords, offset_date, client)
        await client.disconnect()

if __name__ == '__main__':
    print('Бот запущен!')
    client.start()
    with client:
        client.loop.run_until_complete(main(tg_channels, tg_keywords))
