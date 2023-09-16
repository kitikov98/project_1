import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

token = 'Твой токенок '
group_id = 'Твоя id группы вк'


vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

# Отправка месагев
def send_keyboard(user_id, text, keyboard):
    vk.messages.send(
        user_id=user_id,
        random_id=get_random_id(),
        message=text,
        keyboard=keyboard.get_keyboard()
    )

# ПОДкатегория
def create_subcategories_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Закуски", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Супы", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Блюда из мяса", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Блюда из рыбы и морепродуктов", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Паста и пицца", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Салаты", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Новая строка для следующих кнопок
    keyboard.add_button("Десерты", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Барбекю", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Новая строка для следующих кнопок
    keyboard.add_button("Рис и лапша", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Вегетарианские блюда", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Новая строка для следующих кнопок
    keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)  # Кнопка "Назад" к предыдущему меню
    return keyboard

# ГЛАВНОЕ меню
def create_main_menu_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Меню блюд", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Корзина", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Статистика заказов", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Статистика блюд", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Заказы", color=VkKeyboardColor.PRIMARY)
    return keyboard

# Обработочка
def main():
    longpoll = vk_api.longpoll.VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
            user_id = event.user_id
            message = event.text.lower()

            if message == "старт":
                keyboard = create_main_menu_keyboard()
                send_keyboard(user_id, "Выберите действие:", keyboard)

            elif message == "меню блюд":
                subcategories_keyboard = create_subcategories_keyboard()
                send_keyboard(user_id, "Выберите подкатегорию:", subcategories_keyboard)

if __name__ == "__main__":
    main()







# Работа не волк в лес не убежит

# import sqlite3
#
# def add_admin
#
# def remove_admin
#
# def update_admin
#
# def is_admin
#
#
# CREATE TABLE IF NOT EXISTS admins (
#     id INTEGER PRIMARY KEY,
#     tg_id INTEGER UNIQUE
# );