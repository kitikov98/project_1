import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InputMediaPhoto
import json
#загрузит наш секретный токен из .env файла
#from dotenv import load_dotenv
import os
from os.path import join, dirname
from progekt_1_SQL import Database


db = Database('db.sqlite')


text1 = ''
with open('data.json', 'r', encoding='utf-8') as f: #открыли файл с данными
    text1 = json.load(f)

bot = telebot.TeleBot(text1["tg_token"])
markupI_start = InlineKeyboardMarkup()

#клавиатура категорий по данным из БД
markupI_cat = InlineKeyboardMarkup()
for x in db.get_category():
    markupI_cat.add(InlineKeyboardButton(x, callback_data='2'+x))
markupI_cat.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
#клавиатура на меню блюд, формируется ниже динамически, в зависимости от выбранной категории
markupI_cat_val = InlineKeyboardMarkup([])
#клава на кнопки описанием блюд
markupI_add_card = InlineKeyboardMarkup([])
markupI_add_card.add(InlineKeyboardButton("Добавить в корзину", callback_data='4'+ "Добавить в корзину"))
markupI_add_card.add(InlineKeyboardButton("Меню категорий блюд", callback_data='1'+ "Меню категорий блюд"))
lst_start = ["Меню категорий блюд", "Корзина", "Статистика заказов", "Статистика блюд", "Заказы"]
for y in lst_start:
    markupI_start.add(InlineKeyboardButton(y, callback_data='1'+y))
#клавиатура по кнопке корзина для дальнейшего управления,
lst_for_cart = ["Удаление из корзины", "Изменить адрес доставки", "Изменить способ оплаты", "Оформить заказ"]
markupI_management_cart = InlineKeyboardMarkup()
for x in lst_for_cart:
    markupI_management_cart.add(InlineKeyboardButton(x, callback_data='5'+x))
markupI_management_cart.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
#клавиатура по кнопке удаление из корзины для удаления блюд
markupI_delete_cart = InlineKeyboardMarkup()
address = ""
payment = ""
#будет формироваться после user
lst_address_payment = []
lst_payment = ["Карта", "Наличность"]
markupI_payment = InlineKeyboardMarkup()
for x in lst_payment:
    markupI_payment.add(InlineKeyboardButton(x, callback_data='8'+x))
#клава для изменения, удаления заказа
lst_order = ["Изменить заказ", "Отменить заказ", "Меню категорий блюд"]
markupI_order = InlineKeyboardMarkup()
for x in lst_order:
    markupI_order.add(InlineKeyboardButton(x, callback_data='9'+x))
# #для отзыва и оценки
# review_ = ''
# mark_ = ''
# #флаг для отзыва, если True, значит летит отзыв на блюдо
flag_review = False
#клавиатура категорий для статистики по данным из БД
markupI_stat_cat = InlineKeyboardMarkup()
for x in db.get_category():
    markupI_stat_cat.add(InlineKeyboardButton(x, callback_data='10'+x))
markupI_stat_cat.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
#клавиатура на меню блюд для статистики(рейтинга), формируется ниже динамически, в зависимости от выбранной категории
markupI_stat_dish = InlineKeyboardMarkup([])# флаг 11
#использую для рейтинга блюд
markupI_rating = InlineKeyboardMarkup()
markupI_rating.add(InlineKeyboardButton("Выставить рейтинг", callback_data='12'+"Выставить рейтинг"))
markupI_rating.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
#клава для выставления оценки блюду
lst_digits = ["1", "2", "3", "4", "5"]
markupI_digits = InlineKeyboardMarkup()
for x in lst_digits:
    markupI_digits.add(InlineKeyboardButton(x, callback_data='13'+x))
