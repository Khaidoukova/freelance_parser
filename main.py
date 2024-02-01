import os
import json
from dotenv import load_dotenv
from pytz import UTC
from telethon import TelegramClient
from datetime import datetime, timedelta
load_dotenv('.env')

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
username = os.getenv('TELEGRAM_USERNAME')

client = TelegramClient(username, api_id, api_hash, system_version="4.16.30-vxCUSTOM")

async def search_messages(channel, keywords, offset_date):
    all_messages = []
    offset_file = f'offset_{channel}.txt'
    result_file = f'result_{channel}.json'

    # Получение объекта канала по username
    entity = await client.get_entity(channel)

    offset_date_naive = offset_date.replace(tzinfo=UTC)
    # проходим циклом по ключевым словам
    for word in keywords:

        async for message in client.iter_messages(entity, search=word):
            if message.date <= offset_date_naive:
                break

            if word in message.message:

                data = {
                    'message': message.text,
                    'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'user_id': message.from_id.user_id if getattr(message.from_id, 'user_id', None) else None
                }
                #print(data)
                all_messages.append(data)
    # Сортировка сообщений по дате
    all_messages.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'), reverse=True)


    with open(result_file, 'w', encoding='utf-8') as outfile:
        json.dump(all_messages, outfile, ensure_ascii=False)

    with open(offset_file, 'w') as file:
        file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


async def main():
    channel = '@zakazyfreelance'
    keywords = ['python', 'дизайн']
    offset_file = f'offset_{channel}.txt'
    offset_date = datetime.now() - timedelta(days=365)

    try:
        with open(offset_file, 'r') as file:
            offset_data = file.read().strip()

            if offset_data:  # Проверка, что строка не пустая
                offset_date = datetime.strptime(offset_data, '%Y-%m-%d %H:%M:%S')

    except FileNotFoundError:
        pass

    await search_messages(channel, keywords, offset_date)
    await client.disconnect()

if __name__ == '__main__':
    print('Бот запущен!')
    client.start()
    with client:
        client.loop.run_until_complete(main())
