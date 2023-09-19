import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


token = ''
group_id = ''


vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()


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

# Корзина пользователя
user_cart = {}

# Информация о заказе пользователя
user_order_info = {
    "address": "",
    "delivery_time": "",
    "payment_method": "",
}


# Отправка сообщения с клавой
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


# Выбрать из подкатегории и обратно
def handle_subcategory(user_id, subcategory):
    if subcategory in menu_by_subcategory:
        keyboard = create_subcategories_keyboard(subcategory)
        send_keyboard(user_id, f"{subcategory}:", keyboard)
        user_states[user_id] = "subcategory"
    elif subcategory == "Назад в главное меню":
        handle_main_menu(user_id)
    else:
        handle_main_menu(user_id)


#  добавление блюда в корзину пользователя
def add_to_cart(user_id, item):
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append(item)


#  обработка выбора блюда из подкатегории
def handle_dish_selection(user_id, dish):
    add_to_cart(user_id, dish)
    send_keyboard(user_id, f"{dish} добавлено в корзину.", create_subcategories_keyboard(user_states[user_id]))


# Обработка гл меню
def handle_main_menu(user_id):
    keyboard = create_main_menu_keyboard()
    send_keyboard(user_id, "Выберите действие:", keyboard)
    user_states[user_id] = "main_menu"  # Устанавливаем состояние "главное меню"


#  Обработка заказов
def handle_orders(user_id):
    current_order = user_cart.get(user_id, [])
    order_total_cost = calculate_total_cost(current_order)

    if not current_order:
        send_keyboard(user_id, "Ваша корзина пуста.", create_main_menu_keyboard())
    else:
        order_text = "Ваш текущий заказ:\n"
        for item in current_order:
            order_text += f"- {item}\n"

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Управление корзиной", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Адрес доставки", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Время доставки", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Способ оплаты", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Итоговая стоимость", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Оформить заказ", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
        send_keyboard(user_id, order_text, keyboard)


# Функция для расчета итоговой стоимости заказа
def calculate_total_cost(order):
    # Здесь должна быть функция для расчета
    return len(order)


# Оплата
def handle_payment_method(user_id, method):
    if method in ["Карта", "Наличность"]:
        user_order_info["payment_method"] = method
        send_keyboard(user_id, f"Способ оплаты выбран: {method}", create_orders_keyboard())
    elif method == "Назад":
        handle_orders(user_id)
    else:
        send_keyboard(user_id, "Выберите способ оплаты:", create_payment_methods_keyboard())


#  создание клавиатуры с кнопками способов оплаты
def create_payment_methods_keyboard():
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
                handle_main_menu(user_id)

            elif message == "меню блюд" and user_id not in user_states:
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


if __name__ == "__main__":
    main()
