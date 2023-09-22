import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from sql_main_things import get_user_category, adm_get_ord, adm_change_order_status, adm_get_rating_ord, adm_get_ord_rewiew

token = "6119423257:AAHaggUuah3WlSRlp2cuNz5R0PQYYX1w8rM"
bot = telebot.TeleBot(token)

menu_1 = ["Статусы заказов", "Отзывы на заказы", "Отзывы на блюда", "Управление администрацией", "Управление меню блюд"]
menu_2 = ["Добавление", "Изменение", "Удаление", "Назад"]

# Клавиатура для администраторов
admin_markup = InlineKeyboardMarkup()
# Клавиатура для администраторов второго разряда
admin2_markup = InlineKeyboardMarkup()
# Клавиатура для управления администрацией
admin_control_markup = InlineKeyboardMarkup()

for x1 in menu_1:
    admin_markup.add(InlineKeyboardButton(x1, callback_data="A" + str(x1)))

# for x2 in menu_1:
#     admin2_markup.add(InlineKeyboardButton(x2, callback_data="B" + str(x2)))

for x3 in menu_2:
    admin_control_markup.add(InlineKeyboardButton(x3, callback_data="C" + str(x3)))



@bot.message_handler(commands=['start_admin_panel'])
def start_admin_panel(message):
    # Проводим проверку является ли пользователь администратором
    is_admin = check_admin_category(message.from_user.id)

    if is_admin != 0:
        bot.send_message(message.chat.id, "Панель администратора", reply_markup=admin_markup)
    # elif is_admin == 2:
    #     bot.send_message(message.chat.id, "Панель администратора второго разряда", reply_markup=admin2_markup)
    else:
        bot.reply_to(message, "У вас нет прав администратора")




@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    flag = call.data[0:1]
    data = call.data[1:]
    if flag == 'D':
        adm_change_order_status(data)
        bot.send_message(call.message.chat.id, 'status changed')
    elif flag =='A':
        if data == 'back':
            bot.send_message(call.message.chat.id, "Панель администратора первого разряда", reply_markup=admin_markup)
        elif data == "Статусы заказов":
            stat = InlineKeyboardMarkup()
            stat_list = adm_get_ord()
            if stat_list != []:
                for x4 in stat_list:
                    stat.add(InlineKeyboardButton(str(x4[1]), callback_data="D" + str(x4[0])))
                bot.send_message(call.message.chat.id, "Информация о заказе",
                                 reply_markup=stat)
            else:
                bot.send_message(call.message.chat.id, "Активных заказов нет, перезапустите панель администратора")
        elif data == "Отзывы на заказы":
            ord_review_menu = InlineKeyboardMarkup()
            ord_review_list = adm_get_rating_ord()
            for x5 in ord_review_list:
                ord_review_menu.add(InlineKeyboardButton('№ '+str(x5[0]), callback_data='E'+str(x5[0])))
            ord_review_menu.add(InlineKeyboardButton('back', callback_data='A'+'back'))
            bot.send_message(call.message.chat.id, 'Список отзывов заказов, ожидающих расмотрения',
                             reply_markup=ord_review_menu)
        elif data == "Управление администрацией":
            is_admin = check_admin_category(call.message.chat.id)
            if is_admin != 2:
                bot.answer_callback_query(callback_query_id=call.id, text='Вы не обладаете такими правами')
            else:
                pass





def check_admin_category(user_id):
    cat = get_user_category(user_id)
    return cat


bot.polling()