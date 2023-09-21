import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InputMediaPhoto
import json
#загрузит наш секретный токен из .env файла
from dotenv import load_dotenv
import os
from os.path import join, dirname
from sql_main_things import get_category, get_products, add_user, add_products_to_cart_row, del_cart_line
from sql_main_things import get_cart_row, get_description_dish, add_to_order, delete_by_dish, get_orders,  change_order
from sql_main_things import cancel_order, add_product_rating, get_product_rating, get_orders_rating, add_order_rating
#import gspread
#from google_dict_stat import stat_user, stat_cat, stat_shop, dict1, new_dict2, dict2


def get_from_env(key):
    dotenv_path = join(dirname(__file__), 'token.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)


with open('data.json', 'r', encoding='utf-8') as f: #открыли файл с данными
    text = json.load(f)
    #print(text)

token = get_from_env('TG_BOT_TOKEN')
print(token)
#text["tg_token"] = token
# #передаю так токен, т.к. общий json сохраняется с общими строками
# token_ = text.get(token)
# print(token_)
bot = telebot.TeleBot(token)
lst_dishes = []
#блюдо сохраниться для добавления в корзину
temp_dish = ""
#блюдо для удаления
dish_for_delete = ""
#для сохранения номера заказа
number_order = ""
#вынесу для видимости в 2 декораторах
user_id = ''
markupI_start = InlineKeyboardMarkup()
#получаю категории из БД
categories = get_category()
#клавиатура категорий по данным из БД
markupI_cat = InlineKeyboardMarkup()
for x in categories:
    markupI_cat.add(InlineKeyboardButton(x, callback_data='2'+x))
markupI_cat.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))
markupI_cat_val = InlineKeyboardMarkup([])
#клава на кнопки описанием блюд
lst_add_card  = ["Добавить в корзину", "Меню категорий блюд"]
markupI_add_card = InlineKeyboardMarkup([])
for c in lst_add_card:
    markupI_add_card.add(InlineKeyboardButton(c, callback_data='4'+ c))
lst_start = ["Меню категорий блюд", "Корзина", "Статистика заказов", "Статистика блюд", "Заказы"]
for y in lst_start:
    markupI_start.add(InlineKeyboardButton(y, callback_data='1'+y))
#клавиатура по кнопке корзина для дальнейшего управления
lst_for_cart = ["Удаление из корзины", "Адрес доставки", "Способ оплаты", "Оформить заказ", "Меню категорий блюд"]
markupI_management_cart = InlineKeyboardMarkup()
for x in lst_for_cart:
    markupI_management_cart.add(InlineKeyboardButton(x, callback_data='5'+x))
#клавиатура по кнопке удаление из корзины для удаления блюд
markupI_delete_cart = InlineKeyboardMarkup()
address = ""
payment = ""
#в список добавятся строчками при оформлении заказа, т.к. не знаю порядок выбора пользователя
lst_address_payment = []
lst_address = ["Применить адрес", "Меню категорий блюд"]
markupI_address = InlineKeyboardMarkup()
for x in lst_address:
    markupI_address.add(InlineKeyboardButton(x, callback_data='7'+x))
lst_payment = ["Карта", "Наличность", "Меню категорий блюд"]
markupI_payment = InlineKeyboardMarkup()
for x in lst_payment:
    markupI_payment.add(InlineKeyboardButton(x, callback_data='8'+x))
#клава для изменения, удаления заказа
lst_order = ["Изменить заказ", "Отменить заказ", "Меню категорий блюд"]
markupI_order = InlineKeyboardMarkup()
for x in lst_order:
    markupI_order.add(InlineKeyboardButton(x, callback_data='9'+x))


