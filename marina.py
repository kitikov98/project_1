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
from sql_main_things import get_category, get_products, add_user, add_products_to_cart_row, del_cart_line, get_cart_row, get_description_dish
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
#список блюд корзины, используется при удалении блюд, но удаляться будет блюдо на которое нажали
lst_dish_cart = []
#блюдо для удаления
dish_for_delete = ""
#словарь для удаления
dict_del_dish = {}
#вынесу в глобальную область, чтобы вызвать корзину с предыдущего сеанса один раз и видимости в 2 декораторах
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
markupR_desc_dish = ReplyKeyboardMarkup(resize_keyboard=True)
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

#клавиатура по кнопке управление корзиной для удаления блюд
markupI_delete_cart = InlineKeyboardMarkup()


@bot.message_handler(content_types=['text'])
def start(message):
    global user_id
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


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global lst_dishes, temp_dish, lst_dish_cart, dish_for_delete, dict_del_dish
    # user_id = call.from_user.id
    # print(f"user_id {user_id}")
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
            pass
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
           #markupR_desc_dish.keyboard.clear()
            desc = get_description_dish(data)[0]
            desc_str = desc[0] + ": " + desc[1] + '. ' + "Стоимость: " + str(desc[2]) + '. ' + "Время: " + desc[3]
            markupR_desc_dish.add(KeyboardButton(desc_str))
            # можно убрать эту клаву
            #bot.send_message(call.message.chat.id, "Описание блюда: ", reply_markup = markupR_desc_dish)
            #bot.send_message(call.message.chat.id, "Описание", reply_markup=markupR_desc_dish)
            bot.send_photo(call.message.chat.id, photo=get_description_dish(data)[1])
            bot.send_message(call.message.chat.id, desc_str, reply_markup=markupI_add_card)
    elif flag == '4':
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Добавить в корзину":
            # #??уточнить еще раз про amount, 2 клавы появляются тектовая с инфо, что в корзине, и с флагом 5 Управление корзиной...
            print(f"блюдо летит в добавить в корзину {temp_dish}")
            add_products_to_cart_row(user_id, temp_dish, 1)

    #флаг 5-клава управление корзиной...
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
            pass
        elif data == "Способ оплаты":
            pass
        elif data == "Оформить заказ":
            pass
    #если блюдо прилетело из меню по удалению блюд(нажали на блюдо в этом меню)
    elif flag == "6":
        #dish_for_delete = data
        print(f"Блюдо летит для удаления {data}")
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        #без расширения кнопок, нажали на блюдо значит оно на удаление
        else:
            #?надо ли функция по удалению по названию блюда из cart_row или норм со словарем
            for item in cart_:
                #lst_dish_cart.append(item[1])
                dict_del_dish[item[1]] = str(item[0])
            print(f"dict_del_dish {dict_del_dish}")
            del_cart_line(user_id, dict_del_dish.get[data])







print("Ready")

def func_run_teleg():
    bot.infinity_polling()

func_run_teleg()
