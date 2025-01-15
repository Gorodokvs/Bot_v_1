import telebot
import sqlite3
import email
import imaplib
import chardet
import time

from pyexpat.errors import messages
from telebot import types

chat_id_salda = 380781080
chat_id_sibtrakt = 424347833
chat_id_kachkanar = 6209470364
chat_id_distr_order = [-1002314364737]
deliveryMethod = ''
paymentMethod = ''
bot = telebot.TeleBot('7647629268:AAE2HacxBvRl3etkfcIT8gzMz6XSZ3WXsVU')


# Вывод в консоль и ответ пользователю ID
@bot.message_handler(commands=['start'])
def start(message):
    print("Команда СТАРТ")
    bot.send_message(message.chat.id, message.chat.id)
    print(message.chat.id)


# Создание БД
@bot.message_handler(commands=['create_db'])
def createdb(message):
    print("Команда создания БД")
    create_db(message)


# Вывод команд
@bot.message_handler(commands=['help'])
def pomosh(message):
    print("Команда помощи")
    bot.send_message(message.chat.id,
                     "/start - узнать ID\n\n/create_db - создать базу данных\n\n/read_db - вывести данные DB\n\n/check_email - прочитать почту ")


# Вывод в консоль заказов из БД
@bot.message_handler(commands=['read_db'])
def read_db(message):
    print("Команда вывода в консоль БД")
    print("Начало чтения БД")
    conn = sqlite3.connect("orders_list.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")  # Выбор всех записей из таблицы users
    for row in cursor.fetchall():  # Вывод всех записей в консоль
        print(row)
    conn.close()  # Закрываем соединение с базой данных
    print("Завершение чтения БД")


