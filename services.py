import json
from random import randint
import pytz
import datetime

from datas import file_data_json, stop_words


def writing_json(file_data, channels_list):
    """ Записывает данные в формате json """

    with open(file_data, 'w', encoding='utf-8') as file:
        json.dump(channels_list, file, sort_keys=False, indent=4, ensure_ascii=False)


def reading_json(file_data):
    """ Считывает данные из формата json """

    try:
        with open(file_data, 'r', encoding='utf-8') as file:
            channels = json.load(file)
        return channels
    except FileNotFoundError:
        print('Файла пока не существует, будет создан новый файл')
        channels = []
        return channels


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


def get_days_difference(date_time):
    """ Считает разницу между текущей датой и полученной датой в днях """

    desired_timezone = pytz.timezone('Europe/Moscow')  # устанавливаем часовой пояс
    date_time_now = datetime.datetime.now()  # получаем текущие дату и время

    time_now = date_time_now.astimezone(desired_timezone)  # текущее время с учетом часового пояса
    time_received = date_time.astimezone(desired_timezone)  # время полученное с учетом часового пояса

    # считаем разницу между текущей датой и полученной датой в днях
    days_difference = (time_now.date() - time_received.date()).days

    return days_difference


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


cleaning_data(file_data_json, stop_words)
