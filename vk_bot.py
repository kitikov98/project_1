from vk_api import VkApi, VkUpload
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import math
from progekt_1_SQLLLL import Database

db = Database('db.sqlite')

text = ''
with open('data.json', 'r', encoding='utf-8') as f: #открыли файл с данными
    text = json.load(f)

GROUP_ID = text['vk_group']
GROUP_TOKEN = text['vk_token']
API_VERSION = '5.120'
CALLBACK_TYPES = ('show_snackbar', 'open_link', 'open_app', 'text')
menu_1 = db.get_category()
HI = ['start', "Start", "начать", "Начало", "Начать", "начало", "Бот", "бот", "Старт", "старт", "скидки", "Скидки",
      "Hi", "Hello", "hi", "hello", "привет", "Привет", "рш"]

text_inst = """
Привет-привет, я готов тебе помочь со скидками!
Нажми 'Запустить бота!' 
Если клавиатура свернута, нажми на 4 точки в правом нижнем углу!
1. Выберите нужную Вам  категорию, если не нашли на первой странице, нажмите : "далее"
Затем введите номер нужной услуги и отправьте сообщением боту. 
"""

# Запускаем бот
vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

settings = dict(one_time=False, inline=False)
settings2 = dict(one_time=False, inline=True)

# Основное меню
keyboard_1 = VkKeyboard(**settings)
keyboard_1.add_button(label='Меню блюд', color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
keyboard_1.add_line()
keyboard_1.add_button(label='Корзина', color=VkKeyboardColor.SECONDARY,
                      payload={"type": "cart"}
                      )
keyboard_1.add_line()
keyboard_1.add_button(label='Статистика заказов', color=VkKeyboardColor.SECONDARY,
                      payload={"type": "text"})
keyboard_1.add_line()
keyboard_1.add_button(label='Статистика блюд', color=VkKeyboardColor.NEGATIVE,
                      payload={"type": "text"})
keyboard_1.add_line()
keyboard_1.add_button(label='Заказы', color=VkKeyboardColor.PRIMARY,
                      payload={"type": "text"})

keyboard_menu_0 = VkKeyboard(**settings2)
keyboard_menu_0.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})


def menu_gener(list1, num1, num2, *str1):
    keyboard_menu = VkKeyboard(**settings2)
    max_amount = 5
    last_page = math.ceil(len(list1) / max_amount) - 1
    max_buttons = min((num1 + 1) * max_amount, len(list1))
    for x1 in range(max_amount * num1, max_buttons):
        keyboard_menu.add_button(label=list1[x1], color=VkKeyboardColor.SECONDARY, payload={"type": "text"})
        keyboard_menu.add_line()
    if last_page == 0:
        keyboard_menu.add_callback_button(label='Меню!', color=VkKeyboardColor.PRIMARY,
                                          payload={"type": 0, "menu": 1})
    else:
        if num1 == 0:
            keyboard_menu.add_callback_button(label='Далее', color=VkKeyboardColor.PRIMARY,
                                              payload={"type": str(num1 + 1), "menu": num2, 'label': str1})
        elif num1 == last_page:
            keyboard_menu.add_callback_button(label='Назад', color=VkKeyboardColor.PRIMARY,
                                              payload={"type": str(num1 - 1), "menu": num2, 'label': str1})
        else:
            keyboard_menu.add_callback_button(label='Назад', color=VkKeyboardColor.PRIMARY,
                                              payload={"type": str(num1 - 1), "menu": num2, 'label': str1})
            keyboard_menu.add_callback_button(label='Далее', color=VkKeyboardColor.PRIMARY,
                                              payload={"type": str(num1 + 1), "menu": num2, 'label': str1})
    return keyboard_menu


user_stat = ['Меню блюд', 'Корзина', 'Статистика заказов', 'Статистика блюд', 'Заказы', 'Изменить заказ',
             'Отменить заказ']


