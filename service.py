from pytz import UTC
import json
from datetime import datetime


async def search_messages(channel, keywords, offset_date, client):
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
                # print(data)
                all_messages.append(data)
    # Сортировка сообщений по дате
    all_messages.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'), reverse=True)

    with open(result_file, 'w', encoding='utf-8') as outfile:
        json.dump(all_messages, outfile, ensure_ascii=False)

    with open(offset_file, 'w') as file:
        file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
