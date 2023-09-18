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
from sql_main_things import get_category, get_products, add_user, add_products_to_cart_row, del_cart_line, get_cart_row, get_product
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
#markupR_desc = ReplyKeyboardMarkup(resize_keyboard=True)
lst_start = ["Меню категорий блюд", "Корзина", "Статистика заказов", "Статистика блюд", "Заказы"]
for y in lst_start:
    markupI_start.add(InlineKeyboardButton(y, callback_data='1'+y))

#получаю категории из БД
categories = get_category()
# print(get_category())
# print(get_products('Десерты'))
#print(get_product("Борщ")) #(('Борщ', 'Говядина, картофель, лук, марковь, свекла, капуста, чеснок, томатная паста, уксус, лавровый лист ', 12.0, '55:00'), <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=2500x1250 at 0x1A69F6D1630>)
# dict1 = {"Закуски": ["брускетты", "сырные тарелки", "суши и роллы"],
#          "Супы": ["борщ", "грибной суп", "томатный суп с морепродуктами"],
# "Блюда из мяса": ["стейки", "жаркое", "котлеты", "пельмени"],
# "Блюда из рыбы и морепродуктов": ["запеченный лосось", "креветки в сливочном соусе", "кальмары на гриле"],
# "Паста и пицца": ["спагетти болоньезе", "пенне аррабьята", "маргарита пицца", "пицца с морепродуктами"],
# "Салаты": ["цезарь", "греческий", "тунец с картофельным пюре"],
# "Десерты": ["тирамису", "панакотта", "шоколадный фондан"],
# "Барбекю": ["ассорти гриля", "шашлык из свинины", "куриные крылья с барбекю-глазурью"],
# "Рис и лапша": ["паэлья", "кунг пао", "лапша с куриной грудкой"],
# "Вегетарианские блюда": ["овощной гриль", "рататуй", "овощное карри"]
#          }
# dict_description = {"брускетты": "Название: брускетты. Состав: тостовый хлеб, помидоры, базилик, оливковое масло, сыр пармезан.Стоимость: 5 BYN",
#                     "cырные тарелки": "Название: сырные тарелки. Состав: cыр гауда, грецкие орехи, мед, сухофрукты. Стоимость: 12 BYN",
#                     "суши и роллы": "Название: суши и роллы. Состав: рис, нори, рыба, овощи, соевый соус. Стоимость: 11 BYN",
# "борщ": "Состав: свекла, картофель, морковь, капуста, мясо, лук. Стоимость: 7 BYN",
# "грибной суп": "Состав: грибы, картофель, лук, зелень, сливки. Стоимость: 6 BYN",
#  }
#клавиатура категорий по данным из БД
for x in categories:
    markupI_cat.add(InlineKeyboardButton(x, callback_data='2'+x))
markupI_cat.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))

# #клавиатура категорий
# for x in dict1.keys():
#     markupI_cat.add(InlineKeyboardButton(x, callback_data='2'+x))
# markupI_cat.add(InlineKeyboardButton("Назад в главное меню", callback_data='1'+"Назад в главное меню"))

# #сделаю категории одним списком
# categories = []
# for key_ in dict1.keys():
#     categories.append(key_)
#print(categories)
#сделаю блюда одним списком
# dishes = []
# for value_ in dict1.values():
#     dishes += value_
# #print(dishes)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markupI_start)
    # elif message.text in dishes:
    #     pass


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, )
    #print(call)
    id = call.message.chat.id
    flag = call.data[0]
    data = call.data[1:]
    #print(flag, data)
    #print(dict2)
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
            lst_dishes = get_products(data)
            for dish_ in lst_dishes:
                markupI_cat_val.add(InlineKeyboardButton(dish_, callback_data='3' + dish_))
            markupI_cat_val.add(
                InlineKeyboardButton("Назад в меню категорий блюд", callback_data='1' + "Меню категорий блюд"))
            markupI_cat_val.add(
                InlineKeyboardButton("Назад в главное меню", callback_data='1' + "Назад в главное меню"))
            bot.send_message(call.message.chat.id, "Выберите блюдо!",
                             reply_markup=markupI_cat_val)

print("Ready")

def func_run_teleg():
    bot.infinity_polling()

func_run_teleg()
