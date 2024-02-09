import os

import telebot
from telebot import types
from telebot.types import InlineKeyboardButton
from telegram_bot_pagination import InlineKeyboardPaginator
from dotenv import load_dotenv

from channels import get_channels
from datas import stop_words
from services import writing_txt

load_dotenv('.env')  # загружаем данные из виртуального окружения

bot_token = os.getenv('TELEGRAM_ACCESS_TOKEN')  # получаем токен бота

bot = telebot.TeleBot(bot_token)  # создаем бота

character_pages = ['биржа', 'фриланс', 'заказ', 'сайт', 'реклама', 'удаленно', 'сделать']

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


@bot.message_handler(commands=['start', 'search'])
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

    # if message.text == '/info':
    #     # отправляем в бот приветствие и запускам клавиатуру
    #     bot.send_message(message.chat.id, 'Твой ник: @{0.username}'.format(message.from_user))

    if message.text == '/search':

        chat_id = message.chat.id  # получаем id чата

        bot.send_message(chat_id, 'Ожидайте, идет поиск...')

        # запускается поиск Telegram каналов
        new_channels = get_channels(chat_id)

        bot.send_message(chat_id, f'Найдено {new_channels} новых каналов')


@bot.message_handler(commands=['info'])
def get_messages_menu(message):
    if message.text == '/info':
        get_messages(message)


@bot.message_handler(func=lambda message: True)
def get_messages(message):
    send_message_page(message)


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == 'message')
def messages_page_callback(call):
    page = int(call.data.split('#')[1])
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    send_message_page(call.message, page)


def send_message_page(message, page=1):

    messages_list = stop_words

    paginator = InlineKeyboardPaginator(
        len(messages_list),
        current_page=page,
        data_pattern='message#{page}'
    )

    # paginator.add_before(
    #     InlineKeyboardButton('Like', callback_data='like#{}'.format(page)),
    #     InlineKeyboardButton('Dislike', callback_data='dislike#{}'.format(page))
    # )
    # paginator.add_after(InlineKeyboardButton('Go back', callback_data='back'))

    bot.send_message(
        message.chat.id,
        messages_list[page-1],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )


@bot.message_handler(content_types=['document'])
def receive_document_from_bot(message):
    """ Сохранение файла с ключевыми словами в формате txt, который передал пользователь """

    chat_id = message.chat.id  # получаем id чата

    # получаем информацию о файле, переданном пользователем
    file_info = bot.get_file(message.document.file_id)

    # скачиваем файл
    downloaded_file = bot.download_file(file_info.file_path)

    if message.caption == '1':  # проверяем описание файла

        # задаем путь к файлу с данными
        file_name = os.path.abspath(f'./data_dir/searching_words_channels_chat_id_{chat_id}.txt')

        # сохраняем файл с ключевыми словами
        writing_txt(file_name, downloaded_file)

        # выводим сообщение, что файл сохранен
        bot.reply_to(message, "Файл с ключевыми словами для поиска каналов сохранен")

    if message.caption == '2':  # проверяем описание файла

        # задаем путь к файлу с данными
        file_name = os.path.abspath(f'./data_dir/searching_words_messages_chat_id_{chat_id}.txt')

        # сохраняем файл с ключевыми словами
        writing_txt(file_name, downloaded_file)

        # выводим сообщение, что файл сохранен
        bot.reply_to(message, "Файл с ключевыми словами для поиска сообщений сохранен")

    if message.caption not in ['1', '2']:
        bot.send_message(message.chat.id, 'Файл не получен, вероятно вы где-то ошиблись')


bot.polling(non_stop=True)  # команда, чтобы бот не отключался
