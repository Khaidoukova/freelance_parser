import os

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_bot_pagination import InlineKeyboardPaginator
from dotenv import load_dotenv

from channels import get_channels
from messages import get_messages
from services import writing_txt, reading_json, writing_log_txt, writing_json

load_dotenv('.env')  # загружаем данные из виртуального окружения

bot_token = os.getenv('TELEGRAM_ACCESS_TOKEN')  # получаем токен бота

bot = telebot.TeleBot(bot_token)  # создаем бота

# dimarodeo (id = 876689099), Ali_Trofimova (id = 986959236)
# khaidoukova (id = 559091554), GaliulinYar (id = 476890564)

# id пользователей, которым разрешен доступ к сервису
id_list = [876689099, 986959236, 559091554, 476890564]

# --------------- эта часть кода запускается один раз для формирования меню ----------------
# -----------------после запуска кода остановить бот, закомментировать код -----------------


# @bot.message_handler()
# def send_welcome(message: telebot.types.Message):
#     """ Функция формирования меню бота """
#
#     bot.reply_to(message, message.text)
#
#
# bot.set_my_commands([
#     telebot.types.BotCommand("start", "Запуск бота"),
#     telebot.types.BotCommand("display", "Вывести сообщения за последний день"),
#     telebot.types.BotCommand("messages", "Поиск новых сообщений"),
#     telebot.types.BotCommand("channels", "Поиск новых каналов"),
#     telebot.types.BotCommand("edit_ch", "Редактирование списка каналов")
# ])

# ----------------------------------- конец блока -------------------------------------------


@bot.message_handler(commands=['start', 'channels', 'messages'])
def start_bot(message):

    chat_id = message.chat.id  # получаем id чата

    if chat_id in id_list:

        if message.text == '/start':

            # записываем в лог-файл информацию о событии
            writing_log_txt('Запуск бота /start', chat_id)

            # отправляем в бот приветствие и запускам клавиатуру
            bot.send_message(message.chat.id, 'Привет, {0.first_name}!'.format(message.from_user))
            bot.send_message(message.chat.id, 'Чтобы загрузить ключевые слова для поиска каналов,\n'
                                              'отправьте боту файл в формате txt со списком ключевых фраз.\n'
                                              'Каждая фраза должна быть на новой строке.\n'
                                              'В описании файла поставьте цифру "1"')
            bot.send_message(message.chat.id, 'Чтобы загрузить ключевые слова для поиска сообщений,\n'
                                              'отправьте боту файл в формате txt со списком ключевых фраз.\n'
                                              'Каждая фраза должна быть на новой строке.\n'
                                              'В описании файла поставьте цифру "2"')

        if message.text == '/channels':

            bot.send_message(chat_id, 'Начинаю поиск новых каналов\nМожет занять продолжительное время...')

            # запускается поиск Telegram каналов
            new_channels = get_channels(chat_id)

            bot.send_message(chat_id, f'Найдено {new_channels} новых каналов')

        if message.text == '/messages':

            bot.send_message(chat_id, 'Начинаю поиск новых сообщений\nМожет занять продолжительное время...')

            messages_number = get_messages(chat_id)  # запускаем поиск сообщений

            bot.send_message(chat_id, f'Найдено {messages_number} новых сообщений')

    else:
        bot.send_message(chat_id, 'К сожалению вам сервис недоступен')


