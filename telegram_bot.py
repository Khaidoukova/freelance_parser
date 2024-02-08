import os

import telebot
from telebot import types
from dotenv import load_dotenv

from channels import get_channels

from services import writing_txt

load_dotenv('.env')  # загружаем данные из виртуального окружения

bot_token = os.getenv('TELEGRAM_ACCESS_TOKEN')  # получаем токен бота

bot = telebot.TeleBot(bot_token)  # создаем бота


# @bot.message_handler(commands=['start'])
# def start_bot(massage):
#
#
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создаем клавиатуру бота
#     button_1 = types.KeyboardButton('Старт')  # создаем кнопку
#     button_2 = types.KeyboardButton('Инфо')  # создаем кнопку
#     markup.add(button_1, button_2)  # добавляем кнопки в клавиатуру бота
#
#     # отправляем в бот приветствие и запускам клавиатуру
#     bot.send_message(massage.chat.id, 'Привет, {0.first_name}!'.format(massage.from_user), reply_markup=markup)


# @bot.message_handler(content_types=['text'])
# def bot_massage(massage):
#     """ Функция работы меню бота """
#
#     # если в меню бота нажать кнопку "Инфо"
#     if massage.text == 'info':
#         # отправляется сообщение с ником пользователя
#         bot.send_message(massage.chat.id, 'Твой ник: @{0.username}'.format(massage.from_user))
#
#     # если в меню бота нажать кнопку "Старт"
#     elif massage.text == 'search':
#         bot.send_message(massage.chat.id, 'Ожидайте, идет поиск...')
#
#         # запускается поиск Telegram каналов
#         new_channels = get_channels()
#
#         bot.send_message(massage.chat.id, f'Найдено {new_channels} новых каналов')
#         # bot.send_message(massage.chat.id, 'Привет, {0.first_name}!'.format(massage.from_user))


# --------------- эта часть кода запускается один раз для формирования меню ----------------

# @bot.message_handler()
# def send_welcome(message: telebot.types.Message):
#     """ Функция формирования меню бота """
#
#     bot.reply_to(message, message.text)
#
#
# bot.set_my_commands([
#     telebot.types.BotCommand("start", "Перезапуск бота"),
#     telebot.types.BotCommand("info", "Инфо"),
#     telebot.types.BotCommand("search", "Запуск поиска каналов")
# ])

# ----------------------------------- конец блока -------------------------------------------

@bot.message_handler(commands=['start', 'info', 'search'])
def start_bot(message):

    if message.text == '/start':
        # отправляем в бот приветствие и запускам клавиатуру
        bot.send_message(message.chat.id, 'Привет, {0.first_name}!'.format(message.from_user))
        bot.send_message(message.chat.id, 'Чтобы загрузить ключевые слова для поиска каналов, '
                                          'отправьте боту сообщение с текстом "1" и '
                                          'прикрепите файл в формате txt со списком ключевых слов.')
        bot.send_message(message.chat.id, 'Чтобы загрузить ключевые слова для поиска сообщений, '
                                          'отправьте боту сообщение с текстом "2" и '
                                          'прикрепите файл в формате txt со списком ключевых слов.')

    if message.text == '/info':
        # отправляем в бот приветствие и запускам клавиатуру
        bot.send_message(message.chat.id, 'Твой ник: @{0.username}'.format(message.from_user))

    if message.text == '/search':

        bot.send_message(message.chat.id, 'Ожидайте, идет поиск...')

        # запускается поиск Telegram каналов
        new_channels = get_channels()

        bot.send_message(message.chat.id, f'Найдено {new_channels} новых каналов')


@bot.message_handler(content_types=['document'])
def receive_document_from_bot(message):
    """ Сохранение файла с ключевыми словами в формате txt, который передал пользователь """

    chat_id = message.chat.id

    # получаем информацию о файле, переданном пользователем
    file_info = bot.get_file(message.document.file_id)

    # скачиваем файл
    downloaded_file = bot.download_file(file_info.file_path)

    if message.caption == '1':  # проверяем описание файла

        # задаем путь к файлу с данными
        file_name = os.path.abspath(f'./searching_words_channels_chat_id_{chat_id}.txt')

        # сохраняем файл с ключевыми словами
        writing_txt(file_name, downloaded_file)

        # выводим сообщение, что файл сохранен
        bot.reply_to(message, "Файл с ключевыми словами для поиска каналов сохранен")

    if message.caption == '2':  # проверяем описание файла

        # задаем путь к файлу с данными
        file_name = os.path.abspath(f'./searching_words_messages_chat_id_{chat_id}.txt')

        # сохраняем файл с ключевыми словами
        writing_txt(file_name, downloaded_file)

        # выводим сообщение, что файл сохранен
        bot.reply_to(message, "Файл с ключевыми словами для поиска сообщений сохранен")

    else:
        bot.send_message(message.chat.id, 'Файл не получен, вероятно вы где-то ошиблись')


bot.polling(non_stop=True)  # команда, чтобы бот не отключался
