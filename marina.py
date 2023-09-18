import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InputMediaPhoto
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



token = get_from_env('TG_BOT_TOKEN')
bot = telebot.TeleBot(token)


markupI_start = InlineKeyboardMarkup()
markupI_cat = InlineKeyboardMarkup()
markupI_cat_val = InlineKeyboardMarkup([])
markupR_desc_dish = ReplyKeyboardMarkup(resize_keyboard=True)
lst_start = ["Меню категорий блюд", "Корзина", "Статистика заказов", "Статистика блюд", "Заказы"]
for y in lst_start:
    markupI_start.add(InlineKeyboardButton(y, callback_data='1'+y))

#получаю категории из БД
categories = get_category()
lst_dishes = []
# print(get_category())
# print(f"get_description_dish(data)[0] {get_description_dish('Борщ')[0]}")
# desc = get_description_dish('Борщ')[0]
# desc_str = "Название: " + desc[0] + ', ' + "Описание: " + desc[1] + ', ' + "Стоимость: "+ str(desc[2]) + ', ' + "Время доставки: " + desc[3]
# print(f"desc_str {desc_str}")
# print({type(desc_str)})



#клавиатура категорий по данным из БД
for x in categories:
    markupI_cat.add(InlineKeyboardButton(x, callback_data='2'+x))
markupI_cat.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markupI_start)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, )
    # print(call)
    id = call.message.chat.id
    flag = call.data[0]
    data = call.data[1:]
    # print(flag, data)
    global lst_dishes
    print(f"lst_dishes {lst_dishes}" )
    # удаление всех кнопок клавиатуры
    markupI_cat_val.keyboard.clear()
    if flag == "1":
        if data == "Меню категорий блюд":
            bot.send_message(call.message.chat.id, "Выберите категорию блюд", reply_markup=markupI_cat)
        elif data == "Корзина":
            pass
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
            #lst_dishes = dict1[data]
            #???может поменять название функции на get_description_dish
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
            #print(f"get_description_dish(data)[0]{'.'.join(get_description_dish(data)[0])}")
            markupR_desc_dish.keyboard.clear()
            desc = get_description_dish(data)[0]
            desc_str = desc[0] + ": " + desc[1] + '. ' + "Стоимость: " + str(
                desc[2]) + '. ' + "Время: " + desc[3]
            markupR_desc_dish.add(KeyboardButton(desc_str))
            bot.send_message(call.message.chat.id, "Описание блюда: ", reply_markup = markupR_desc_dish)

print("Ready")

def func_run_teleg():
    bot.infinity_polling()

func_run_teleg()