@bot.message_handler(commands=['edit_ch'])
def edit_channels(message):
    """ Обработчик команды вывода списка каналов """

    chat_id = message.chat.id  # получаем id чата

    if chat_id in id_list:

        if message.text == '/edit_ch':

            # записываем в лог-файл информацию о событии
            writing_log_txt('Вывод списка каналов для редактирования /edit_ch', chat_id)

            # путь к файлу, в котором хранятся каналы
            file_channels_json = os.path.abspath(f'./data_dir/channels_chat_id_{chat_id}.json')

            channels_list = reading_json(file_channels_json)  # получаем список сообщений из файла хранения

            markup = InlineKeyboardMarkup()  # создаем клавиатуру

            # выводим кнопки с каналами
            for channel in channels_list:
                button = InlineKeyboardButton(text=channel['title'],
                                              callback_data='delete_channel ' + str(channel["id"]))
                markup.add(button)

            bot.send_message(message.chat.id, "Выберите канал для удаления:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'delete_channel')
def handle_button_click(call):
    """ Обработчик нажатия на кнопку выбора канала для удаления """

    chat_id = call.message.chat.id  # получаем id чата

    # путь к файлу, в котором хранятся каналы
    file_channels_json = os.path.abspath(f'./data_dir/channels_chat_id_{chat_id}.json')

    # путь к файлу, в котором хранятся стоп каналы
    file_stop_channels_json = os.path.abspath(f'./data_dir/stop_channels_chat_id_{chat_id}.json')

    # получаем ID канала, который надо удалить
    channel_id_to_delete = int(call.data.replace('delete_channel ', ''))

    channels_list = reading_json(file_channels_json)  # получаем список каналов из файла хранения

    stop_channels_list = reading_json(file_stop_channels_json)  # получаем список стоп каналов из файла хранения

    # перебираем каналы
    for channel in channels_list:

        if channel['id'] == channel_id_to_delete:  # находим соответствующий канал

            channels_list.remove(channel)  # удаляем канал из списка
            stop_channels_list.append(channel)  # и добавляем его в список стоп каналов

            break

    writing_json(file_channels_json, channels_list)  # сохраняем список каналов в файл

    writing_json(file_stop_channels_json, stop_channels_list)  # сохраняем список стоп каналов в файл

    bot.send_message(chat_id, "Канал перемещен в черный список\n"
                              "Если хотите продолжить редактирование списка, запустите процедуру заново")


@bot.message_handler(commands=['display'])
def display_messages(message):
    """ Обработчик команды вывода сообщений """

    if message.chat.id in id_list:

        if message.text == '/display':

            # записываем в лог-файл информацию о событии
            writing_log_txt('Вывод последних сообщений /display', message.chat.id)

            send_messages(message)  # Запускаем вывод сообщений в чат


@bot.message_handler(func=lambda message: True)
def send_messages(message):
    """ Вывод сообщений в чат """

    send_message_page(message)


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == 'message')
def messages_page_callback(call):
    """ Обработчик кнопок с пагинацией """

    page = int(call.data.split('#')[1])
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )

    send_message_page(call.message, page)  # выводим сообщения в чат


def send_message_page(message, page=1):
    """ Вывод сообщений в чат с пагинацией """

    chat_id = message.chat.id  # получаем id чата

    # получаем путь к файлу, в котором хранятся сообщения
    file_messages_json = os.path.abspath(f'./data_dir/result_messages_chat_id_{chat_id}.json')

    messages_all = reading_json(file_messages_json)  # получаем список сообщений из файла хранения

    # собираем текст сообщений в список
    messages_list = [message['message'] for message in messages_all]
    # print(len(messages_list))
    # messages_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    paginator = InlineKeyboardPaginator(
        len(messages_list),
        current_page=page,
        data_pattern='message#{page}'
    )

    # paginator.add_before(
    #     InlineKeyboardButton('Like', callback_data='like#{}'.format(page)),
    #     InlineKeyboardButton('Dislike', callback_data='dislike#{}'.format(page))
    # )
    # paginator.add_after(InlineKeyboardButton('Жми', callback_data='press'))

    try:
        bot.send_message(
            message.chat.id,
            messages_list[page-1],
            reply_markup=paginator.markup,
            parse_mode='HTML'  # использовать этот атрибут, если нужна разметка в выводимых сообщениях
            # parse_mode='Markdown'
        )

    except IndexError:
        bot.send_message(chat_id, 'Новых сообщений нет')


@bot.message_handler(content_types=['document'])
def receive_document_from_bot(message):
    """ Сохранение файла с ключевыми словами в формате txt, который передал пользователь """

    chat_id = message.chat.id  # получаем id чата

    # записываем в лог-файл информацию о событии
    writing_log_txt('Загрузка файла с ключевыми фразами', chat_id)

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
