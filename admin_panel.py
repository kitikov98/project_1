import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from sql_main_things import get_user_category

token = "6119423257:AAHaggUuah3WlSRlp2cuNz5R0PQYYX1w8rM"
bot = telebot.TeleBot(token)

menu_1 = ["Статусы заказов","Отзывы на заказы", "Отзывы на блюда", "Управление администрацией", "Управление меню блюд"]
menu_2 = ["Добавление", "Изменение", "Удаление", "Назад"]

# Клавиатура для администраторов
admin_markup = InlineKeyboardMarkup()
# Клавиатура для администраторов второго разряда
admin2_markup = InlineKeyboardMarkup()
# Клавиатура для управления администрацией
admin_control_markup = InlineKeyboardMarkup()

for x1 in menu_1[:3]:
    admin_markup.add(InlineKeyboardButton(x1, callback_data="A" + str(x1)))

for x2 in menu_1:
    admin2_markup.add(InlineKeyboardButton(x2, callback_data="B" + str(x2)))

for x3 in menu_2:
    admin_control_markup.add(InlineKeyboardButton(x3, callback_data="B" + str(x3)))



@bot.message_handler(commands=['start_admin_panel'])
def start_admin_panel(message):
    # Проводим проверку является ли пользователь администратором
    is_admin = check_admin_category(message.from_user.id)

    if is_admin == 1:
        bot.send_message(message.chat.id, "Панель администратора первого разряда", reply_markup=admin_markup)
    elif is_admin == 2:
        bot.send_message(message.chat.id, "Панель администратора второго разряда", reply_markup=admin2_markup)
    else:
        bot.reply_to(message, "У вас нет прав администратора")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    flag = call.data[0:1]
    data = call.data[1:]
    if data == "Статусы заказов":
        bot.send_message(call.message.chat.id, "Информация о заказе",
                         reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton("Изменить статус"),
                                                                 InlineKeyboardButton("Назад")))
    # elif call.data == "Отзывы на заказы" or call.data == "Отзывы на блюда":
    #     bot.send_message(call.message.chat.id, "Информация об отзыве (заказ, блюдо)",
    #                      reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton("Принять"),
    #                                                              InlineKeyboardButton("Не принимать")))
    # elif call.data == "Управление администрацией":
    #     bot.send_message(call.message.chat.id, "Выберите действие", reply_markup=admin_control_markup)


def check_admin_category(user_id):
    cat = get_user_category(user_id)
    return cat


bot.polling()