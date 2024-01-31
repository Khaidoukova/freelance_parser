import os
import json
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv('.env')

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
username = os.getenv('TELEGRAM_USERNAME')

client = TelegramClient(username, api_id, api_hash, system_version="4.16.30-vxCUSTOM")


async def main():
    pass

if __name__ == '__main__':
    print('Бот запущен!')
    client.start()
    with client:
        client.loop.run_until_complete(main())