@bot.message_handler(content_types=['text'])
def start(message):
    global user_id, address, number_order
    try:
        message.text = int(message.text)
    except:
        pass
    print(f"message.text, type(message.text) {message.text}, {type(message.text)}")
    if message.text == '/start':
        chat_id = message.chat.id
        print(f"chat_id {chat_id}")
        user_id = message.from_user.id
        print(f"user_id {user_id}")
        try:
            add_user(None, message.from_user.id, message.from_user.first_name + ' ' + message.from_user.last_name)
        except:
            pass
        bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markupI_start)
    #обработка номера заказа для удаления или редактирования
    elif  type(message.text) == int:
        number_order = message.text
        bot.send_message(message.chat.id, f"Заказ под номером {number_order} желаете:", reply_markup=markupI_order )
    #обработка ввода адреса
    else:
        address = message.text
        print(f"address {address}")

    print(f"get_orders after start {get_orders(user_id)}")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global user_id, lst_dishes, temp_dish, lst_dish_cart, dish_for_delete, dict_del_dish, \
        address, lst_address_payment, address, payment, number_order
    bot.answer_callback_query(callback_query_id=call.id, )
    # print(call)
    id = call.message.chat.id
    flag = call.data[0]
    data = call.data[1:]
    # print(flag, data)
    cart_total = get_cart_row(user_id)
    print(f"cart_total {cart_total}")
    cart_ = cart_total[0]
    total_ = cart_total[1]
    print(f"cart_ {cart_}")
    print(f"total_ {total_}")
    print(f"get_orders in 2 decorator {get_orders(user_id)}")
    # удаление всех кнопок клавиатуры
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
            pass
        elif data =="Статистика блюд":
            pass
        elif data =="Заказы":
            #получу все заказы со статусом 1(доступные для редактирования), статус 0 зазакам дает административка
            print(f"get_orders in orders {get_orders(user_id)}")
            lst_orders = get_orders(user_id)  # [(1, '', '2023-09-20 18:10:23.375185', 1, 1, 0), (2, 'Витебск, ул. Ленина, 89', '2023-09-20 18:30:17.736339', 1, 1, 1)]
            info_orders = "Заказ оформлен!\nВведите номер заказа для отмены или изменения и нажмите Enter:\n" +"№ заказа:  " + \
                          "адрес:                   " + "                          ожидаемое время\n"
            for item in lst_orders:
                info_orders +=  str(item[0]) + "                  " + str(item[1]) + "  " + str(item[2][11:]) + '\n'
            # print(f"change_order {change_order(user_id, 3)}")
            # print(f"change_order {change_order(user_id, 4)}")
            bot.send_message(call.message.chat.id, info_orders)
        elif data == "Назад в главное меню":
            bot.send_message(call.message.chat.id, "Выбирайте:", reply_markup=markupI_start)
    elif flag == '2':
        if data in categories:
            lst_dishes = get_products(data)
            for dish_ in lst_dishes:
                markupI_cat_val.add(InlineKeyboardButton(dish_, callback_data='3' + dish_))
            markupI_cat_val.add(
                InlineKeyboardButton("Назад в меню категорий блюд", callback_data='1' + "Меню категорий блюд"))
            markupI_cat_val.add(
                InlineKeyboardButton("Назад в главное меню", callback_data='1' + "Назад в главное меню"))
            bot.send_message(call.message.chat.id, "Выберите блюдо!",
                             reply_markup=markupI_cat_val)
    if flag == '3':
        if data in lst_dishes:
            temp_dish = data
            desc = get_description_dish(data)[0]
            desc_str = desc[0] + ": " + desc[1] + '. ' + "Стоимость: " + str(desc[2]) + '. ' + "Время: " + desc[3]
            bot.send_photo(call.message.chat.id, photo=get_description_dish(data)[1])
            bot.send_message(call.message.chat.id, desc_str, reply_markup=markupI_add_card)
    elif flag == '4':
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Добавить в корзину":
            # #??уточнить еще раз про amount, 2 клавы появляются тектовая с инфо, что в корзине, и с флагом 5 Управление корзиной...
            print(f"блюдо летит в добавить в корзину {temp_dish}")
            add_products_to_cart_row(user_id, temp_dish, 1)

    #флаг 5-клава управления корзиной...
    elif flag == "5":
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Удаление из корзины":
            markupI_delete_cart.keyboard.clear()
            for x in cart_:
                print(x[1])
                markupI_delete_cart.add(InlineKeyboardButton(x[1], callback_data='6' + x[1]))
            markupI_delete_cart.add(
                InlineKeyboardButton("Меню категорий блюд", callback_data='6' + "Меню категорий блюд"))
            bot.send_message(call.message.chat.id, "Выберите блюдо для удаления или вернитесь назад в меню категорий блюд", reply_markup=markupI_delete_cart)
        elif data == "Адрес доставки":
            bot.send_message(call.message.chat.id, "Введите адрес доставки и нажмите Enter", reply_markup=markupI_address)
        elif data == "Способ оплаты":
            bot.send_message(call.message.chat.id, "Выберите способ оплаты", reply_markup=markupI_payment)
        elif data == "Оформить заказ":
            lst_address_payment.append(address)
            lst_address_payment.append(payment)
            print(f"lst_address_payment {lst_address_payment}")
            add_to_order(user_id, lst_address_payment)
            bot.send_message(call.message.chat.id, "Оформить заказ!")
    #если блюдо прилетело из меню по удалению блюд(нажали на блюдо в этом меню)
    elif flag == "6":
        print(f"Блюдо летит для удаления {data}")
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        #нажали на блюдо - сработала функция удаления записи в cart_row
        else:
            delete_by_dish(user_id, data)
            bot.send_message(call.message.chat.id, f"Блюдо {data} удалено из корзины!")
    elif flag == "7":
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        else:# кнопка применить заказ
            bot.send_message(call.message.chat.id, "Адрес записан!")
    elif flag == "8":
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Карта":
            payment = "1"
            bot.send_message(call.message.chat.id, "Далее:\n\
            *назад в меню категорий блюд\n*назад в главное меню\n*корзина\n*оформить заказ")
        elif data == "Наличность":
            payment = "0"
    elif flag == "9":
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Изменить заказ":
            change_order(user_id, number_order)
            bot.send_message(call.message.chat.id, "Заказ изменен!")
        elif data == "Отменить заказ":
            cancel_order(user_id, number_order)
            bot.send_message(call.message.chat.id, "Заказ отменен!")












print("Ready")

def func_run_teleg():
    bot.infinity_polling()

func_run_teleg()
