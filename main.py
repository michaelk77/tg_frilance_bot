import telebot
from telebot import types
import time
from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, insert, select, update, or_, and_, BOOLEAN
import datetime as dt
from hashlib import sha256

# импортирования библиотек

slov = {}
metadata = MetaData()

engine = create_engine("your adrees to bd")  # подключение к бд

# Ниже объекты для управления базой данных и каждый отвечает за свою таблицу

Workers = Table("Workers", metadata,
                Column('id', Integer(), primary_key=True),
                Column('languages', String(255), nullable=True),
                Column("other", String(255), nullable=True),
                Column("date", String(64), nullable=False,
                       default=dt.date.today().strftime('%Y-%m-%d %H:%M:%S')),
                Column("login", String(64), unique=True, nullable=False),
                Column("hash", String(256), nullable=False),
                )

Jobs = Table("jobs", metadata,
             Column("name", String(64), nullable=False),
             Column('id', Integer(), primary_key=True),
             Column("employer_id", Integer(), ForeignKey('Employers.id'), nullable=False),
             Column("finding", BOOLEAN(), nullable=False),
             Column("worker_id", Integer(), ForeignKey('Workers.id'), nullable=True),
             Column("other", String(255), nullable=True),
             Column("sum", Integer(), nullable=True),
             Column("date", String(64), nullable=False,
                    default=dt.date.today().strftime('%Y-%m-%d %H:%M:%S')),
             Column("finished", BOOLEAN(), nullable=False),
             Column("categories", String(50), nullable=True)
             )

Employers = Table("Employers", metadata,
                  Column("id", Integer(), primary_key=True),
                  Column("other", String(255), nullable=True),
                  Column("date", String(64), nullable=False,
                         default=dt.date.today().strftime('%Y-%m-%d %H:%M:%S')),
                  Column("hash", String(256), nullable=False),
                  Column("login", String(64), unique=True, nullable=False),
                  )

Feedback_workers = Table("Feedback_workers", metadata,
                         Column('id', Integer(), primary_key=True),
                         Column('worker_id', Integer(), ForeignKey('Workers.id'), nullable=False),
                         Column("other", String(255), nullable=False),
                         Column("pros", BOOLEAN(), nullable=False), )
Feedback_employers = Table("Feedback_employers", metadata,
                           Column('id', Integer(), primary_key=True),
                           Column('employer_id', Integer(), ForeignKey('Employers.id'),
                                  nullable=False),
                           Column("other", String(255), nullable=False),
                           Column("pros", BOOLEAN(), nullable=False), )
metadata.create_all(engine)

bot = telebot.TeleBot('bot')
admin = "id"

inline_btn_1 = types.InlineKeyboardButton('Что же это за бот?', callback_data='button1')
inline_kb1 = types.InlineKeyboardMarkup().add(inline_btn_1)

inline_btn_1 = types.InlineKeyboardButton('Как пользоваться?', callback_data='button2')
inline_btn_2 = types.InlineKeyboardButton('Cразу приступим!', callback_data='button3')
inline_kb2 = types.InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row("Заказать выполнение", "Поиск работы")
keyboard1.row("Профиль")

keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard2.row("Прогромирование", "Доставка")
keyboard2.row("Тестирование", "Дизайн")
keyboard2.row("назад")

keyboard3 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard3.row("Регистрация", "Отмена")

keyboard4 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard4.row("Рабочий", "Работодатель")


@bot.message_handler(commands=['start'])
def process_command_1(message):
    w = str([message.text, message.from_user.id, message.from_user.first_name,
             message.from_user.last_name])
    bot.send_message(message.from_user.id, "Привет👋", reply_markup=inline_kb1)


@bot.callback_query_handler(func=lambda call: True)
def bottonconfig(call):
    if call.data == "button1":
        process_callback_button1(call)
    elif call.data == "button2":
        process_callback_button2(call)
    elif call.data == "button3":
        process_callback_button3(call)
    else:
        bot.send_message(call.from_user.id, f"@{str(call.data)}")
        bot.answer_callback_query(call.id)


def process_callback_button1(callback_query):
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.from_user.id,
                     'Данный бот эта платформа для поиска работы, а также возможность заказа '
                     'выполнения вашего проекта у других учасников', reply_markup=inline_kb2)


def process_callback_button2(callback_query):
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.from_user.id,
                     "Описание функционала:\n\nПоиск работы - позволит вам искать вакансии в "
                     "выбанной вами сфере\n\nЗаказать выполнение - позволяет заказать выполнение "
                     "проекта по вашему описанию",
                     reply_markup=keyboard1)