# Запись заказа с сайта в БД
@bot.message_handler(func=lambda message: message.chat.id in chat_id_distr_order)
def handle_order(message):
    print("Получен новый заказ")
    orders = message.text.split('&')
    if len(orders) >= 12:
        print("Начало записи заказа в БД")
        conn = sqlite3.connect("orders_list.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (OrderNumber, CreationDate, OrderAmount, DeliveryMethod, PaymentMethod, Recipient, RecipientPhone, Region, City, DeliveryAddress, Comment, Products) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)
        ''', (
            orders[0],  # OrderNumber
            orders[1],  # CreationDate
            orders[2],  # OrderAmount
            orders[3],  # DeliveryMethod
            orders[4],  # PaymentMethod
            orders[5],  # Recipient
            orders[6],  # RecipientPhone
            orders[7],  # Region
            orders[8],  # City
            orders[9],  # DeliveryAddress
            orders[10],  # Comment
            orders[11]  # Products
        ))
        conn.commit()  # Подтверждаем изменения в базе данных
        print("Завершение записи заказа в БД: " + orders[0])
        conn.close()  # Закрываем соединение с базой данных
    else:
        print("Принят не верный формат данных для записи в БД")
    main()


@bot.callback_query_handler(func=lambda call: True)
def AnswerTime(call):
    try:
        if call.data == "20":
            print()
            bot.send_message(call.message.chat.id, "Круто!")  # Ответ на нажатие первой кнопки
        elif call.data == "30":
            bot.send_message(call.message.chat.id, "все еще не плохо")  # Ответ на нажатие второй кнопки
        elif call.data == "60":
            bot.send_message(call.message.chat.id, "можно и побыстрее")  # Ответ на нажатие третьей кнопки
        elif call.data == "90":
            bot.send_message(call.message.chat.id, "очень долго")  # Ответ на нажатие четвертой кнопки
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        nummord = call.message.text.find("Номер заказа:")
        nummord = call.message.text[nummord:][14:22]
        conn = sqlite3.connect("orders_list.db")
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET AnswerTime = ? WHERE OrderNumber = ?', (1, nummord))
        cursor.execute('UPDATE users SET CookingTime = ? WHERE OrderNumber = ?', (call.data, nummord))
        conn.commit()
        print("Записано в бд подтверждение заказа")
        conn.close()
        print(nummord)
    except Exception as e:  # Обработка исключений
        print(repr(e))  # Вывод ошибки в консоль
    main()


def reqvestTime(message):
    global chat_id_salda
    global chat_id_sibtrakt
    global chat_id_kachkanar
    global deliveryMethod
    global paymentMethod
    print("начало чтения бд")
    conn = sqlite3.connect('orders_list.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE RequestTime IS NULL')
    unknown_RequestTime = cursor.fetchall()

    for row in unknown_RequestTime:
        print("начало цикла отправки клавиатуры")
        if int(row[4]) == 1:
            deliveryMethod = 'Самовывоз'
        elif int(row[4]) == 2:
            deliveryMethod = 'Доставка курьером'

        if int(row[5]) == 3:
            paymentMethod = 'Наличные'
        elif int(row[5]) == 4:
            paymentMethod = 'Банковской картой'
        elif int(row[5]) == 5:
            paymentMethod = 'Оплата через сайт'

        # Формирование сообщения без названий полей
        formatted_message = (
            f"Номер заказа: {row[1]}\n"
            f"Дата: {row[2]}\n"
            f"Сумма заказа: {row[3]}\n"
            f"Метод доставки: {deliveryMethod}\n"
            f"Метод оплаты: {paymentMethod}\n"
            f"Имя: {row[6]}\n"
            f"Телефон: {row[7]}\n"
            f"Город: {row[9]}\n"
            f"Адрес доставки: {row[10]}\n"
            f"Заказ:\n{row[12]}\n"
            f"Комментарий: {row[11]}\n"
        )

        otvet = types.InlineKeyboardMarkup(row_width=2)
        button1 = types.InlineKeyboardButton("20минут", callback_data='20')
        button2 = types.InlineKeyboardButton("30минут", callback_data='30')
        button3 = types.InlineKeyboardButton("60минут", callback_data='60')
        button4 = types.InlineKeyboardButton("90минут", callback_data='90')
        otvet.add(button1, button2, button3, button4)

        # Отправка сообщения с форматированным текстом
        if int(row[8]) == 109:
            bot.send_message(chat_id_salda, formatted_message, reply_markup=otvet)
        elif int(row[8]) == 110:
            bot.send_message(chat_id_sibtrakt, formatted_message, reply_markup=otvet)
        elif int(row[8]) == 112:
            bot.send_message(chat_id_kachkanar, formatted_message, reply_markup=otvet)
        else:
            # Если данных недостаточно, отправляем простое сообщение
            bot.send_message(380781080, message.text)  # Отправка сообщения в указанный чат

        cursor.execute('UPDATE users SET RequestTime = ? WHERE OrderNumber = ?', (1, row[1]))
        conn.commit()
        print("Записано в бд запрос времени заказа")

    conn.commit()
    conn.close()
# Запрос почты
def checkemail():
    print("Начало запроса почты")
    # создаю соединение
    imap = imaplib.IMAP4_SSL('imap.yandex.ru')

    # логинюсь
    imap.login('botmyasnoi', 'axasvfykumndzzys')

    # выбираем папку входящие
    imap.select('INBOX')

    # ищем все письма с кодировкой ...
    typ, data = imap.search(None, 'UNSEEN')

    # перевод в список
    data = data[0].split()

    for i in data:
        status, data = imap.fetch(i, '(RFC822)')
        data = data[0][1]
        enc = chardet.detect(data)
        # print("\n\n\nКодировка: ", enc)

        msg = email.message_from_bytes(data)
        encoded_subject = msg['Subject']
        subject = email.header.decode_header(encoded_subject)

        decoded_parts = []
        for part, encoding in subject:
            if isinstance(part, bytes):
                if encoding is not None:
                    decoded_parts.append(part.decode(encoding))
                else:
                    decoded_parts.append(part.decode('utf-8'))
            else:
                decoded_parts.append(part)

        # Объединяем декодированные части
        final_subject = ''.join(decoded_parts)
        ordpay = final_subject.find("оплачен")

        if ordpay == 20:
            print("Получено подтверждение оплаты заказа")
            numord = final_subject.find("#")
            numord = final_subject[numord:][1:9]
            conn = sqlite3.connect("orders_list.db")
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET PaymentConfirmed = ? WHERE OrderNumber = ?', (1, numord))
            conn.commit()
            print("Записано в бд подтверждение заказа")
            conn.close()

    imap.close()
    print("Завершение запроса почты")

def create_db(message):
    print("Начало создания БД")
    conn = sqlite3.connect("orders_list.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            OrderNumber TEXT,
            CreationDate TEXT,
            OrderAmount INTEGER,
            DeliveryMethod TEXT,
            PaymentMethod TEXT,
            Recipient TEXT,
            RecipientPhone TEXT,
            Region TEXT,
            City TEXT,
            DeliveryAddress TEXT,
            Comment TEXT,
            Products TEXT,
            RequestTime INTEGER,
            AnswerTime INTEGER,
            SendSMSclient INTEGER,
            PaymentConfirmed INTEGER,
            CookingTime TEXT
        );
    ''')
    conn.commit()  # Подтверждаем изменения в базе данных
    conn.close()  # Закрываем соединение с базой данных
    print("Создана БД")

def sendsms():
    conn = sqlite3.connect('orders_list.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE CookingTime IS NOT NULL')
    unknown_SendSMSclient = cursor.fetchall()
    lasttaimsendsms = 0
    for row in unknown_SendSMSclient:
        clietphone = row[7]
        coocingtime = row[17]
        ssms = row[15]
        ordnam = row[1]
        if time.time() - lasttaimsendsms >= 3000 and ssms != 1:
            clietphone = clietphone.replace("(", "").replace(")", "").replace("+", "").replace("-", "").strip()
            clietphone = clietphone[1:]
            conn = sqlite3.connect("orders_list.db")
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET SendSMSclient = ? WHERE OrderNumber = ?', (1, ordnam))
            conn.commit()
            print("Записано в бд подтверждение заказа")
            conn.close()
            lasttaimsendsms = time.time()
            print(clietphone)

def main():
    reqvestTime(messages)
    checkemail()
    sendsms()

main()
bot.polling(none_stop=True)