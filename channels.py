import asyncio
import time

from telethon.sync import TelegramClient
from telethon import functions
from dotenv import load_dotenv
import os

from datas import key_words, stop_words, file_data_json
from services import writing_json, reading_json, get_key_phrase, get_days_difference

load_dotenv('.env')  # загружаем данные из виртуального окружения

api_id = os.getenv('TELEGRAM_API_ID')  # получаем api_id, полученный у Telegram
api_hash = os.getenv('TELEGRAM_API_HASH')  # получаем api_hash, полученный у Telegram
username = os.getenv('TELEGRAM_USERNAME')  # получаем имя пользователя для задания имени файла сессии
key_word = 'gurienomika'

# Создаем клиент Telegram
client = TelegramClient(username, api_id, api_hash)


def get_channels():
    """ Функция поиска каналов """

    channels_list = reading_json(file_data_json)  # получаем список каналов из файла хранения
    len_channels_list_start = len(channels_list)  # определяем начальное количество каналов

    # loop = asyncio.get_event_loop()  # получаем текущий цикл событий
    loop = asyncio.new_event_loop()  # создаем новый цикл событий
    asyncio.set_event_loop(loop)  # устанавливаем цикл событий

    # запускаем цикл поиска каналов, количество итераций можно изменить
    for i in range(2):
        loop.run_until_complete(get_channels_by_keyword())  # запускаем цикл событий
        print('----- ожидайте -----')
        time.sleep(20)

    channels_list = reading_json(file_data_json)  # получаем список каналов из файла хранения
    len_channels_list_end = len(channels_list)  # определяем конечное количество каналов

    len_difference = len_channels_list_end - len_channels_list_start  # определяем разницу в количестве каналов

    print(f"Добавлено {len_difference} новых каналов")
    print(f"Всего каналов в файле: {len_channels_list_end}")

    return len_difference


async def get_channels_by_keyword():
    """ Функция поиска каналов по ключевым словам """

    await client.start()  # запускаем сессию клиента Telegram

    key_phrase = get_key_phrase(key_words)  # получаем ключевую фразу
    print(f"Ключевая фраза: {key_phrase}")

    # Ищем каналы по ключевой фразе
    result = await client(functions.contacts.SearchRequest(
        q=key_phrase,
        limit=10  # Можно увеличить или уменьшить лимит, однако Telegram не выдает больше 10 вариантов
    ))

    # print(result.stringify())
    chat_list = result.chats  # получаем список каналов из ответа Telegram
    print(f"Найдено каналов: {len(chat_list)}")

    # получаем список каналов из файла хранения
    # если файла еще не существует, будет создан пустой список
    channels_list = reading_json(file_data_json)

    # перебираем список спарсенных каналов
    for chat in chat_list:

        channel_dict = {}  # создаем словарь, в который будем складывать данные о канале
        if chat.username:
            chat_link = f"https://t.me/{chat.username}"  # формируем ссылку на канал, если она доступна
        else:
            chat_link = None
        print(f"ID канала: {chat.id}, Название: {chat.title}, Ссылка на канал: {chat_link}")
        channel_dict['id'] = chat.id  # id канала
        channel_dict['title'] = chat.title  # название канала
        channel_dict['link'] = chat_link  # ссылка на канал

        flag = True  # устанавливаем метку добавления канала в новый список

        for word in stop_words:  # проверяем наличие в названии канала стоп-слов
            if word.lower() in chat.title.lower().split():  # если стоп-слово есть в названии канала
                flag = False  # устанавливаем запрет на добавление канала

        if flag:  # если метка разрешает добавление канала

            # проверяем последнее сообщение в канале
            async for message in client.iter_messages(chat.title, limit=1):
                # print(message.date)

                # определяем давность последнего сообщения в днях от текущей даты
                days_difference = get_days_difference(message.date)

                # проверяем давность сообщения (чтобы сообщение было опубликовано не позднее 7 дней)
                if days_difference <= 7:

                    if channel_dict not in channels_list:  # если канала нет в списке, добавляем в список
                        channels_list.append(channel_dict)

    writing_json(file_data_json, channels_list)  # сохраняем список каналов в файл в формате json

    await client.disconnect()
