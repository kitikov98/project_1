import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from sql_main_things import get_category, get_products, get_cart_row, get_cart_id, add_user, add_products_to_cart_row, add_to_order, get_orders, get_description_dish, get_orders_rating, get_product_rating, change_order,cancel_order, add_order_rating, add_product_rating
# импортировал все функции для работы с БД

token = ''
group_id = ''


vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

# get_category() - выдаст тебе список категорий
# get_products(category) - выдаст тебе продукты из категории category
menu_by_subcategory = {
    "Закуски": ["Брускетты", "Сырные тарелки", "Суши и роллы"],
    "Супы": ["Борщ", "Грибной суп", "Томатный суп с морепродуктами"],
    "Блюда из мяса": ["Стейки", "Жаркое", "Котлеты", "Пельмени"],
    "Блюда из рыбы и морепродуктов": ["Запеченный лосось", "Креветки в сливочном соусе", "Кальмары на гриле"],
    "Паста и пицца": ["Спагетти болоньезе", "Пенне аррабьята", "Маргарита пицца", "Пицца с морепродуктами"],
    "Салаты": ["Цезарь", "Греческий", "Тунец с картофельным пюре"],
    "Десерты": ["Тирамису", "Панакотта", "Шоколадный фондан"],
    "Барбекю": ["Ассорти гриля", "Шашлык из свинины", "Куриные крылья с барбекю-глазурью"],
    "Рис и лапша": ["Паэлья", "Кунг Пао", "Лапша с куриной грудкой"],
    "Вегетарианские блюда": ["Овощной гриль", "Рататуй", "Овощное карри"]
}

user_states = {}

user_cart = {}

user_order_info = {
    "address": "",
    "delivery_time": "",
    "payment_method": "",
}

stop_list = set()


def send_keyboard(user_id, text, keyboard):
    vk.messages.send(
        user_id=user_id,
        random_id=get_random_id(),
        message=text,
        keyboard=keyboard.get_keyboard()
    )


def create_main_menu_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Меню блюд", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Корзина", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Статистика заказов", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Статистика блюд", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Заказы", color=VkKeyboardColor.PRIMARY)
    return keyboard


