import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

token = "6182506398:AAFQz06nOEpCeBLrJuK9LQ-D-OH8nhWtf7o"
bot = telebot.TeleBot(token)

# Клавиатура для администраторов
admin_markup = InlineKeyboardMarkup()
admin_markup.row(InlineKeyboardButton("Статусы заказов"), InlineKeyboardButton("Отзывы на заказы"),
                 InlineKeyboardButton("Отзывы на блюда"))

# Клавиатура для администраторов второго разряда
admin2_markup = InlineKeyboardMarkup()
admin2_markup.row(InlineKeyboardButton("Статусы заказов"), InlineKeyboardButton("Отзывы на заказы"),
                  InlineKeyboardButton("Отзывы на блюда"))
admin2_markup.row(InlineKeyboardButton("Управление администрацией"), InlineKeyboardButton("Управление меню блюд"))

# Клавиатура для управления администрацией
admin_control_markup = InlineKeyboardMarkup()
admin_control_markup.row(InlineKeyboardButton("Добавление"), InlineKeyboardButton("Изменение"),
                         InlineKeyboardButton("Удаление"))
admin_control_markup.row(InlineKeyboardButton("Назад"))


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
    if call.data == "Статусы заказов":
        bot.send_message(call.message.chat.id, "Информация о заказе",
                         reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton("Изменить статус"),
                                                                 InlineKeyboardButton("Назад")))
    elif call.data == "Отзывы на заказы" or call.data == "Отзывы на блюда":
        bot.send_message(call.message.chat.id, "Информация об отзыве (заказ, блюдо)",
                         reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton("Принять"),
                                                                 InlineKeyboardButton("Не принимать")))
    elif call.data == "Управление администрацией":
        bot.send_message(call.message.chat.id, "Выберите действие", reply_markup=admin_control_markup)


def check_admin_category(user_id):
    # Проверяем значение колонки category для пользователя в БД
    # Возвращаем 1 для администратора первого разряда
    # Возвращаем 2 для администратора второго разряда
    # Возвращаем 0 для обычного пользователя
    return 1


bot.polling()