import telebot
from telebot import types
import sqlite3
from datetime import datetime
import calendar

bot = telebot.TeleBot("7047928321:AAEnZNpdK3HUWtIh3RUS-xRDfdAJqe34DMA")
HR = 1239398217
hr_chat = None
vac = []
date = None
id = None
chat = None

try:
    def generate_vacancy_buttons(vacancies):
        keyboard = types.InlineKeyboardMarkup()
        for i in vacancies:
            keyboard.add(types.InlineKeyboardButton(text=i, callback_data=f"vac-{i}"))
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
            bot.send_message(message.chat.id,
                             "Добрый день, вас приветствует чат-бот компании Profi soft! Мы занимаемся автоматизацией "
                             "бизнеса и наша эволюционная цель  звучит так - ЧТОБЫ ЦИФРОВАЯ ТРАНСФОРМАЦИЯ СТАЛА "
                             "ДВИЖУЩЕЙ"
                             "СИЛОЙ РЕАЛЬНОГО СЕКТОРА ЭКОНОМИКИ, ПРЕДОСТАВЛЯЮШИЙ ПОЛЕЗНЫЕ ДЛЯ ОБЩЕСТВА ТОВАРЫ И "
                             "УСЛУГИ И"
                             "ПРИЗНАНИЕ ЕГО ВЕДУЩЕЙ РОЛИ В ЭКОНОМИЧЕСКОМ РАЗВИТИИ.")
            bot.send_message(message.chat.id, f"Сейчас у нас открыты следующие вакансии:", reply_markup=generate_vacancy_buttons(vac))
        else:
            bot.send_message(message.chat.id, "Чем могу помочь?", reply_markup=main_markup())
            bot.register_next_step_handler(message, hr)


    @bot.callback_query_handler(func=lambda call: call.data.startswith('vac-'))
    def candidate_vacancy(callback):
        data = callback.data.split("-")[1]
        conn = sqlite3.connect("SqlLite.db")
        cur = conn.cursor()
        cur.execute(f"INSERT into `candidates` (Vacancy, ChatID) VALUES ('{data}', {callback.from_user.id});")
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
        try:
            age_int = int(message.text)
            conn = sqlite3.connect("SqlLite.db")
            cur = conn.cursor()
            cur.execute(f"UPDATE `candidates` SET `Age` = {age_int} WHERE `ID` = '{id}';")
            conn.commit()
            bot.send_message(message.chat.id, "Опишите ваши достижения (профессиональные или личные)?")
            bot.register_next_step_handler(message, achievments, id)
        except Exception:
            bot.send_message(message.chat.id, "Введите корректное значение")
            bot.register_next_step_handler(message, age, id)


    def achievments(message, id: int):
        conn = sqlite3.connect("SqlLite.db")
        cur = conn.cursor()
        cur.execute(
            f"UPDATE `candidates` SET (`Achievements`, `ChatID`) = ('{message.text}', {message.from_user.id}) WHERE `ID` = '{id}';")
        conn.commit()
        bot.send_message(message.chat.id, "Отлично, ожидайте пока наш HR откликнется на ваше резюме")
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
        if message.text != "Назад":
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
        else:
            bot.send_message(message.chat.id, "Чем могу помочь?", reply_markup=main_markup())
            bot.register_next_step_handler(message, hr)


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
            elif message.text == "Пригласить на собеседование✅":
                global id
                global chat
                conn = sqlite3.connect("SqlLite.db")
                cur = conn.cursor()
                cur.execute(f"UPDATE `candidates` SET `Accepted` = '1' WHERE `ID` = '{data[i][6]}';")
                id = data[i][6]
                chat = data[i][7]
                conn.commit()
                bot.send_message(message.chat.id, "Когда хотите назначить собеседование?", reply_markup=generate_calendar(datetime.now().year, datetime.now().month))
            elif message.text == "Отправить в резерв":
                conn = sqlite3.connect("SqlLite.db")
                cur = conn.cursor()
                cur.execute(f"DELETE FROM `candidates` WHERE `ID` = '{data[i][6]}';")
                date = datetime.now().strftime("%d-%m-%Y %H:%M")
                cur.execute(f"INSERT into `reservation` (`Date_Of_Reservation`, `Name`, `Resume`, `PhoneNumber`, `Age`, `Achievements`, `Chat_ID`, `Vacancy`) VALUES ('{date}', '{data[i][0]}', '{data[i][2]}', '{data[i][3]}', {data[i][4]}, '{data[i][5]}', '{data[i][7]}', '{data[i][9]}');")
                conn.commit()
                data.remove(data[i])
                bot.send_message(message.chat.id, f"Кандидат {data[i][0]} отправлен в резерв", reply_markup=get_vacancies())
                bot.send_message(message.chat.id, generate_candidate_text(data[0]), reply_markup=get_vacancies())
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
        bot.register_next_step_handler(message, Comment, data)

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
            bot.send_message(message.chat.id, "Чем могу помочь?", reply_markup=main_markup())
            bot.register_next_step_handler(message, hr)

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
        row = [types.InlineKeyboardButton(f'{calendar.month_name[month]} {year}', callback_data='ignore')]
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

    def generate_time_keyboard(date):
        markup = types.InlineKeyboardMarkup()
        row1 = []
        row2 = []
        for hour in range(8, 19):
            button = types.InlineKeyboardButton(str(hour), callback_data=f'hour-{hour}')
            if hour % 2 == 0:
                row1.append(button)
            else:
                row2.append(button)
        markup.row(*row1)
        markup.row(*row2)
        return markup

    @bot.callback_query_handler(func=lambda call: call.data.startswith('hour-'))
    def callback_select_hour(call):
        conn = sqlite3.connect("SqlLite.db")
        cur = conn.cursor()
        hour = int(call.data.split('-')[1])
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        cur.execute(f"UPDATE `candidates` SET `DateOfMeet` = '{date} {hour}:00' WHERE `ID` = '{id}';")
        conn.commit()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text="Онлайн"), types.KeyboardButton(text="Офлайн"))
        bot.send_message(call.message.chat.id, "В каком формате вы желаете провести собеседование?", reply_markup=keyboard)
        bot.register_next_step_handler(call.message, formatOfMeet, hour)

    def formatOfMeet(message, hour):
        bot.send_message(message.chat.id, "Добавьте коментарий к собеседованию (Если вы не хотите оставлять коментарий, отправьте 0)")
        bot.register_next_step_handler(message, Comment, hour, message.text)

    def Comment(message, hour, format):
        text = ""
        data = date.strip()
        date_obj = datetime.strptime(data, "%d-%m-%Y")
        months = {
            1: "Января",
            2: "Февраля",
            3: "Марта",
            4: "Апреля",
            5: "Мая",
            6: "Июня",
            7: "Июля",
            8: "Августа",
            9: "Сентября",
            10: "Октября",
            11: "Ноября",
            12: "Декабря"
        }
        new_date_str = f"{date_obj.day} {months[date_obj.month]}"
        bot.send_message(message.chat.id, f'Вы назначили собеседование {new_date_str} на {hour}:00, в {format} формате', reply_markup=types.ReplyKeyboardRemove())
        if format == "Офлайн":
            text = f"Поздравляю! Вас пригласили на собеседование. Ждем вас {new_date_str} в наш офис г.Костанай, ул.Дзержинского, 92А, 2 этаж. в {hour}:00."
        if format == "Онлайн":
            text = f"Поздравляю! Вас пригласили на собеседование {new_date_str} в {hour}:00."
        if message.text != "0":
            text += f"\nКоментарий: {message.text}"
        bot.send_message(chat, text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет"))
        bot.send_message(chat, "Желаете ли вы сменить время?", reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == 'Да')
    def HR_date(message):
        bot.send_message(message.chat.id, f"Хорошо, напишите на почту hr.zhanark@profi-soft.kz, скоро с вами свяжется наш Hr для назначения нового времени", reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(HR, f"Кандидат @{message.from_user.username} желает связаться с ним в другое время, ожидайте сообщения на почту")

    @bot.message_handler(func=lambda message: message.text == 'Нет')
    def HR_date2(message):
        bot.send_message(message.chat.id, "Отлично! Будем ждать вас в назначенное время")

    # Обработка коллбеков из календаря
    @bot.callback_query_handler(func=lambda call: call.data.startswith('day-'))
    def callback_select_day(call):
        global date
        year, month, day = map(int, call.data.split('-')[1:])
        date = f'{day:02d}-{month:02d}-{year} '
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=generate_time_keyboard(date))


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


    bot.polling(non_stop=True)

except Exception as e:
    bot.send_message(1239398217, str(e))
    bot.polling(non_stop=True)