def discription(list1):
    text = f"""
Название: {list1[0]}
Соства блюда: {list1[1]}
Стоимость: {list1[2]}
Время приоготовления: {list1[3]}
"""
    return text


def make_or_list(user_id):
    list1 = db.get_cart_row(user_id)
    list2 = list1[0]
    list3 = []
    for item in list2:
        list3.append(f', item[2]]')
    return list3


menu_2 = []
for tuples in db.list_products():
    menu_2.append(tuples[0])


def vk_send_text(text, obj, keyboard=None):
    vk.messages.send(
            user_id=obj['from_id'],
            random_id=get_random_id(),
            peer_id=obj['from_id'],
            message=text,
            keyboard=keyboard.get_keyboard())


delivery = ['', 0]
product_rat = ['', '', 4]
ord_rating = [0, '', 4]

print("Ready vk_bot")


# print('s\np\na\ns\ni\nt\ne\n \nm\ne\nn\ny\na')

def vk_bot(category):
    global user_stat_ind, product, user_id, label_list, adress, type_payment, mark, review

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            try:
                db.add_user(event.obj.message['from_id'], None, '')
            except:
                pass
            if event.obj.message['text'] in HI:
                user_stat_ind = user_stat.index('Меню блюд')
                vk_send_text(text_inst, event.obj.message, keyboard_1)

            elif event.obj.message['text'] != '':
                if event.from_user:
                    if event.obj.message['text'] == 'Меню блюд' or event.obj.message['text'] == "Меню!":
                        user_stat_ind = user_stat.index(event.obj.message['text'])
                        vk_send_text('Выбирай категорию', event.obj.message, menu_gener(menu_1, 0, 1))
                    elif event.obj.message['text'] in user_stat:
                        user_stat_ind = user_stat.index(event.obj.message['text'])


                    else:
                        if event.obj.message['text'] in db.get_category():
                            if event.obj.message['text'] not in category.keys():
                                category.update({event.obj.message['text']: 1})
                            else:
                                category[event.obj.message['text']] += 1
                            vk_send_text('Выбирайте блюдо', event.obj.message,
                                    menu_gener(db.get_products(event.obj.message['text']), 0, 2,
                                               event.obj.message['text']))
                if user_stat_ind == 0:
                    global amount
                    if event.obj.message['text'].isdigit():
                        amount = event.obj.message['text']
                        print(event.obj.message['text'])
                        keyboard_menu = VkKeyboard(**settings2)
                        keyboard_menu.add_callback_button(label="Добавить в карзину", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'A', 'prod': product, 'amount': amount})
                        keyboard_menu.add_callback_button(label="Назад в категории", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 0, "menu": 1})
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f'Выбранное количество - {amount}',
                            keyboard=keyboard_menu.get_keyboard()
                        )

                    elif event.obj.message['text'] not in menu_1 and event.obj.message['text'] != 'Меню блюд':
                        keyboard_menu = VkKeyboard(**settings2)
                        keyboard_menu.add_callback_button(label="Назад в категории", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 0, "menu": 1})
                        product = event.obj.message['text']
                        image_bytes = db.get_description_dish(event.obj.message['text'])[2]
                        upload = VkUpload(vk_session)
                        photo = upload.photo_messages(photos=image_bytes)[0]

                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=discription(db.get_description_dish(event.obj.message['text'])[0]),
                            keyboard=keyboard_menu.get_keyboard(),
                            attachment=f"photo{photo['owner_id']}_{photo['id']}",
                        )
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message="Введите количество продукта"
                        )

                elif user_stat_ind == 1:
                    global list_of_dishes
                    if event.obj.message['text'] == 'Корзина':
                        cart_rows = db.get_cart_row(event.obj.message['from_id'])
                        total = cart_rows[1]
                        list_of_dishes = cart_rows[0]
                        label_list = []
                        for row in cart_rows[0]:
                            cart_row_label = row[1]
                            id_row = row[0]
                            amount = row[2]
                            label_list.append(f'{id_row}. {cart_row_label} - {amount}шт.')

                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Стоимость корзины: {total}р.\n"
                                    f"Выберите товар для удаления",
                            keyboard=menu_gener(label_list, 0, 3).get_keyboard()
                        )
                    elif event.obj.message['text'] != '':
                        row_id = event.obj.message['text'].split('.')[0]
                        label = event.obj.message['text'].split('.')[1]
                        label = label.split('-')[0]
                        amount = event.obj.message['text'].split('-')[1]
                        db.del_cart_line(user_id, row_id)
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f'Блюдо {label} в количестве {amount} удалено '
                        )

                elif user_stat_ind == 2:
                    if event.obj.message['text'] == 'Статистика заказов':
                        orders_list = db.get_to_rat_ord(user_id)
                        menu_orders = []
                        for order in orders_list:
                            if order is not None:
                                menu_orders.append(f'{order[0]}) {order[1][:16]}')
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Выберите заказ для отзыва",
                            keyboard=menu_gener(menu_orders, 0, 5).get_keyboard()
                        )
                    elif ')' in event.obj.message['text']:

                        print(event.obj.message['text'])
                        ord_rating[0] = event.obj.message['text'].split(')')[0]
                        keyboard_menu = VkKeyboard(**settings2)
                        keyboard_menu.add_callback_button(label="1", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'F', 'label': 1})
                        keyboard_menu.add_callback_button(label="2", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'F', 'label': 2})
                        keyboard_menu.add_callback_button(label="3", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'F', 'label': 3})
                        keyboard_menu.add_callback_button(label="4", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'F', 'label': 4})
                        keyboard_menu.add_callback_button(label="5", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'F', 'label': 5})
                        rating_ord = db.get_orders_rating()
                        if type(rating_ord) == str:
                            average_rat = rating_ord
                        else:
                            list_of_dish_rating = ''
                            for reviews in rating_ord[1]:
                                list_of_dish_rating += f'{reviews} \n'
                            average_rat = f'Средний рейтинг{rating_ord[0]}\n {list_of_dish_rating}'
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"{average_rat}\n Выбирайте отметку выбранному блюду",
                            keyboard=keyboard_menu.get_keyboard()
                        )
                    elif event.obj.message['text'] != '' and ord_rating[0] != 0:
                        ord_rating[1] = event.obj.message['text']
                        db.add_order_rating(user_id, ord_rating[0], ord_rating[1], ord_rating[2])
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Спасибо за ваш отзыв"
                        )

                elif user_stat_ind == 3:
                    if event.obj.message['text'] == 'Статистика блюд':
                        vk_send_text('Выбирай категорию', event.obj.message, menu_gener(menu_1, 0, 1))
                    elif event.obj.message['text'] in menu_2:
                        product_rat[0] = event.obj.message['text']
                        keyboard_menu = VkKeyboard(**settings2)
                        keyboard_menu.add_callback_button(label="1", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'E', 'label': 1})
                        keyboard_menu.add_callback_button(label="2", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'E', 'label': 2})
                        keyboard_menu.add_callback_button(label="3", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'E', 'label': 3})
                        keyboard_menu.add_callback_button(label="4", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'E', 'label': 4})
                        keyboard_menu.add_callback_button(label="5", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'E', 'label': 5})
                        rating_dish = db.get_product_rating(event.obj.message['text'])
                        if type(rating_dish) == str:
                            average_rat = rating_dish
                        else:
                            list_of_dish_rating = ''
                            for reviews in rating_dish[1]:
                                list_of_dish_rating += f'{reviews} \n'
                            average_rat = f'Средний рейтинг{rating_dish[0]}\n {list_of_dish_rating}'
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"{average_rat}\n Выбирайте отметку выбранному блюду",
                            keyboard=keyboard_menu.get_keyboard()
                        )
                    elif event.obj.message['text'] != '' and product_rat[0] != '':
                        product_rat[1] = event.obj.message['text']
                        db.add_product_rating(user_id, product_rat[0], product_rat[1], product_rat[2])
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Спасибо за ваш отзыв"
                        )
                elif user_stat_ind == 4:
                    keyboard_menu = VkKeyboard(**settings2)
                    keyboard_menu.add_callback_button(label="Выбор способа оплаты", color=VkKeyboardColor.PRIMARY,
                                                      payload={"type": 'B'})
                    keyboard_menu.add_line()
                    keyboard_menu.add_callback_button(label="Выбор адреса доставки", color=VkKeyboardColor.PRIMARY,
                                                      payload={"type": 'C'})
                    keyboard_menu.add_line()
                    keyboard_menu.add_callback_button(label="Оформить заказ", color=VkKeyboardColor.PRIMARY,
                                                      payload={"type": 'D', 'adress': delivery[0],
                                                               'type_payment': delivery[1]})
                    keyboard_menu.add_line()
                    keyboard_menu.add_button(label="Изменить заказ", color=VkKeyboardColor.PRIMARY,
                                             payload={"type": 'text'})
                    keyboard_menu.add_line()
                    keyboard_menu.add_button(label="Отменить заказ", color=VkKeyboardColor.PRIMARY,
                                             payload={"type": 'text'})

                    if event.obj.message['text'] == 'Карта':
                        delivery[1] = 1
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Способ оплаты выбран",
                            keyboard=keyboard_menu.get_keyboard()
                        )
                    elif event.obj.message['text'] == 'Наличность':
                        delivery[1] = 0
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Способ оплаты выбран",
                            keyboard=keyboard_menu.get_keyboard()
                        )

                    elif event.obj.message['text'] == 'Заказы':
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Order menu",
                            keyboard=keyboard_menu.get_keyboard()
                        )
                    elif event.obj.message['text'] != '':
                        delivery[0] = event.obj.message['text']
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Адресом доставки выбрано {event.obj.message['text']}"
                        )
                elif user_stat_ind == 5:
                    if event.obj.message['text'] == 'Изменить заказ':
                        orders_list = db.get_orders(user_id)
                        menu_orders = []
                        for order in orders_list:
                            if order is not None:
                                menu_orders.append(f'{order[0]}) {order[1][:16]}')
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Выберите заказ для изменения",
                            keyboard=menu_gener(menu_orders, 0, 4).get_keyboard()
                        )
                    elif event.obj.message['text'] != '':
                        order_id = event.obj.message['text'].split(')')[0]
                        date = event.obj.message['text'].split(')')[1]
                        db.change_order(user_id, order_id)
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f'Заказ на время: {date}; готов к редактированию. Пожалуйста, перейдите в корзину '
                        )
                elif user_stat_ind == 6:
                    if event.obj.message['text'] == 'Отменить заказ':
                        orders_list = db.get_orders(user_id)
                        menu_orders = []
                        for order in orders_list:
                            if order is not None:
                                menu_orders.append(f'{order[0]}) {order[1][:16]}')
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f"Выберите какой заказ хотите отменить",
                            keyboard=menu_gener(menu_orders, 0, 5).get_keyboard()
                        )
                    elif event.obj.message['text'] != '':
                        order_id = event.obj.message['text'].split(')')[0]
                        date = event.obj.message['text'].split(')')[1]
                        db.cancel_order(order_id)
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            conversation_message_id=event.obj.message['from_id'],
                            message=f'Заказ на время: {date}; отменен. '
                        )

        elif event.type == VkBotEventType.MESSAGE_EVENT:
            if event.object.payload.get('type') in CALLBACK_TYPES:
                print(event.object.payload.get('type'))
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=event.object.user_id,
                    peer_id=event.object.peer_id,
                    event_data=json.dumps(event.object.payload))

            elif event.object.payload.get('type') == 'A':
                product = event.object.payload.get('prod')
                pr_amount = event.object.payload.get('amount')
                keyboard_menu = VkKeyboard(**settings2)
                keyboard_menu.add_callback_button(label="Назад в категории", color=VkKeyboardColor.PRIMARY,
                                                  payload={"type": 0, "menu": 1})
                db.add_products_to_cart_row(user_id, product, pr_amount)
                vk.messages.send(
                    random_id=get_random_id(),
                    peer_id=event.obj.peer_id,
                    conversation_message_id=event.obj.conversation_message_id,
                    message='Успешно добавлено в корзину',
                    keyboard=keyboard_menu.get_keyboard()
                )
            elif event.object.payload.get('type') == 'B':
                keyboard_menu = VkKeyboard(**settings2)
                keyboard_menu.add_button(label="Карта", color=VkKeyboardColor.SECONDARY,
                                         payload={"type": 'text'})
                keyboard_menu.add_line()
                keyboard_menu.add_button(label="Наличность", color=VkKeyboardColor.SECONDARY,
                                         payload={"type": 'text'})
                vk.messages.send(
                    random_id=get_random_id(),
                    peer_id=event.obj.peer_id,
                    conversation_message_id=event.obj.conversation_message_id,
                    message='способы оплаты',
                    keyboard=keyboard_menu.get_keyboard()
                )

            elif event.object.payload.get('type') == 'C':
                vk.messages.send(
                    random_id=get_random_id(),
                    peer_id=event.obj.peer_id,
                    conversation_message_id=event.obj.conversation_message_id,
                    message='Введите адрес доставки'
                )
            elif event.object.payload.get('type') == 'D':
                if event.object.payload.get('adress') == '':
                    vk.messages.send(
                        random_id=get_random_id(),
                        peer_id=event.obj.peer_id,
                        conversation_message_id=event.obj.conversation_message_id,
                        message='Заполните адрес доставки и способ оплаты'
                    )
                else:
                    db.add_delivery(user_id, delivery)
                    db.add_to_order(user_id)
                    vk.messages.send(
                        random_id=get_random_id(),
                        peer_id=event.obj.peer_id,
                        conversation_message_id=event.obj.conversation_message_id,
                        message='Заказ принят'
                    )
            elif event.object.payload.get('type') == 'E':
                mark = event.object.payload.get('label')
                product_rat[2] = mark
                vk.messages.send(
                    random_id=get_random_id(),
                    peer_id=event.obj.peer_id,
                    conversation_message_id=event.obj.conversation_message_id,
                    message='Ваша отметка принята, напишите пожалуйста отзыв'
                )

            elif event.object.payload.get('type') == 'F':
                mark = event.object.payload.get('label')
                ord_rating[2] = mark
                vk.messages.send(
                    random_id=get_random_id(),
                    peer_id=event.obj.peer_id,
                    conversation_message_id=event.obj.conversation_message_id,
                    message='Ваша отметка принята, напишите пожалуйста отзыв'
                )

            elif event.object.payload.get('menu') == 1:
                name = event.object.payload.get('label')
                num1 = int(event.object.payload.get('type'))
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Выбирай категорию',
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=menu_gener(menu_1, num1, 1, name).get_keyboard())

            elif event.object.payload.get('menu') == 3:
                num1 = int(event.object.payload.get('type'))
                total = db.get_cart_row(user_id)[1]
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message=f"Стоимость корзины: {total}р.\n"
                            f"Выберите товар для удаления",
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=menu_gener(label_list, num1, 3).get_keyboard())

            elif event.object.payload.get('menu') == 4:
                num1 = int(event.object.payload.get('type'))
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message=f"Выберите закз для изменени",
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=menu_gener(label_list, num1, 4).get_keyboard())

            elif event.object.payload.get('menu') == 5:
                num1 = int(event.object.payload.get('type'))
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message=f"Выберите закз для изменени",
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=menu_gener(label_list, num1, 5).get_keyboard())

            else:
                name = event.object.payload.get('label')[0]
                num1 = int(event.object.payload.get('type'))
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message='Выбирай блюдо',
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=menu_gener(db.get_products(name), num1, 2, name).get_keyboard())


if __name__ == '__main__':
    print()
    category = {}
    vk_bot(category)
