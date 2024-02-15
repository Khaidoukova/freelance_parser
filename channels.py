import asyncio
import sys
import time
import nest_asyncio

from telethon.sync import TelegramClient
from telethon import functions
from dotenv import load_dotenv
import os

from datas import stop_words
from services import writing_json, reading_json, get_key_phrase, get_days_difference, reading_txt

load_dotenv('.env')  # загружаем данные из виртуального окружения

api_id = os.getenv('TELEGRAM_API_ID')  # получаем api_id, полученный у Telegram
api_hash = os.getenv('TELEGRAM_API_HASH')  # получаем api_hash, полученный у Telegram
username = os.getenv('TELEGRAM_USERNAME')  # получаем имя пользователя для задания имени файла сессии

# Создаем клиент Telegram
client = TelegramClient(username, api_id, api_hash)

nest_asyncio.apply()

# def main(chat_id):
#     try:
#         loop = asyncio.get_event_loop()
#         try:
#             tasks = asyncio.all_tasks(loop)
#             for task in tasks:
#                 task.cancel()
#         except RuntimeError as err:
#             sys.exit(1)
#     except RuntimeError:
#         loop = None
#
#     if loop is None:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#
#     loop = asyncio.get_event_loop()  # получаем текущий цикл событий


def get_channels(chat_id):
    """
    Функция поиска каналов
    :param chat_id: id чата бота с пользователем
    :return:
    """

    # получаем путь к файлу, в котором хранятся каналы
    file_channels_json = os.path.abspath(f'./data_dir/channels_chat_id_{chat_id}.json')

    # получаем список каналов из файла хранения
    # если файла еще не существует, будет создан пустой список
    channels_list = reading_json(file_channels_json)
    len_channels_list_start = len(channels_list)  # определяем начальное количество каналов

    try:
        loop = asyncio.get_event_loop()
        try:
            tasks = asyncio.all_tasks(loop)
            for task in tasks:
                task.cancel()
        except RuntimeError as err:
            sys.exit(1)
    except RuntimeError:
        loop = None

    if loop is None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop = asyncio.get_event_loop()  # получаем текущий цикл событий

    # loop = asyncio.new_event_loop()  # создаем новый цикл событий
    # asyncio.set_event_loop(loop)  # устанавливаем цикл событий

    loop.run_until_complete(get_channels_by_keyword(chat_id, channels_list))  # запускаем цикл событий
    # get_channels_by_keyword(chat_id, channels_list)  # запускаем цикл событий

    channels_list = reading_json(file_channels_json)  # получаем список каналов из файла хранения
    len_channels_list_end = len(channels_list)  # определяем конечное количество каналов

    len_difference = len_channels_list_end - len_channels_list_start  # определяем разницу в количестве каналов

    print(f"Добавлено {len_difference} новых каналов")
    print(f"Всего каналов в файле: {len_channels_list_end}")

    # loop.stop()
    # loop.close()

    time.sleep(10)

    return len_difference


async def get_channels_by_keyword(chat_id, channels_list):
    """
    Функция поиска каналов по ключевым словам
    :param channels_list: список каналов
    :param chat_id: id чата бота с пользователем
    :return:
    """

    await client.start()  # запускаем сессию клиента Telegram
    # await client.connect()

    # получаем путь к файлу с ключевыми словами
    file_channels_keywords = os.path.abspath(f'./data_dir/searching_words_channels_chat_id_{chat_id}.txt')

    # получаем путь к файлу, в котором хранятся каналы
    file_channels_json = os.path.abspath(f'./data_dir/channels_chat_id_{chat_id}.json')

    key_words = reading_txt(file_channels_keywords)  # получаем список ключевых слов

    if len(key_words) > 0:  # если список слов существует, делаем поиск новых каналов

        iter_number = len(key_words)  # получаем количество циклов проверки каналов

        for word in key_words:

            iter_number -= 1  # уменьшаем счетчик циклов

            # key_phrase = get_key_phrase(key_words)  # получаем ключевую фразу
            print(f"Ключевое слово: {word}")

            # Ищем каналы по ключевому слову
            result = await client(functions.contacts.SearchRequest(
                q=word,
                limit=10  # Можно увеличить или уменьшить лимит, однако Telegram не выдает больше 10 вариантов
            ))

            # print(result.stringify())
            chat_list = result.chats  # получаем список каналов из ответа Telegram
            print(f"Найдено каналов: {len(chat_list)}")

            # получаем список каналов из файла хранения
            # если файла еще не существует, будет создан пустой список
            channels_new = []  # создаем список для новых каналов

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

                for stop_word in stop_words:  # проверяем наличие в названии канала стоп-слов
                    if stop_word.lower() in chat.title.lower().split():  # если стоп-слово есть в названии канала
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
                                channels_new.append(channel_dict)

            # print(f'Добавлено {len(channels_new)}')
            channels_list.extend(channels_new)
            # print(f'Всего {len(channels_list)}')

            print(f'----- ожидайте ----- {iter_number}')
            time.sleep(20)

        writing_json(file_channels_json, channels_list)  # сохраняем список каналов в файл в формате json

    else:
        print('Список ключевых слов отсутствует')

    await asyncio.sleep(2)

    await client.disconnect()
    # client.disconnect()

# get_channels(876689099)
