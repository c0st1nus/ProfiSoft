import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot("7047928321:AAEnZNpdK3HUWtIh3RUS-xRDfdAJqe34DMA")
HR = 1239398217
hr_chat = None
vac = []


def generate_vacancy_buttons(vacancies):
    keyboard = types.InlineKeyboardMarkup()
    for i in vacancies:
        keyboard.add(types.InlineKeyboardButton(text=i, callback_data=i))
    return keyboard


def generate_candidate_text(i):
    text = ""
    text += f"Вакансия: {i[9]}\n"
    text += f"Имя: {i[0]}\n"
    text += f"Возраст: {i[4]}\n"
    text += f"Телефон: {i[3]}\n"
    text += f"Резюме: {i[2]}\n"
    text += f"Достижения: {i[5]}\n"
    text += "------------------------------------\n"
    return text


def get_vacancies():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(text="◀️Назад")
    button2 = types.KeyboardButton(text="Выйти в главное меню")
    button3 = types.KeyboardButton(text="Вперед▶️")
    keyboard.row(button1, button2, button3)
    button4 = types.KeyboardButton(text="Пригласить на собеседование✅")
    button5 = types.KeyboardButton(text="Отправить в резерв")
    keyboard.row(button4, button5)
    return keyboard


def main_markup():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton(text="Добавить вакансию")
    button2 = types.KeyboardButton(text="Удалить вакансию")
    button3 = types.KeyboardButton(text="Посмотреть список кандидатов")
    keyboard.row(button1, button2)
    keyboard.row(button3)
    return keyboard


def keyboard_from_list(lst):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in lst:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    keyboard.add(types.KeyboardButton(text="Назад"))
    return keyboard


@bot.message_handler(commands=['start'])
def main(message):
    vac.clear()
    conn = sqlite3.connect("SqlLite.db")
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM `vacancies`").fetchall()
    for i in res:
        vac.append(i[0])
    if message.from_user.id != HR:
        print(message.chat.id)
        bot.send_message(message.chat.id,
                         "Добрый день, вас приветствует чат-бот компании Profi soft! Мы занимаемся автоматизацией "
                         "бизнеса и наша эволюционная цель  звучит так - ЧТОБЫ ЦИФРОВАЯ ТРАНСФОРМАЦИЯ СТАЛА ДВИЖУЩЕЙ "
                         "СИЛОЙ РЕАЛЬНОГО СЕКТОРА ЭКОНОМИКИ, ПРЕДОСТАВЛЯЮШИЙ ПОЛЕЗНЫЕ ДЛЯ ОБЩЕСТВА ТОВАРЫ И УСЛУГИ И "
                         "ПРИЗНАНИЕ ЕГО ВЕДУЩЕЙ РОЛИ В ЭКОНОМИЧЕСКОМ РАЗВИТИИ.")
        bot.send_message(message.chat.id, f"Сейчас у нас открыты следующие вакансии:", reply_markup=generate_vacancy_buttons(vac))
    else:
        bot.send_message(message.chat.id, "HR здравствуйте! Чем могу помочь?", reply_markup=main_markup())
        bot.register_next_step_handler(message, hr)


@bot.callback_query_handler(func=lambda call: True)
def candidate_vacancy(callback):
    conn = sqlite3.connect("SqlLite.db")
    cur = conn.cursor()
    cur.execute(f"INSERT into `candidates` (Vacancy, ChatID) VALUES ('{callback.data}', {callback.from_user.id});")
    conn.commit()
    id = cur.execute("SELECT last_insert_rowid();").fetchone()[0]
    conn.close()
    bot.send_message(callback.message.chat.id,
                     "Прикрепи свое резюме, так мы познакомимся с тобой поближе, и ответь на вопрос - что является "
                     "твоим продуктом должности?")
    bot.register_next_step_handler(callback.message, resume, id)


def resume(message, id):
    conn = sqlite3.connect("SqlLite.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE `candidates` SET `Resume` = '{message.text}' WHERE `ID` = '{id}';")
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Отлчино! Перед приглашением на интервью ответьте пожалуйста на пару вопросов")
    bot.send_message(message.chat.id, "Укажите ваш контактный номер телефона (10 цифр без кода страны)")
    bot.register_next_step_handler(message, phone, id)


def phone(message, id: int):
    conn = sqlite3.connect("SqlLite.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE `candidates` SET `PhoneNumber` = '{message.text}' WHERE `ID` = '{id}';")
    conn.commit()
    bot.send_message(message.chat.id, "Укажите ваше полное ФИО")
    bot.register_next_step_handler(message, name, id)


def name(message, id: int):
    conn = sqlite3.connect("SqlLite.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE `candidates` SET `Name` = '{message.text}' WHERE `ID` = '{id}';")
    conn.commit()
    bot.send_message(message.chat.id, "Сколько вам полных лет?")
    bot.register_next_step_handler(message, age, id)


def age(message, id: int):
    conn = sqlite3.connect("SqlLite.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE `candidates` SET `Age` = '{message.text}' WHERE `ID` = '{id}';")
    conn.commit()
    bot.send_message(message.chat.id, "Опишите ваши достижения (профессиональные или личные)?")
    bot.register_next_step_handler(message, achievments, id)


