import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InputMediaPhoto
import json
#загрузит наш секретный токен из .env файла
#from dotenv import load_dotenv
#import os
#from os.path import join, dirname
from sql_main_things import get_category, get_products, add_user, add_products_to_cart_row, del_cart_line, get_cart_row, get_description_dish
#import gspread
#from google_dict_stat import stat_user, stat_cat, stat_shop, dict1, new_dict2, dict2

# def get_from_env(key):
#     dotenv_path = join(dirname(__file__), 'token.env')
#     load_dotenv(dotenv_path)
#     return os.environ.get(key)

with open('data.json', 'r', encoding='utf-8') as f: #открыли файл с данными
    text = json.load(f)
    #print(text)

#token = get_from_env('TG_BOT_TOKEN')
token = text.get('tg_token')
bot = telebot.TeleBot(token)


markupI_start = InlineKeyboardMarkup()
markupI_cat = InlineKeyboardMarkup()
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

#получаю категории из БД
categories = get_category()
lst_dishes = []
#блюдо сохраниться для добавления в корзину
temp_dish = ""
#клавиатура категорий по данным из БД
for x in categories:
    markupI_cat.add(InlineKeyboardButton(x, callback_data='2'+x))
markupI_cat.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        chat_id = message.chat.id
        print(f"chat_id {chat_id}")
        user_id = message.from_user.id
        print(f"chat_id {user_id}")
        try:
            add_user(None, message.user.id, 'Marina_1')
        except:
            pass
        bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markupI_start)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    user_id = call.from_user.id
    print(f"user_id {user_id}")
    bot.answer_callback_query(callback_query_id=call.id, )
    # print(call)
    id = call.message.chat.id
    flag = call.data[0]
    data = call.data[1:]
    # print(flag, data)
    global lst_dishes
    global temp_dish
    print(f"lst_dishes {lst_dishes}" )
    # удаление всех кнопок клавиатуры
    markupI_cat_val.keyboard.clear()
    if flag == "1":
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Корзина":
            print(get_cart_row(user_id))
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
            markupR_desc_dish.keyboard.clear()
            desc = get_description_dish(data)[0]
            desc_str = desc[0] + ": " + desc[1] + '. ' + "Стоимость: " + str(desc[2]) + '. ' + "Время: " + desc[3]
            markupR_desc_dish.add(KeyboardButton(desc_str))
            #bot.send_message(call.message.chat.id, "Описание блюда: ", reply_markup = markupR_desc_dish)
            bot.send_message(call.message.chat.id, desc_str, reply_markup=markupR_desc_dish)
            bot.send_photo(call.message.chat.id, photo=get_description_dish(data)[1])
            bot.send_message(call.message.chat.id, desc_str, reply_markup=markupI_add_card)
    elif flag == '4':
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Добавить в корзину":
            #??уточнить еще раз про amount
            print(f"блюдо летит в добавить в корзину {temp_dish}")
            add_products_to_cart_row(user_id, temp_dish, 1)




print("Ready")

def func_run_teleg():
    bot.infinity_polling()

func_run_teleg()
