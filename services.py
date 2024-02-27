import json

from random import randint
import pytz
import datetime

from dotenv import load_dotenv
import os
import requests

load_dotenv('.env')  # загружаем данные из виртуального окружения
bot_token = os.getenv('TELEGRAM_ACCESS_TOKEN')  # получаем токен бота


def send_message_to_bot(chat_id, message):
    """ Функция отправки сообщения в телеграм-бот
    chat_id: id чата
    message: передаваемое сообщение
    """
    send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'  # url для отправки сообщений

    params = {"chat_id": chat_id, "text": message}

    response = requests.get(send_message_url, params=params).json()

    return response


def writing_json(file_data, data_list):
    """ Записывает данные в формате json """

    with open(file_data, 'w', encoding='utf-8') as file:
        json.dump(data_list, file, sort_keys=False, indent=4, ensure_ascii=False)


def reading_json(file_data):
    """ Считывает данные из формата json """

    try:
        with open(file_data, 'r', encoding='utf-8') as file:
            data_list = json.load(file)
        return data_list
    except FileNotFoundError:
        print('Файла пока не существует, будет создан новый файл')
        data_list = []
        return data_list


def number_generator(list_len):
    """ Генератор случайного числа, исходя из списка ключевых слов """

    number = int(randint(0, list_len))

    return number


def get_key_phrase(words_list):
    """ Формирует ключевую фразу для поиска """

    words_list_len = int(len(words_list) - 1)  # определяем количество слов

    word_number_1 = number_generator(words_list_len)  # получаем случайный номер первого слова
    word_number_2 = number_generator(words_list_len)  # получаем случайный номер второго слова

    key_phrase = str(f"{words_list[word_number_1]} {words_list[word_number_2]}")

    return key_phrase


def get_time_difference(date_time):
    """ Считает разницу между текущей датой и полученной датой в днях """

    desired_timezone = pytz.timezone('Europe/Moscow')  # устанавливаем часовой пояс
    date_time_now = datetime.datetime.now()  # получаем текущие дату и время

    time_now = date_time_now.astimezone(desired_timezone)  # текущее время с учетом часового пояса
    time_received = date_time.astimezone(desired_timezone)  # время полученное с учетом часового пояса

    # считаем разницу между текущей датой и полученной датой
    # days_difference = (time_now.date() - time_received.date()).days
    time_difference = time_now.date() - time_received.date()

    return time_difference


def cleaning_data(file_data, words_list):
    """ Очистка файла с данными о каналах по списку стоп-слов """

    channels_list = reading_json(file_data)  # получаем список каналов из файла хранения
    len_channels_list_start = len(channels_list)  # определяем начальное количество каналов
    print(f"Начальное количество каналов: {len_channels_list_start}")

    channels_list_new = []  # создаем пустой список

    for channel in channels_list:  # проверяем каналы

        flag = True  # устанавливаем метку добавления канала в новый список

        for word in words_list:  # проверяем наличие в названии канала стоп-слов

            if word.lower() in channel['title'].lower().split():  # если стоп-слово есть в названии канала
                flag = False  # устанавливаем запрет на добавление канала

        if flag:  # если метка разрешает добавление канала
            if channel not in channels_list_new:  # если канала нет в новом списке
                channels_list_new.append(channel)  # добавляем канал в новый список

    len_channels_list_end = len(channels_list_new)  # определяем конечное количество каналов
    len_difference = len_channels_list_start - len_channels_list_end  # определяем количество удаленных каналов

    print(f"Удалено каналов: {len_difference}")
    print(f"Осталось каналов в файле: {len_channels_list_end}")

    writing_json(file_data, channels_list_new)  # сохраняем новый список каналов в файл в формате json


def writing_txt(file_name, downloaded_file):
    """ Записывает скачанный файл в файл с указанным именем """

    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)


def reading_txt(file_data):
    """ Считывает ключевые слова из файла txt """

    try:
        with open(file_data, 'r') as file:
            keywords = file.read().splitlines()
        return keywords
    except FileNotFoundError:
        print('Файла пока не существует, проверьте данные')
        keywords = []
        return keywords


def writing_log_txt(log_text, chat_id):
    """
    Записывает в файл лог действий пользователей
    :param log_text: действия пользователя
    :param chat_id: id чата пользователя с ботом
    """

    # задаем имя файла
    log_file = os.path.abspath(f'./data_dir/log_file.txt')

    date_time_now = datetime.datetime.now()  # получаем текущие дату и время

    # записываем данные в файл
    with open(log_file, 'a') as file:
        file.write(f'{date_time_now}|{log_text}|{chat_id}\n')


def reading_log_txt():
    """ Считывает данные лог файла """

    # задаем имя файла
    log_file = os.path.abspath(f'./data_dir/log_file.txt')

    # считываем последние 20 действий пользователей
    try:
        with open(log_file, 'r') as file:
            log_lines = file.read().splitlines()
            last_lines = log_lines[-20:]

    except FileNotFoundError:
        log_lines = []
        last_lines = []

    # проверяем размер лог файла, если записей больше 200, оставляем последние 100 записей
    if len(log_lines) > 200:
        with open(log_file, 'w') as file:
            file.write('\n'.join(log_lines[-100:]))
            file.write('\n')

    return last_lines


def checking_bot_status():
    """ Проверяет последнее использование бота пользователями перед рестартом.
     Если последние 5 минут ботом пользовались, то в случае рестарта
     пользователям будет об этом сообщено """

    # получаем последние действия пользователей
    log_list = reading_log_txt()

    if len(log_list) > 0:
        # получаем дату и время последней записи
        last_action = log_list[-1].split('|')[0]

        # преобразуем строку в формат datetime
        last_action_time = datetime.datetime.strptime(last_action, '%Y-%m-%d %H:%M:%S.%f')

        # определяем разницу по времени между последним действием пользователя текущим временем в минутах
        time_difference = (get_time_difference(last_action_time)).total_seconds() / 60

        # если с момента последних действий пользователя прошло меньше 5 минут
        if time_difference < 5:

            # получаем id пользователей, которые пользовались ботом
            users_id = set([log.split('|')[-1] for log in log_list])

            # отправляем пользователям сообщение о рестарте бота
            for user in users_id:
                send_message_to_bot(int(user),
                                    'К сожалению, по техническим причинам я перезагрузился')


# cleaning_data(file_data_json, stop_words)

checking_bot_status()
