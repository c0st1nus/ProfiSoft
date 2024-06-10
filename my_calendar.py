import telebot
from telebot import types
from datetime import datetime
import calendar

API_TOKEN = '7474314334:AAFR5qrmffYrze7Uru8zEEEzCpVueWeG7QE'
bot = telebot.TeleBot(API_TOKEN)

# Стартовое сообщение
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    btn_today = types.KeyboardButton('Today')
    btn_select_date = types.KeyboardButton('Select Date')
    markup.add(btn_today, btn_select_date)
    bot.send_message(message.chat.id, "Welcome! Choose an option:", reply_markup=markup)


# Обработка команды Today
@bot.message_handler(func=lambda message: message.text == 'Today')
def send_today(message):
    today = datetime.now().strftime('%Y-%m-%d')
    bot.send_message(message.chat.id, f'Today is {today}')


# Обработка команды Select Date
@bot.message_handler(func=lambda message: message.text == 'Select Date')
def select_date(message):
    markup = generate_calendar()
    bot.send_message(message.chat.id, "Select a date:", reply_markup=markup)


# Генерация календаря
def generate_calendar(year=None, month=None):
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month

    markup = types.InlineKeyboardMarkup()
    # Заголовок с месяцем и годом
    row = [types.InlineKeyboardButton(f'{year}-{month}', callback_data='ignore')]
    markup.row(*row)

    # Названия дней недели
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    row = [types.InlineKeyboardButton(day, callback_data='ignore') for day in days_of_week]
    markup.row(*row)

    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(' ', callback_data='ignore'))
            else:
                row.append(types.InlineKeyboardButton(str(day), callback_data=f'day-{year}-{month}-{day}'))
        markup.row(*row)

    # Кнопки навигации
    row = [
        types.InlineKeyboardButton('<', callback_data=f'prev-{year}-{month}'),
        types.InlineKeyboardButton('>', callback_data=f'next-{year}-{month}')
    ]
    markup.row(*row)

    return markup


# Обработка коллбеков из календаря
@bot.callback_query_handler(func=lambda call: call.data.startswith('day-'))
def callback_select_day(call):
    day = call.data.split('-')[3]
    bot.send_message(call.message.chat.id, f'You selected {day}')


@bot.callback_query_handler(func=lambda call: call.data.startswith('prev-'))
def callback_prev_month(call):
    year, month = map(int, call.data.split('-')[1:3])
    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    markup = generate_calendar(year, month)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('next-'))
def callback_next_month(call):
    year, month = map(int, call.data.split('-')[1:3])
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    markup = generate_calendar(year, month)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


# Игнорирование ненужных callback data
@bot.callback_query_handler(func=lambda call: call.data == 'ignore')
def callback_ignore(call):
    pass

if __name__ == '__main__':
    bot.polling(non_stop=True)