def create_subcategories_keyboard(subcategory):
    keyboard = VkKeyboard(one_time=True)
    for item in menu_by_subcategory.get(subcategory, []):
        keyboard.add_button(item, color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Назад в главное меню", color=VkKeyboardColor.SECONDARY)
    return keyboard


def handle_subcategory(user_id, subcategory):
    if subcategory in menu_by_subcategory:
        keyboard = create_subcategories_keyboard(subcategory)
        send_keyboard(user_id, f"{subcategory}:", keyboard)
        user_states[user_id] = "subcategory"
    elif subcategory == "Назад в главное меню":
        handle_main_menu(user_id)
    else:
        #
        handle_main_menu(user_id)


def add_to_cart(user_id, item):
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append(item)


def handle_dish_selection(user_id, dish):
    add_to_cart(user_id, dish)
    send_keyboard(user_id, f"{dish} добавлено в корзину.", create_subcategories_keyboard(user_states[user_id]))


def handle_main_menu(user_id):
    keyboard = create_main_menu_keyboard()
    send_keyboard(user_id, "Выберите действие:", keyboard)
    user_states[user_id] = "main_menu"


def handle_orders(user_id):
    # get_cart_row(user_id) выдаст тебе все записи из корзины и сумму всей корзины (список из списков строк корзины, сумма корзины)
    current_order = user_cart.get(user_id, [])
    order_total_cost = calculate_total_cost(current_order)

    if not current_order:
        send_keyboard(user_id, "Ваша корзина пуста.", create_main_menu_keyboard())
    else:
        order_text = "Ваш текущий заказ:\n"
        for item in current_order:
            order_text += f"- {item}\n"

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Управление корзиной", color=VkKeyboardColor.PRIMARY) # в миро поменялось посмотри как должно меню выглядеть
        keyboard.add_button("Адрес доставки", color=VkKeyboardColor.PRIMARY) # его в список для функции add_order
        keyboard.add_button("Время доставки", color=VkKeyboardColor.PRIMARY)  # можешь убирать этот пункт, т.к. будет считаться автоматически
        keyboard.add_button("Способ оплаты", color=VkKeyboardColor.PRIMARY) # его в список для add_order
        keyboard.add_button("Итоговая стоимость", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Оформить заказ", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
        send_keyboard(user_id, order_text, keyboard)


# Функция для расчета итоговой стоимости заказа
def calculate_total_cost(order):
    # get_cart_row(user_id) здесь вызовешь для просмотра итоговой стоимости корзины заказа
    return len(order)


#
def handle_payment_method(user_id, method):
    if method in ["Карта", "Наличность"]:
        #  сохраняй в определенный списко наличность или карта под значением 0 или 1, подробнее в функции add_order() - чему равна наличность, чему карта
        user_order_info["payment_method"] = method
        send_keyboard(user_id, f"Способ оплаты выбран: {method}", create_orders_keyboard())
    elif method == "Назад":
        handle_orders(user_id)
    else:
        send_keyboard(user_id, "Выберите способ оплаты:", create_payment_methods_keyboard())


#
def create_payment_methods_keyboard():
    #  сохраняй в определенный списко наличность или карта под значением 0 или 1, подробнее в функции add_order() - чему равна наличность, чему карта
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Карта", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Наличность", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def main():
    longpoll = VkBotLongPoll(vk_session, group_id)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.object.message.from_id
            message = event.object.message.text.lower()

            if message == "старт":
                # add_user - функция сохранит пользователя в БД, создаст для него корзину и прочее
                handle_main_menu(user_id)

            elif message == "меню блюд" and user_id not in user_states:
                # посмотри старый файл бота, там как раз то меню, что надо - inlne
                keyboard = create_subcategories_keyboard("Закуски")
                send_keyboard(user_id, "Выберите подкатегорию:", keyboard)
                user_states[user_id] = "subcategory"

            elif message in menu_by_subcategory.keys() and user_id in user_states:
                if user_states[user_id] == "subcategory":
                    handle_dish_selection(user_id, message)
                elif user_states[user_id] == "main_menu":

                    pass

            elif message == "назад" and user_id in user_states:
                if user_states[user_id] == "subcategory":
                    handle_main_menu(user_id)
                elif user_states[user_id] == "main_menu":

                    pass

            elif message == "корзина":
                handle_orders(user_id)

            elif message == "способ оплаты" and "payment_method" not in user_order_info:
                send_keyboard(user_id, "Выберите способ оплаты:", create_payment_methods_keyboard())

            elif "payment_method" not in user_order_info:
                handle_payment_method(user_id, message)

            elif message == "список товаров в корзине":
                handle_stop_list(user_id)


# функция для обработки списка товаров на стопе
def handle_stop_list(user_id):
    # это можешь не делать, т.к одмен будет в телеграме менять состояние стопа продуктов
    if user_id in user_cart and user_cart[user_id]:
        stop_list_text = "Список товаров на стопе:\n"
        for item in stop_list:
            stop_list_text += f"- {item}\n"

        keyboard = VkKeyboard(one_time=True)
        for item in user_cart[user_id]:
            keyboard.add_button(f"Убрать {item} со стопа", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Назад в корзину", color=VkKeyboardColor.SECONDARY)
        send_keyboard(user_id, stop_list_text, keyboard)
    else:
        send_keyboard(user_id, "Ваша корзина пуста.", create_main_menu_keyboard())


if __name__ == "__main__":
    main()

    # def send_dish_photo(user_id, photo_path):
    #     try:
    #         # zagruzka photo
    #         photo = upload.photo_messages(photo_path)
    #
    #         owner_id = photo[0]['owner_id']
    #         photo_id = photo[0]['id']
    #         access_key = photo[0]['access_key']
    #
    #         attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    #
    #         #otpravka
    #         vk.messages.send(
    #             user_id=user_id,
    #             random_id=get_random_id(),
    #             attachment=attachment
    #         )
    #     except Exception as e:
    #         print(f"Ошибка при отправке фотографии: {e}")
# kak to tak vot