def achievments(message, id: int):
    conn = sqlite3.connect("SqlLite.db")
    cur = conn.cursor()
    cur.execute(
        f"UPDATE `candidates` SET (`Achievements`, `ChatID`) = ('{message.text}', {message.from_user.id}) WHERE `ID` = '{id}';")
    conn.commit()
    bot.send_message(message.chat.id, "Отлично, ожидайте пока наш HR откликнется на ваше резюме")
    bot.send_message(1239398217, "Поступило новое резюме! Проверьте список кандидатов")
    main(message)


def hr(message):
    if message.text == "Добавить вакансию":
        bot.send_message(message.chat.id, "Введите название вакансии", reply_markup=keyboard_from_list([]))
        bot.register_next_step_handler(message, add_vacancy)
    elif message.text == "Удалить вакансию":
        bot.send_message(message.chat.id, "Выберете вакансию", reply_markup=keyboard_from_list(vac))
        bot.register_next_step_handler(message, delete_vacancy)
    elif message.text == "Посмотреть список кандидатов":
        bot.send_message(message.chat.id, "Выберите вакансию", reply_markup=keyboard_from_list(vac))
        bot.register_next_step_handler(message, candidates_list)
    else:
        bot.send_message(message.chat.id, "Выберите один из вариантов")
        bot.register_next_step_handler(message, hr)


def candidates_list(message):
    conn = sqlite3.connect("SqlLite.db")
    cur = conn.cursor()
    data = cur.execute(
        f"SELECT * FROM `candidates` WHERE `Accepted` IS NULL AND `Name` IS NOT NULL AND `Resume` IS NOT NULL AND `PhoneNumber` IS NOT NULL AND `Age` IS NOT NULL AND `Achievements` IS NOT NULL AND `vacancy` IS '{message.text}';").fetchall()
    if len(data) == 0:
        bot.send_message(message.chat.id, "Кандидатов нет", reply_markup=main_markup())
        hr(message)
    else:
        bot.send_message(message.chat.id, generate_candidate_text(data[0]), reply_markup=get_vacancies())
        bot.register_next_step_handler(message, candidates, 0, data)


def candidates(message, i: int, data: list):
    try:
        if message.text == "Вперед▶️":
            i += 1
            if i >= len(data):
                i = 0
            bot.send_message(message.chat.id, generate_candidate_text(data[i]), reply_markup=get_vacancies())
            bot.register_next_step_handler(message, candidates, i, data)
        elif message.text == "◀️Назад":
            i -= 1
            if i < 0:
                i = len(data) - 1
            bot.send_message(message.chat.id, generate_candidate_text(data[i]), reply_markup=get_vacancies())
            bot.register_next_step_handler(message, candidates, i, data)
        elif message.text == "✅":
            conn = sqlite3.connect("SqlLite.db")
            cur = conn.cursor()
            cur.execute(f"UPDATE `candidates` SET `Accepted` = '1' WHERE `ID` = '{data[i][6]}';")
            conn.commit()
            data.remove(data[i])
            bot.send_message(message.chat.id, "На какое время вы хотите назначить собеседование?")
            bot.register_next_step_handler(message, interview, data)
        elif message.text == "❌":
            conn = sqlite3.connect("SqlLite.db")
            cur = conn.cursor()
            cur.execute(f"UPDATE `candidates` SET `Accepted` = '0' WHERE `ID` = '{data[i][6]}';")
            conn.commit()
            data.remove(data[i])
            bot.send_message(message.chat.id, "Кандидат отклонен")
            bot.send_message(data[i][7], "Ваше резюме отклонено")
            bot.send_message(message.chat.id, generate_candidate_text(data[i]), reply_markup=get_vacancies())
            bot.register_next_step_handler(message, candidates, 0, data)
        elif message.text == "Выйти в главное меню":
            main(message)
    except IndexError:
        bot.send_message(message.chat.id, "Все кандидаты рассмотрены")
        main(message)

def interview(message, data):
    conn = sqlite3.connect("SqlLite.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE `candidates` SET `Interview` = '{message.text}' WHERE `ID` = '{data[0][6]}';")
    conn.commit()
    bot.send_message(message.chat.id, "Напишите комментарий к собеседованию либо нажмите на кнопку ниже", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text="Оставить без коментария")))
    bot.register_next_step_handler(message, comment, data)

def comment(message, data):
    bot.send_message(data[0][7], f"Поздравляем! Вас пригласили на собеседование {data[0][9]} на {data[0][10]}")


def delete_vacancy(message):
    if message.text != "Назад":
        conn = sqlite3.connect("SqlLite.db")
        cur = conn.cursor()
        cur.execute(f"DELETE FROM `vacancies` WHERE `vacancy` = '{message.text}'")
        conn.commit()
        bot.send_message(message.chat.id, f"Вакансия {message.text} удалена")
        main(message)
    else:
        main(message)


def add_vacancy(message):
    if message.text != "Назад":
        conn = sqlite3.connect("SqlLite.db")
        cur = conn.cursor()
        cur.execute(f"INSERT into `vacancies` (Vacancy) VALUES ('{message.text}');")
        conn.commit()
        bot.send_message(message.chat.id, f"Вакансия {message.text} добавлена")
        main(message)
    else:
        main(message)


bot.polling(non_stop=True)