def process_callback_button3(callback_query):
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.from_user.id,
                     'Ну поехали!', reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def work(message):
    if message.text == "Заказать выполнение":
        bot.send_message(message.from_user.id, "Введите название для вашего проекта")
        bot.register_next_step_handler(message, sakas)
    elif message.text == "Поиск работы":
        bot.send_message(message.from_user.id, "Выберете свою область работы",
                         reply_markup=keyboard2)
    elif message.text == "Прогромирование":
        conn = engine.connect()
        bot.send_message(message.from_user.id, "Список вакансий программирования:")
        a = "Прогромирование"
        jobs_c = conn.execute(select(Jobs).where(Jobs.c.categories == a)).all()
        zapros = jobs_c
        for i in zapros:
            idtg = conn.execute(select(Employers).where(Employers.c.id == i[2])).first()
            inline_btn_10 = types.InlineKeyboardButton('Откликнуться', callback_data=idtg[-1])
            inline_kb10 = types.InlineKeyboardMarkup().add(inline_btn_10)
            bot.send_message(message.from_user.id, i[0] + "\n\n" + i[5], reply_markup=inline_kb10)
    elif message.text == "Доставка":
        bot.send_message(message.from_user.id, "Список вакансий доставок:")
        conn = engine.connect()
        a = "Доставка"
        jobs_c = conn.execute(select(Jobs).where(Jobs.c.categories == a)).all()
        zapros = jobs_c
        for i in zapros:
            idtg = conn.execute(select(Employers).where(Employers.c.id == i[2])).first()
            inline_btn_10 = types.InlineKeyboardButton('Откликнуться', callback_data=idtg[-1])
            inline_kb10 = types.InlineKeyboardMarkup().add(inline_btn_10)
            bot.send_message(message.from_user.id, i[0] + "\n\n" + i[5], reply_markup=inline_kb10)
    elif message.text == "Тестирование":
        bot.send_message(message.from_user.id, "Список вакансий тестирования:")
        conn = engine.connect()
        a = "Тестирование"
        jobs_c = conn.execute(select(Jobs).where(Jobs.c.categories == a)).all()
        zapros = jobs_c
        for i in zapros:
            print(i)
            idtg = conn.execute(select(Employers).where(Employers.c.id == i[2])).first()
            inline_btn_10 = types.InlineKeyboardButton('Откликнуться', callback_data=idtg[-1])
            inline_kb10 = types.InlineKeyboardMarkup().add(inline_btn_10)
            bot.send_message(message.from_user.id, i[0] + "\n\n" + i[5], reply_markup=inline_kb10)
    elif message.text == "Дизайн":
        conn = engine.connect()
        a = "Дизайн"
        jobs_c = conn.execute(select(Jobs).where(Jobs.c.categories == a)).all()
        zapros = jobs_c
        for i in zapros:
            idtg = conn.execute(select(Employers).where(Employers.c.id == i[2])).first()
            inline_btn_10 = types.InlineKeyboardButton('Откликнуться', callback_data=idtg[-1])
            inline_kb10 = types.InlineKeyboardMarkup().add(inline_btn_10)
            bot.send_message(message.from_user.id, i[0] + "\n\n" + i[5], reply_markup=inline_kb10)
    if message.text == "Профиль":
        conn = engine.connect()
        r = conn.execute(select([Workers]).where(
            Workers.c.login == message.from_user.username
        ))
        answer = r.first()
        r1 = conn.execute(select([Employers]).where(
            Employers.c.login == message.from_user.username
        ))
        answer1 = r1.first()
        # print(answer1, answer)
        if answer:
            keyboard10 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard10.row("редактировать", "назад")
            bot.send_message(message.from_user.id, str(answer[4]) + "\n\n" + str(answer[2]),
                             reply_markup=keyboard10)
        elif answer1:
            keyboard14 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard14.row("редактировать", "назад")
            bot.send_message(message.from_user.id, str(answer1[4]) + "\n\n" + str(answer1[1]),
                             reply_markup=keyboard14)
        else:
            bot.send_message(message.from_user.id, f"Ваш логин: {message.from_user.username}")
            bot.send_message(message.from_user.id,
                             "Для полного функционирования бота вам нужно зарегистрироваться",
                             reply_markup=keyboard3)
    if message.text == "Регистрация":
        bot.send_message(message.from_user.id, "Выберите тип аккаунта", reply_markup=keyboard4)
        bot.register_next_step_handler(message, vibor)
    if message.text == "Отмена" or message.text == "назад":
        bot.send_message(message.from_user.id, "Возвращаемся в главное меню", reply_markup=keyboard1)
    if message.text == "редактировать":
        redopis(message)


def vibor(message):
    if message.text == "Работодатель":
        bot.send_message(message.from_user.id, "Введите свой пароль")
        bot.register_next_step_handler(message, regrab)
    elif message.text == "Рабочий":
        bot.send_message(message.from_user.id, "Введите свой пароль")
        bot.register_next_step_handler(message, reg)
    else:
        print(34)


