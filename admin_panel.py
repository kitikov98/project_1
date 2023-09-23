import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from sql_main_things import (get_user_category, adm_get_ord, adm_change_order_status, adm_get_rating_ord,
                             adm_get_ord_rewiew, adm_accept_stat_ord, adm_refuse_stat_ord, adm_get_rating_prod,
                             adm_get_prod_rewiew, adm_accept_stat_prod, adm_refuse_stat_prod,adm_get_products_status,
                             adm_stop_prod, adm_unstop_prod, adm_change_to_second_rank, add_user, adm_change_to_first_rank)

token = "6119423257:AAHaggUuah3WlSRlp2cuNz5R0PQYYX1w8rM"
bot = telebot.TeleBot(token)

menu_1 = ["Статусы заказов", "Отзывы на заказы", "Отзывы на блюда", "Управление администрацией", "Управление меню блюд"]
menu_2 = ["Добавление", "Изменение", "Удаление", "Назад"]

# Клавиатура для администраторов
admin_markup = InlineKeyboardMarkup()


for x1 in menu_1:
    admin_markup.add(InlineKeyboardButton(x1, callback_data="A" + str(x1)))


def check_admin_category(user_id):
    cat = get_user_category(user_id)
    return cat


@bot.message_handler(commands=['start_admin_panel'])
def start_admin_panel(message):
    # Проводим проверку является ли пользователь администратором
    is_admin = check_admin_category(message.from_user.id)

    if is_admin != 0:
        bot.send_message(message.chat.id, "Панель администратора", reply_markup=admin_markup)
    else:
        bot.reply_to(message, "У вас нет прав администратора")


@bot.message_handler(commands=['Это_Казахстан?'])
def secret_panel(message):
    adm_change_to_second_rank(message.from_user.id)
    bot.reply_to(message, "Казахстан, да")


@bot.message_handler(commands=['init_admin'])
def init_new_admin(message):
    msg = bot.send_message(message.chat.id, 'Введите id пользователя')
    bot.register_next_step_handler(msg, create_adm)