markupI_digits.add(InlineKeyboardButton("Отзыв", callback_data='13'+"Отзыв"))
markupI_digits.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
#клава для отзыва по блюду
markupI_review = InlineKeyboardMarkup()
markupI_review.add(InlineKeyboardButton("Отправить отзыв", callback_data='14'+"Отправить отзыв"))
markupI_review.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
#использую для рейтинга заказов
markupI_rating_order = InlineKeyboardMarkup()
markupI_rating_order.add(InlineKeyboardButton("Выставить рейтинг", callback_data='15'+"Выставить рейтинг"))
markupI_rating_order.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
#для вывода заказов по номерам и времени, флаг 16
markupI_stat_order = InlineKeyboardMarkup()
id_order_stat = ''
#для различия отзыва по блюду и отзыва по заказу
flag_review_order = False
# mark_order = ""
# review_order = ''
#если True - летит отзыв на заказ
flag_review_order = False
#клава для выставления оценки заказу
markupI_mark_order = InlineKeyboardMarkup()
for x in lst_digits:
    markupI_mark_order.add(InlineKeyboardButton(x, callback_data='17'+x))
markupI_mark_order.add(InlineKeyboardButton("Отзыв", callback_data='17'+"Отзыв"))
markupI_mark_order.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
#клава для отзыва по заказу
markupI_review_order = InlineKeyboardMarkup()
markupI_review_order.add(InlineKeyboardButton("Отправить отзыв", callback_data='18'+"Отправить отзыв"))
markupI_review_order.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
#словарь для 1 пользователя со всеми его выборами
dict_users = {}


