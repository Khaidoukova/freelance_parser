import os

# список стоп-слов, по которым будут исключаться каналы
stop_words = ['oriflame', 'спецтехники', 'отзывов', 'клипы', 'wildberries', 'исламский',
              'ВЕЙПШОП', 'Шкафы', 'Zara', 'Ozon']

# список ключевых слов из которых будет составлена ключевая фраза
key_words = ['биржа', 'фриланс', 'заказ', 'сайт', 'реклама', 'удаленно', 'сделать']

# файл для хранения списка вакансий
file_data_json = os.path.abspath('./channels.json')