def create_adm(message):
    print(message.text)
    try:
        add_user(None, int(message.text), None)
        adm_change_to_first_rank(int(message.text))
        bot.send_message(message.chat.id, 'красаучык')
    except:
        bot.send_message(message.chat.id, "Некоректные данные id")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    flag = call.data[0:1]
    data = call.data[1:]
    if flag =='A':
        if data == 'back':
            bot.edit_message_text("Панель администратора", call.message.chat.id,
                                  call.message.message_id, reply_markup=admin_markup)

        elif data == "Статусы заказов":
            stat = InlineKeyboardMarkup()
            stat_list = adm_get_ord()
            if stat_list != []:
                for x4 in stat_list:
                    stat.add(InlineKeyboardButton(str(x4[1]), callback_data="D" + str(x4[0])))
                stat.add(InlineKeyboardButton('back', callback_data='Aback'))
                bot.edit_message_text("Информация о заказе", call.message.chat.id,
                                      call.message.message_id, reply_markup=stat)
            else:
                stat.add(InlineKeyboardButton('back', callback_data='Aback'))
                bot.edit_message_text("Активных заказов нет", call.message.chat.id,
                                      call.message.message_id, reply_markup=stat)

        elif data == "Отзывы на заказы":
            ord_review_menu = InlineKeyboardMarkup()
            ord_review_list = adm_get_rating_ord()
            for x5 in ord_review_list:
                ord_review_menu.add(InlineKeyboardButton('№ '+str(x5[0]), callback_data='E'+str(x5[0])))
            ord_review_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Список отзывов заказов, ожидающих расмотрения', call.message.chat.id,
                                  call.message.message_id, reply_markup=ord_review_menu)

        elif data == "Отзывы на блюда":
            prod_review_menu = InlineKeyboardMarkup()
            prod_review_list = adm_get_rating_prod()
            for x5 in prod_review_list:
                prod_review_menu.add(InlineKeyboardButton('№ '+str(x5[0]), callback_data='F'+str(x5[0])))
            prod_review_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Список отзывов на блюда, ожидающих расмотрения', call.message.chat.id,
                                  call.message.message_id, reply_markup=prod_review_menu)

        elif data == "Управление администрацией":
            is_admin = check_admin_category(call.message.chat.id)
            if is_admin != 2:
                bot.answer_callback_query(callback_query_id=call.id, text='Вы не обладаете такими правами')
            else:
                pass

        elif data == "Управление меню блюд":
            is_admin = check_admin_category(call.message.chat.id)
            if is_admin != 2:
                bot.answer_callback_query(callback_query_id=call.id, text='Вы не обладаете такими правами')
            else:
                list_pr_st = adm_get_products_status()
                prod_menu = InlineKeyboardMarkup()
                for x6 in list_pr_st:
                    prod_menu.add(InlineKeyboardButton(str(x6[0])+' - status: '+str(x6[1]),
                                                       callback_data='H'+x6[0]+str(x6[1])))
                prod_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
                bot.edit_message_text('меню продуктов', call.message.chat.id,
                                      call.message.message_id, reply_markup=prod_menu)

    elif flag == 'D':
        d_menu = InlineKeyboardMarkup()
        d_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
        adm_change_order_status(data)
        bot.edit_message_text('status changed', call.message.chat.id, call.message.message_id, reply_markup=d_menu)

    elif flag == 'E':
        list1 = adm_get_ord_rewiew(data)
        ord_rat_menu = InlineKeyboardMarkup()
        ord_rat_menu.add(InlineKeyboardButton('принять', callback_data='B'+str(data)+'accept'),
                         InlineKeyboardButton('отклонить', callback_data='B'+str(data)+'refuse'))
        ord_rat_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
        bot.edit_message_text('Отметка ☆: '+str(list1[0])+'\n'+'Отзыв: '+str(list1[1]),
                              call.message.chat.id, call.message.message_id, reply_markup=ord_rat_menu)

    elif flag == 'F':
        list1 = adm_get_prod_rewiew(data)
        ord_rat_menu = InlineKeyboardMarkup()
        ord_rat_menu.add(InlineKeyboardButton('принять', callback_data='G'+str(data)+'accept'),
                         InlineKeyboardButton('отклонить', callback_data='G'+str(data)+'refuse'))
        ord_rat_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
        bot.edit_message_text('Отметка ☆: '+str(list1[0])+'\n'+'Отзыв: '+str(list1[1]),
                              call.message.chat.id, call.message.message_id, reply_markup=ord_rat_menu)

    elif flag == 'B':
        b_menu = InlineKeyboardMarkup()
        if data[-6:] == 'accept':
            order_id = data.replace('accept', '')
            adm_accept_stat_ord(int(order_id))
            b_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отзыв принят', call.message.chat.id, call.message.message_id, reply_markup=b_menu)
        elif data[-6:] == 'refuse':
            order_id = data.replace('refuse', '')
            adm_refuse_stat_ord(int(order_id))
            b_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отзыв отклонен', call.message.chat.id, call.message.message_id, reply_markup=b_menu)

    elif flag == 'G':
        f_menu = InlineKeyboardMarkup()
        if data[-6:] == 'accept':
            order_id = data.replace('accept', '')
            adm_accept_stat_prod(int(order_id))
            f_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отзыв принят', call.message.chat.id, call.message.message_id, reply_markup=f_menu)
        elif data[-6:] == 'refuse':
            order_id = data.replace('refuse', '')
            adm_refuse_stat_prod(int(order_id))
            f_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отзыв отклонен', call.message.chat.id,call.message.message_id, reply_markup=f_menu)

    elif flag =='H':
        if data[-1:] == "1":
            product = data.replace('1','')
            adm_stop_prod(product)
            bot.answer_callback_query(callback_query_id=call.id, text=f'Статус {product} изменен')
            list_pr_st = adm_get_products_status()
            prod_menu = InlineKeyboardMarkup()
            for x6 in list_pr_st:
                prod_menu.add(InlineKeyboardButton(str(x6[0]) + ' - status: ' + str(x6[1]),
                                                   callback_data='H' + x6[0] + str(x6[1])))
            prod_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('меню продуктов', call.message.chat.id,
                                  call.message.message_id, reply_markup=prod_menu)
        elif data[-1:] == "0":
            product = data.replace('0','')
            adm_unstop_prod(product)
            bot.answer_callback_query(callback_query_id=call.id, text=f'Статус {product} изменен')
            list_pr_st = adm_get_products_status()
            prod_menu = InlineKeyboardMarkup()
            for x6 in list_pr_st:
                prod_menu.add(InlineKeyboardButton(str(x6[0]) + ' - status: ' + str(x6[1]),
                                                   callback_data='H' + x6[0] + str(x6[1])))
            prod_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('меню продуктов', call.message.chat.id,
                                  call.message.message_id, reply_markup=prod_menu)


bot.polling()