@bot.message_handler(content_types=['text'])
def start(message):
    global address, number_order, new_lst_address_payment
    global id_order_stat, flag_review_order, flag_review
    #print(f"message.chat.id {message.chat.id}")
    if message.from_user.id not in dict_users:
        dict_users[message.from_user.id] = {}
    print(dict_users)
    print(f"message.from_user.id {message.from_user.id}")
    try:
        message.text = int(message.text)
    except:
        pass
    print(f"message.text, type(message.text) {message.text}, {type(message.text)}")
    print(f"flag_review {flag_review}")
    if message.text == '/start':
        #заберет и имя, и фамилию
        try:
            db.add_user(None, message.from_user.id, message.from_user.first_name + ' ' + message.from_user.last_name)
        except:
            pass
        bot.send_message(message.chat.id, "Введите адрес доставки и нажмите Enter:")
    #обработка номера заказа для удаления или редактирования
    elif type(message.text) == int:
        bot.send_message(message.chat.id, f"Что желаете сделать с заказом № {message.text}?",
                         reply_markup=markupI_order)
        dict_users[message.chat.id]['number_order'] = message.text
    elif len(lst_address_payment) == 0 and flag_review == False and flag_review_order == False:
        print(f"Летит адрес {message.text}")
        lst_address_payment.append(message.text)
        bot.send_message(message.chat.id, "Адрес записан!")
        bot.send_message(message.chat.id, "Выберите способ оплаты:", reply_markup=markupI_payment)
    elif len(lst_address_payment) == 2 and flag_review == False and flag_review_order == False:
        print(f"Летит адрес {message.text}")
        lst_address_payment[0] = message.text
        bot.send_message(message.chat.id, "Адрес записан!")
        db.add_delivery(message.from_user.id, lst_address_payment)
    #обработка ввода отзыва
    elif flag_review == True and flag_review_order == False:
        #review_ = message.text
        dict_users[message.chat.id]['review_'] = message.text
        print(f"review_ {message.text}")
        bot.send_message(message.chat.id, "Отзыв по блюду сохранен! Можете его отправить!")
    elif flag_review_order == True:
        #review_order = message.text
        dict_users[message.chat.id]['review_order'] = message.text
        #print(f"review_order {review_order}")
        bot.send_message(message.chat.id, "Отзыв по заказу сохранен! Можете его отправить!")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global lst_dish_cart, dict_del_dish, dish_for_stat,flag_review_order, \
        flag_review
    global address, lst_address_payment, address, payment, new_lst_address_payment
    global id_order_stat
    bot.answer_callback_query(callback_query_id=call.id, )
    flag = ""
    data = ""
    #нужно отделить цифры в call.data, т.к. м.б. и > 1 цифры
    for char in call.data:
        if char.isdigit() and len(flag) < 2:
            flag += char
        else:
            data += char
    cart_total = db.get_cart_row(call.message.chat.id)
    print(f"cart_total {cart_total}")
    cart_ = cart_total[0]
    total_ = cart_total[1]
    print(f"cart_ {cart_}")
    print(f"total_ {total_}")
    print(f"get_orders in 2 decorator {db.get_orders(call.message.chat.id)}")
    print(f"flag = {flag}")
    print(f"data = {data}")
    markupI_cat_val.keyboard.clear()
    if flag == "1":
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Корзина":
            desc_cart = ''
            for item in cart_:
                desc_cart += '*' + str(item[1]) + ' ' + str(item[2]) + " шт." + '\n'
            bot.send_message(call.message.chat.id, desc_cart + "Стоимость: " + str(total_), reply_markup=markupI_management_cart)
        elif data == "Статистика заказов":
            average_rating = db.get_orders_rating()[0]
            reviews = db.get_orders_rating()[1]
            str_reviews = '\n'
            num = 1
            for i in reviews:
                str_reviews += str(num) + '. ' + i + '\n'
                num += 1
            #ветвление есть средний рейтинг или нет
            if average_rating == "B":
                bot.send_message(call.message.chat.id, db.get_orders_rating())
            else:
                bot.send_message(call.message.chat.id, f"\n Средний рейтинг заказов: {average_rating}, \nОтзывы: {str_reviews}", reply_markup=markupI_rating_order)
        elif data =="Статистика блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюда для рейтинга", reply_markup=markupI_stat_cat)
        elif data =="Заказы":
            #получу все заказы со статусом 1(доступные для редактирования), статус 0 заказам дает администратор
            info_orders = "Информация о заказах(№ заказа, ожидаемое время)\n"
            #None формируется из БД, если заказ был отменен, изменение статуса по отзыву
            if db.get_orders(call.message.chat.id) == [] or len(db.get_orders(call.message.chat.id))==db.get_orders(call.message.chat.id).count(None):
                bot.send_message(call.message.chat.id, "Нет заказов, доступных для редактирования!")
            else:
                for item in db.get_orders(call.message.chat.id):
                    if item == None:
                        continue
                    else:
                        info_orders += str(item[0]) + ". " + str(item[1]) + '\n'
                bot.send_message(call.message.chat.id, info_orders)
                bot.send_message(call.message.chat.id, "При необходимости редактировать заказ введите номер заказа и Enter")
        elif data == "Назад в главное меню":
            bot.send_message(call.message.chat.id, "Выбирайте:", reply_markup=markupI_start)
    elif flag == '2':
        for dish_ in db.get_products(data):
            markupI_cat_val.add(InlineKeyboardButton(dish_, callback_data='3' + dish_))
        markupI_cat_val.add(
            InlineKeyboardButton("Назад в меню категорий блюд", callback_data='1' + "Меню категорий блюд"))
        markupI_cat_val.add(
            InlineKeyboardButton("Назад в главное меню", callback_data='1' + "Назад в главное меню"))
        bot.send_message(call.message.chat.id, "Выберите блюдо!",
                         reply_markup=markupI_cat_val)
    if flag == '3':
        #здесь только просматриваю, сохраняю для кнопки добавить в корзину
        dict_users[call.message.chat.id]['dish'] = data
        print(f"dict_users {dict_users}")
        desc = db.get_description_dish(data)[0]
        desc_str = desc[0] + ": " + desc[1] + '. ' + "Стоимость: " + str(desc[2]) + '. ' + "Время: " + desc[3]
        bot.send_photo(call.message.chat.id, photo=db.get_description_dish(data)[1])
        bot.send_message(call.message.chat.id, desc_str, reply_markup=markupI_add_card)
    elif flag == '4':
        print(f"Блюдо летит в добавить в корзину {dict_users.get(call.message.chat.id).get('dish')}")
        db.add_products_to_cart_row(call.message.chat.id, dict_users.get(call.message.chat.id).get('dish'), 1)
        bot.send_message(call.message.chat.id, "Блюдо добавлено в корзину!")
    #флаг 5-клава управления корзиной...
    elif flag == "5":
        if data == "Удаление из корзины":
            markupI_delete_cart.keyboard.clear()
            for x in cart_:
                print(x[1])
                markupI_delete_cart.add(InlineKeyboardButton(x[1], callback_data='6' + x[1]))
            markupI_delete_cart.add(
                InlineKeyboardButton("Меню категорий блюд", callback_data='6' + "Меню категорий блюд"))
            bot.send_message(call.message.chat.id, "Выберите блюдо для удаления или вернитесь назад в меню категорий блюд", reply_markup=markupI_delete_cart)
        elif data == "Изменить адрес доставки":
            bot.send_message(call.message.chat.id, "Введите адрес доставки и нажмите Enter")
        elif data == "Изменить способ оплаты":
            bot.send_message(call.message.chat.id, "Выберите способ оплаты", reply_markup=markupI_payment)
        elif data == "Оформить заказ":
            print(db.get_cart_row(call.message.chat.id))
            #если total=0
            if db.get_cart_row(call.message.chat.id)[1] == 0:
                bot.send_message(call.message.chat.id, "Вы не выбрали блюда!")
            else:
                db.add_to_order(call.message.chat.id)
                bot.send_message(call.message.chat.id, "Заказ оформлен!")
    #если блюдо прилетело из меню по удалению блюд(нажали на блюдо в этом меню)
    elif flag == "6":
        print(f"Блюдо летит для удаления {data}")
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        #нажали на блюдо - сработала функция удаления записи в cart_row
        else:
            db.delete_by_dish(call.message.chat.id, data)
            bot.send_message(call.message.chat.id, f"Блюдо {data} удалено из корзины!")
    elif flag == "8":
        if data == "Карта":
            payment = "1"
            if len(lst_address_payment) == 1:
                lst_address_payment.append(payment)
            elif len(lst_address_payment) == 2:
                lst_address_payment[1] = payment
            print(f"lst_address_payment {lst_address_payment}")
            db.add_delivery(call.message.chat.id, lst_address_payment)
            bot.send_message(call.message.chat.id, "Вы выбрали способ оплаты картой!")
            bot.send_message(call.message.chat.id, "Выбирайте:", reply_markup=markupI_start)
        elif data == "Наличность":
            payment = "0"
            if len(lst_address_payment) == 1:
                lst_address_payment.append(payment)
            elif len(lst_address_payment) == 2:
                lst_address_payment[1] = payment
            print(f"lst_address_payment {lst_address_payment}")
            db.add_delivery(call.message.chat.id, lst_address_payment)
            bot.send_message(call.message.chat.id, "Вы выбрали способ оплаты наличными!")
            bot.send_message(call.message.chat.id, "Выбирайте:", reply_markup=markupI_start)
    elif flag == "9":
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Изменить заказ":
            db.change_order(call.message.chat.id, dict_users.get(call.message.chat.id).get('number_order'))
            bot.send_message(call.message.chat.id, f"Можете редактировать заказ {dict_users.get(call.message.chat.id).get('number_order')}!")
        elif data == "Отменить заказ":
            db.cancel_order(dict_users.get(call.message.chat.id).get('number_order'))
            bot.send_message(call.message.chat.id, "Заказ отменен!")
    elif flag == '10':
        #формирую клавиатуры блюд для статистики
        markupI_stat_dish.keyboard.clear()
        for dish_ in db.get_products(data):
            markupI_stat_dish.add(InlineKeyboardButton(dish_, callback_data='11' + dish_))
        markupI_stat_dish.add(
            InlineKeyboardButton("Назад в главное меню", callback_data='1' + "Назад в главное меню"))
        bot.send_message(call.message.chat.id, "Выберите блюдо для рейтинга!",
                         reply_markup=markupI_stat_dish)
    #средний рейтинг посчитается после ввода 10 рейтингов и отзывов, и дляя отзывов "Принят"
    elif flag == '11':
        print(f"Блюдо летит для рейтинга {data}")
        dict_users[call.message.chat.id]['dish_for_stat'] = data
        #average_rating = db.get_product_rating(data)[0]
        reviews = "\n"
        num = 1
        for item in db.get_product_rating(data)[1]:
            reviews += str(num)+ '. ' + item + '\n'
            num += 1
        print(f"average_rating {average_rating}")
        # #ветвление где есть отзывы, где нет
        if  db.get_product_rating(data)[0] == "В":
            bot.send_message(call.message.chat.id, db.get_product_rating(data), reply_markup=markupI_rating)
        else:
            bot.send_message(call.message.chat.id, f"Cредний рейтинг {db.get_product_rating(data)[0]}, \n Отзывы: {reviews}" ,
                         reply_markup=markupI_rating)
    elif flag == "12":
        if data == "Выставить рейтинг":
            bot.send_message(call.message.chat.id, "Выберите рейтинг блюда!",
                             reply_markup=markupI_digits)
    elif flag == "13":
        print(f"data in 13 {data}")
        if data == "Отзыв":
            flag_review = True
            bot.send_message(call.message.chat.id, "Введите отзыв и нажмите Enter!", reply_markup=markupI_review)
        elif data == "1" or data == "2" or data == "3" or data == "4" or data == "5":
            dict_users[call.message.chat.id]['mark_'] = data
            bot.send_message(call.message.chat.id, "Ваш рейтинг сохранен! Нажмите на кнопку 'Отзыв'!")
    elif flag == "14":
        if data == "Отправить отзыв":
            if 'review_' not in dict_users.get(call.message.chat.id) or 'mark_' not in dict_users.get(call.message.chat.id):
                bot.send_message(call.message.chat.id, "Вам необходимо заполнить отзыв и выставить рейтинг!")
            else:
                db.add_product_rating(call.message.chat.id, dict_users.get(call.message.chat.id).get('dish_for_stat'), dict_users.get(call.message.chat.id).get('review_'),dict_users.get(call.message.chat.id).get('mark_'))
                bot.send_message(call.message.chat.id, "Отзыв отправлен!")
    elif flag == "15":
        if data == "Выставить рейтинг":
            #c закрытыми заказами, со статусом 0
            # orders_ = db.get_to_rat_ord(call.message.chat.id)
            # print(f"orders_ {orders_}")
            markupI_stat_order.keyboard.clear()
            for item in db.get_to_rat_ord(call.message.chat.id):
                if item == None:
                    continue
                else:
                    markupI_stat_order.add(InlineKeyboardButton(str(item[0]) + ' ' + item[1], callback_data='16' + str(item[0])))
            markupI_stat_order.add(
                InlineKeyboardButton("Назад в главное меню", callback_data='1' + "Назад в главное меню"))
            bot.send_message(call.message.chat.id, "Выберите заказ для рейтинга!", reply_markup=markupI_stat_order)
    elif flag == "16":
        flag_id_order_stat = True
        id_order_stat = data
        print(f"Летит номер заказа для peйтинга = {data}")
        bot.send_message(call.message.chat.id, f"Выберите рейтинг по заказу {data}\n и для написания отзыва выбирайте кнопку 'Отзыв'!", reply_markup=markupI_mark_order)
    elif flag == "17":
        print(f"Летит рейтинг заказа = {data}")
        #if dict_users.get(call.message.chat.id).get('mark_order') == '':
        dict_users[call.message.chat.id]['mark_order'] = data
        print(f"data in 17 {data}")
        if data == "Отзыв":
            flag_review_order  = True
            bot.send_message(call.message.chat.id, "Напишите отзыв в чате и введите Enter!", reply_markup=markupI_review_order)
    elif flag == "18":
        if data == "Отправить отзыв":
            if "review_order" not in dict_users[call.message.chat.id] or "mark_order" not in dict_users[call.message.chat.id]:
                bot.send_message(call.message.chat.id, "Вам необходимо заполнить отзыв и выставить рейтинг!")
            else:
                print(f"Отправляется отзыв по заказу data = {data}")
                # print(f'user_id {call.message.chat.id}')
                # print(f'id_order_stat {id_order_stat}')
                # print(f'review_order {review_order}')
                # print(f'mark_order {mark_order}')
                db.add_order_rating(call.message.chat.id, id_order_stat, dict_users.get(call.message.chat.id).get(review_order), dict_users.get(call.message.chat.id).get(mark_order))
                bot.send_message(call.message.chat.id, "Отзыв по заказу отправлен!")


print("Ready")

def func_run_teleg():
    bot.infinity_polling()

func_run_teleg()
