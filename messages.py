import asyncio
from telethon.sync import TelegramClient
import telethon

from pytz import UTC
from datetime import datetime, timedelta
import time

from dotenv import load_dotenv
import os

from services import writing_json, reading_json, reading_txt

load_dotenv('.env')  # загружаем данные из виртуального окружения

api_id = os.getenv('TELEGRAM_API_ID')  # получаем api_id, полученный у Telegram
api_hash = os.getenv('TELEGRAM_API_HASH')  # получаем api_hash, полученный у Telegram
username = os.getenv('TELEGRAM_USERNAME')  # получаем имя пользователя для задания имени файла сессии


# Создаем клиент Telegram
client = TelegramClient(username, api_id, api_hash)


def get_messages(chat_id):
    """
    Поиск сообщений в каналах и запись их в файл
    :param chat_id: id чата пользователя с ботом
    :return:
    """

    # задаем имя файла, в котором будут храниться сообщения для пользователя
    result_file = f'./data_dir/result_messages_chat_id_{chat_id}.json'

    # задаем имя файла, в котором будет храниться дата последней проверки сообщений канала
    offset_file = f'./data_dir/offset_messages_chat_id_{chat_id}.json'

    # получаем путь к файлу, в котором хранятся каналы
    file_channels_json = os.path.abspath(f'./data_dir/channels_chat_id_{chat_id}.json')
    # получаем список каналов из файла хранения
    channels_list = reading_json(file_channels_json)
    # получаем список id каналов
    channels = [channel['id'] for channel in channels_list]

    # задаем путь к файлу, в котором хранятся ключевые слова для поиска сообщений
    file_keywords_txt = os.path.abspath(f'./data_dir/searching_words_messages_chat_id_{chat_id}.txt')
    # получаем список ключевых слов
    keywords = reading_txt(file_keywords_txt)

    messages_list = []  # задаем список для сообщений

    # пытаемся получить текущий цикл событий, если не существует запускаем новый
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

    # loop = asyncio.new_event_loop()  # создаем новый цикл событий
    # asyncio.set_event_loop(loop)  # устанавливаем цикл событий
    # loop = asyncio.get_event_loop()  # получаем текущий цикл событий

    iter_number = len(channels)  # получаем количество циклов проверки каналов

    # перебираем каналы
    for channel in channels:

        iter_number -= 1  # уменьшаем количество проверок

        # задаем временной промежуток, за который производится проверка сообщений
        offset_date = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now() - timedelta(days=1))

        channels_list = reading_json(offset_file)  # получаем список каналов из файла хранения

        # проверяем есть ли каналы в файле
        if len(channels_list) == 0:
            new_channel = {str(channel): offset_date}  # формируем новый словарь для нового канала
            channels_list.append(new_channel)  # добавляем в список

        # если каналы существуют, получаем дату последней проверки канала
        else:
            try:
                offset_date = channels_list[0][str(channel)]
            # если канала еще не существует, добавляем его в словарь
            except KeyError:
                channels_list[0][str(channel)] = offset_date

        # запускаем цикл событий для получения сообщений в канале
        messages_in_channel = loop.run_until_complete(search_messages(channel,
                                                                      keywords,
                                                                      offset_date,
                                                                      offset_file,
                                                                      channels_list
                                                                      ))

        # добавляем сообщения из канала в общий список
        messages_list.extend(messages_in_channel)

        if iter_number > 0:
            print(f'----- ожидайте ----- {iter_number}')
            time.sleep(20)

    writing_json(result_file, messages_list)  # сохраняем список сообщений в файл в формате json
    print('Поиск закончен')

    time.sleep(2)

    return len(messages_list)


async def search_messages(channel, keywords, offset_date, offset_file, channels_list):
    """
    Поиск сообщений в канале по ключевым словам
    :param channels_list: список каналов
    :param offset_file: файл с датой последней проверки канала
    :param channel: id канала
    :param keywords: ключевые слова
    :param offset_date: дата последней проверки
    :return: список сообщений
    """

    try:
        await client.start()  # запускаем сессию клиента Telegram
    except RuntimeError:
        pass

    all_messages = []  # задаем список для сообщений

    try:
        # Получение объекта канала
        entity = await client.get_entity(channel)

        # устанавливаем дату
        offset_date_naive = datetime.strptime(offset_date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=UTC)

        # проходим циклом по ключевым словам
        for word in keywords:

            # ищем ключевое слово в сообщениях
            async for message in client.iter_messages(entity, search=word):
                if message.date <= offset_date_naive:
                    break

                # если ключевое слово есть в сообщении, формируем словарь
                if word in message.message:
                    data = {
                        'message': message.text,
                        'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
                        'user_id': message.from_id.user_id if getattr(message.from_id, 'user_id', None) else None
                    }

                    all_messages.append(data)  # добавляем сообщение в список
    except telethon.errors.rpcerrorlist.ChannelPrivateError:
        pass

    # Сортировка сообщений по дате
    all_messages.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'), reverse=True)

    # записываем дату проверки
    channels_list[0][str(channel)] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())

    writing_json(offset_file, channels_list)  # сохраняем список каналов в файл в формате json

    await client.disconnect()

    return all_messages

# get_messages(876689099)
