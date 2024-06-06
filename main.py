import telebot
from telebot import types

bot = telebot.TeleBot("7047928321:AAEnZNpdK3HUWtIh3RUS-xRDfdAJqe34DMA")
HR = "1239398217"
vac = ['менеджер']

def keyboard_from_list(lst):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in lst:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    keyboard.add(types.KeyboardButton(text="Назад"))
    return keyboard

@bot.message_handler(commands=['start'])
def main(message):
    if str(message.from_user.id) != HR:
        bot.send_message(message.chat.id, "Добрый день, вас приветствует чат-бот компании Profi soft! Мы занимаемся автоматизацией бизнеса и наша эволюционная цель  звучит так - ЧТОБЫ ЦИФРОВАЯ ТРАНСФОРМАЦИЯ СТАЛА ДВИЖУЩЕЙ СИЛОЙ РЕАЛЬНОГО СЕКТОРА ЭКОНОМИКИ, ПРЕДОСТАВЛЯЮШИЙ ПОЛЕЗНЫЕ ДЛЯ ОБЩЕСТВА ТОВАРЫ И УСЛУГИ И ПРИЗНАНИЕ ЕГО ВЕДУЩЕЙ РОЛИ В ЭКОНОМИЧЕСКОМ РАЗВИТИИ.")
        vacancy = ', '.join(vac)
        bot.send_message(message.chat.id, f"Сейчас у нас открыты вакансии - {vacancy}")

    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button1 = types.KeyboardButton(text="Добавить вакансию")
        button2 = types.KeyboardButton(text="Удалить вакансию")
        button3 = types.KeyboardButton(text="Посмотреть список кандидатов")
        keyboard.row(button1, button2)
        keyboard.row(button3)
        bot.send_message(message.chat.id, "HR здравствуйте! Чем могу помочь?", reply_markup=keyboard)
        bot.register_next_step_handler(message, hr)

def hr(message):
    if message.text == "Добавить вакансию":
        bot.send_message(message.chat.id, "Введите название вакансии")

    elif message.text == "Удалить вакансию":
        bot.send_message(message.chat.id, "Выберете вакансию", reply_markup=keyboard_from_list(vac))

    elif message.text == "Посмотреть список кандидатов":
        bot.send_message(message.chat.id, "Введите название вакансии")

    else:
        bot.send_message(message.chat.id, "Выберите один из вариантов")
        bot.register_next_step_handler(message, hr)


bot.polling(non_stop=True)