def sakas(message):
    global slov
    slov[message.from_user.username] = str(message.text)
    # print(6789)
    conn = engine.connect()
    r = conn.execute(
        select(Employers).where(Employers.c.login == message.from_user.username)).first()
    # print(r)
    ins = insert(Jobs).values(employer_id=r[0],
                              name=str(message.text), finished=False, finding=True)
    conn.execute(ins)
    bot.send_message(message.from_user.id, "Введите описание")
    bot.register_next_step_handler(message, opisanie)


def opisanie(message):
    conn = engine.connect()
    r = conn.execute(
        select(Employers).where(Employers.c.login == message.from_user.username)).first()
    # print(r[0])
    conn.execute(update(Jobs).where(Jobs.c.employer_id == r[0],
                                    Jobs.c.name == slov[message.from_user.username]).values(
        other=str(message.text)))
    bot.send_message(message.from_user.id, "Введите желаемую стоимость в рублях")
    bot.register_next_step_handler(message, rub)


def rub(message):
    conn = engine.connect()
    r = conn.execute(
        select(Employers).where(Employers.c.login == message.from_user.username)).first()
    r = conn.execute(update(Jobs).where(Jobs.c.employer_id == r[0],
                                        Jobs.c.name == slov[message.from_user.username]).values(
        sum=message.text))
    asd = telebot.types.ReplyKeyboardMarkup()
    asd.row("Прогромирование", "Доставка", "Тестирование", "Дизайн")
    bot.send_message(message.from_user.id, "Выберите категорию", reply_markup=asd)
    bot.register_next_step_handler(message, categori)


def categori(message):
    conn = engine.connect()
    r = conn.execute(
        select(Employers).where(Employers.c.login == message.from_user.username)).first()
    conn.execute(update(Jobs).where(Jobs.c.employer_id == r[0],
                                    Jobs.c.name == slov[message.from_user.username]).values(
        categories=str(message.text)))
    r1 = conn.execute(select([Jobs]).where(
        Jobs.c.employer_id == r[0]
    ))
    answer1 = r1.first()
    # print(answer1)
    if answer1:
        bot.send_message(message.from_user.id, "Успешно", reply_markup=keyboard1)
    else:
        bot.send_message(message.from_user.id, "Что-то пошло не так", reply_markup=keyboard1)


def redopis(message):
    conn = engine.connect()
    r = conn.execute(select([Workers]).where(
        Workers.c.login == message.from_user.username
    ))
    answer = r.first()
    r1 = conn.execute(select([Employers]).where(
        Employers.c.login == message.from_user.username
    ))
    answer1 = r1.first()
    bot.send_message(message.from_user.id, "Введите новое описание")
    if answer:
        bot.register_next_step_handler(message, opisan)
    elif answer1:
        bot.register_next_step_handler(message, opisanrab)


def reg(message):
    conn = engine.connect()
    ins = insert(Workers).values(login=str(message.from_user.username),
                                 hash=str(sha256(message.text.encode("UTF-8")).hexdigest()))
    r = conn.execute(ins)
    bot.send_message(message.from_user.id, "Введите ваше описание, потом его можно будет изменить")
    bot.register_next_step_handler(message, opisan)


def regrab(message):
    conn = engine.connect()
    ins = insert(Employers).values(login=str(message.from_user.username),
                                   hash=str(sha256(message.text.encode("UTF-8")).hexdigest()))
    r = conn.execute(ins)
    bot.send_message(message.from_user.id,
                     "Введите описание своей компании, потом его можно будет изменить")
    bot.register_next_step_handler(message, opisanrab)


def opisan(message):
    conn = engine.connect()
    r = conn.execute(update(Workers).where(Workers.c.login == message.from_user.username).values(
        other=str(message.text)))
    r = conn.execute(select(Workers).where(
        Workers.c.login == message.from_user.username
    ))
    answer = r.first()
    if answer:
        bot.send_message(message.from_user.id, "Успешная регистрация", reply_markup=keyboard1)
    else:
        bot.send_message(message.from_user.id, "Что-то пошло не так", reply_markup=keyboard1)


def opisanrab(message):
    conn = engine.connect()
    r = conn.execute(update(Employers).where(Employers.c.login == message.from_user.username).values(
        other=str(message.text)))
    r = conn.execute(select(Employers).where(
        Employers.c.login == message.from_user.username
    ))
    answer = r.first()
    if answer:
        bot.send_message(message.from_user.id, "Успешная регистрация", reply_markup=keyboard1)
    else:
        bot.send_message(message.from_user.id, "Что-то пошло не так", reply_markup=keyboard1)


while True:
    try:
        print("@frilansmsk_bot")
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        time.sleep(1)
        print(str(e))