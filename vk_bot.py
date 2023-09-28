from vk_api import VkApi, VkUpload
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import math
from progekt_1_SQL import Database

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


def rating_keyboard(flag):
    keyboard_r = VkKeyboard(**settings2)
    for x in range(1,6):
        keyboard_r.add_callback_button(label=str(x), color=VkKeyboardColor.PRIMARY, payload={"type": flag, 'label': x})
    return keyboard_r


def discription(list1):
    text = f"""
Название: {list1[0]}
Соства блюда: {list1[1]}
Стоимость: {list1[2]}
Время приоготовления: {list1[3]}
"""
    return text


menu_2 = []
for tuples in db.list_products():
    menu_2.append(tuples[0])


def vk_send_text(idvk, texts, keyboard=None, attachment=None):
    vk.messages.send(
        user_id=idvk,
        random_id=get_random_id(),
        peer_id=idvk,
        message=texts,
        keyboard=keyboard,
        attachment=attachment
    )


def vk_edit_message(peerid, texts, cmid, keyboard=None):
    vk.messages.edit(
        peer_id=peerid,
        message=texts,
        conversation_message_id=cmid,
        keyboard=keyboard
    )


print("Ready vk_bot")
# print('s\np\na\ns\ni\nt\ne\n \nm\ne\nn\ny\na')

def vk_bot():
    global user_stat_ind,  label_list
    products = {'product': None, 'amount': None}
    user_delivery = {'adress': None, 'type_payment': None}
    product_rat = {'product': None, 'review': None, 'mark': None}
    ord_rating = {'order_id': None, 'review': None, 'mark': None}
    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                db.add_user(event.obj.message['from_id'], None, '')
            except:
                pass
            if event.obj.message['text'] in HI:
                user_stat_ind = user_stat.index('Меню блюд')
                vk_send_text(event.obj.message['from_id'], text_inst,  keyboard_1.get_keyboard())

            elif event.obj.message['text'] != '':
                if event.from_user:
                    if event.obj.message['text'] == 'Меню блюд' or event.obj.message['text'] == "Меню!":
                        user_stat_ind = user_stat.index(event.obj.message['text'])
                        vk_send_text(event.obj.message['from_id'], 'Выбирай категорию', menu_gener(menu_1, 0, 1).get_keyboard())
                    elif event.obj.message['text'] in user_stat:
                        user_stat_ind = user_stat.index(event.obj.message['text'])

                    elif event.obj.message['text'] in db.get_category():
                        vk_send_text(event.obj.message['from_id'], 'Выбирайте блюдо',
                                menu_gener(db.get_products(event.obj.message['text']), 0, 2,
                                           event.obj.message['text']).get_keyboard())
                if user_stat_ind == 0:
                    if event.obj.message['text'].isdigit():
                        products['amount'] = event.obj.message['text']
                        keyboard_menu = VkKeyboard(**settings2)
                        keyboard_menu.add_callback_button(label="Добавить в карзину", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 'A', 'prod': products['product'],
                                                                   'amount': products['amount']})
                        keyboard_menu.add_callback_button(label="Назад в категории", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 0, "menu": 1})
                        vk_send_text(event.obj.message['from_id'], f'Выбранное количество - {products["amount"]}', keyboard_menu.get_keyboard())

                    elif event.obj.message['text'] not in menu_1 and event.obj.message['text'] != 'Меню блюд':
                        keyboard_menu = VkKeyboard(**settings2)
                        keyboard_menu.add_callback_button(label="Назад в категории", color=VkKeyboardColor.PRIMARY,
                                                          payload={"type": 0, "menu": 1})
                        products['product'] = event.obj.message['text']
                        image_bytes = db.get_description_dish(event.obj.message['text'])[2]
                        upload = VkUpload(vk_session)
                        photo = upload.photo_messages(photos=image_bytes)[0]
                        vk_send_text(event.obj.message['from_id'], discription(db.get_description_dish(event.obj.message['text'])[0]),
                                     keyboard_menu.get_keyboard(), f"photo{photo['owner_id']}_{photo['id']}")
                        vk_send_text(event.obj.message['from_id'], "Введите количество продукта")

                elif user_stat_ind == 1:
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

                        vk_send_text(event.obj.message['from_id'], f"Стоимость корзины: {total}р.\n Выберите товар для удаления", menu_gener(label_list, 0, 3).get_keyboard())

                    elif event.obj.message['text'] != '':
                        row_id = event.obj.message['text'].split('.')[0]
                        label = event.obj.message['text'].split('.')[1]
                        label = label.split('-')[0]
                        amount = event.obj.message['text'].split('-')[1]
                        db.del_cart_line(event.obj.message['from_id'], row_id)
                        vk_send_text(event.obj.message['from_id'], f'Блюдо {label} в количестве {amount} удалено')

                elif user_stat_ind == 2:
                    if event.obj.message['text'] == 'Статистика заказов':
                        orders_list = db.get_to_rat_ord(event.obj.message['from_id'])
                        menu_orders = []
                        for order in orders_list:
                            if order is not None:
                                menu_orders.append(f'{order[0]}) {order[1][:16]}')
                        vk_send_text(event.obj.message['from_id'], f"Выберите заказ для отзыва", menu_gener(menu_orders,0, 5).get_keyboard())

                    elif ')' in event.obj.message['text']:
                        print(event.obj.message['text'])
                        ord_rating['order_id'] = event.obj.message['text'].split(')')[0]
                        keyboard_menu = rating_keyboard('F')
                        rating_ord = db.get_orders_rating()
                        if type(rating_ord) == str:
                            average_rat = rating_ord
                        else:
                            list_of_dish_rating = ''
                            for reviews in rating_ord[1]:
                                list_of_dish_rating += f'{reviews} \n'
                            average_rat = f'Средний рейтинг{rating_ord[0]}\n {list_of_dish_rating}'
                        vk_send_text(event.obj.message['from_id'], f"{average_rat}\n Выбирайте отметку выбранному блюду", keyboard_menu.get_keyboard())

                    elif event.obj.message['text'] != '' and ord_rating['order_id'] is not None:
                        ord_rating['review'] = event.obj.message['text']
                        db.add_order_rating(event.obj.message['from_id'], ord_rating['order_id'], ord_rating['review'], ord_rating['mark'])
                        vk_send_text(event.obj.message['from_id'], f"Спасибо за ваш отзыв")

                elif user_stat_ind == 3:
                    if event.obj.message['text'] == 'Статистика блюд':
                        vk_send_text(event.obj.message['from_id'], 'Выбирай категорию', menu_gener(menu_1, 0, 1).get_keyboard())
                    elif event.obj.message['text'] in menu_2:
                        product_rat['product'] = event.obj.message['text']
                        keyboard_menu = rating_keyboard('E')
                        rating_dish = db.get_product_rating(event.obj.message['text'])
                        if type(rating_dish) == str:
                            average_rat = rating_dish
                        else:
                            list_of_dish_rating = ''
                            for reviews in rating_dish[1]:
                                list_of_dish_rating += f'{reviews} \n'
                            average_rat = f'Средний рейтинг{rating_dish[0]}\n {list_of_dish_rating}'
                        vk_send_text(event.obj.message['from_id'], f"{average_rat}\n Выбирайте отметку выбранному блюду", keyboard_menu.get_keyboard())

                    elif event.obj.message['text'] != '' and product_rat['product'] is not None:
                        product_rat['review'] = event.obj.message['text']
                        db.add_product_rating(event.obj.message['from_id'], product_rat['product'],
                                              product_rat['rewiev'], product_rat['mark'])
                        vk_send_text(event.obj.message['from_id'], f"Спасибо за ваш отзыв")

                elif user_stat_ind == 4:
                    keyboard_menu = VkKeyboard(**settings2)
                    keyboard_menu.add_callback_button(label="Выбор способа оплаты", color=VkKeyboardColor.PRIMARY,
                                                      payload={"type": 'B'})
                    keyboard_menu.add_line()
                    keyboard_menu.add_callback_button(label="Выбор адреса доставки", color=VkKeyboardColor.PRIMARY,
                                                      payload={"type": 'C'})
                    keyboard_menu.add_line()
                    keyboard_menu.add_callback_button(label="Оформить заказ", color=VkKeyboardColor.PRIMARY,
                                                      payload={"type": 'D', 'adress': user_delivery['adress'],
                                                               'type_payment': user_delivery['type_payment']})
                    keyboard_menu.add_line()
                    keyboard_menu.add_button(label="Изменить заказ", color=VkKeyboardColor.PRIMARY,
                                             payload={"type": 'text'})
                    keyboard_menu.add_line()
                    keyboard_menu.add_button(label="Отменить заказ", color=VkKeyboardColor.PRIMARY,
                                             payload={"type": 'text'})

                    if event.obj.message['text'] in ['Наличность', 'Карта']:
                        vk_send_text(event.obj.message['from_id'], f"Способ оплаты выбран")
                        user_delivery['type_payment'] = ['Наличность', 'Карта'].index(event.obj.message['text'])

                    elif event.obj.message['text'] == 'Заказы':
                        vk_send_text(event.obj.message['from_id'], f"Order menu", keyboard_menu.get_keyboard())

                    elif event.obj.message['text'] != '':
                        vk_send_text(event.obj.message['from_id'], f"Адресом доставки выбрано {event.obj.message['text']}")
                        user_delivery['adress'] = event.obj.message['text']

                elif user_stat_ind == 5:
                    if event.obj.message['text'] == 'Изменить заказ':
                        orders_list = db.get_orders(event.obj.message['from_id'])
                        menu_orders = []
                        for order in orders_list:
                            if order is not None:
                                menu_orders.append(f'{order[0]}) {order[1][:16]}')
                        vk_send_text(event.obj.message['from_id'], f"Выберите заказ для изменения", menu_gener(menu_orders, 0, 4).get_keyboard())

                    elif event.obj.message['text'] != '':
                        order_id = event.obj.message['text'].split(')')[0]
                        date = event.obj.message['text'].split(')')[1]
                        db.change_order(event.obj.message['from_id'], order_id)
                        vk_send_text(event.obj.message['from_id'], f'Заказ на время: {date}; готов к редактированию. Пожалуйста, перейдите в корзину ')

                elif user_stat_ind == 6:
                    if event.obj.message['text'] == 'Отменить заказ':
                        orders_list = db.get_orders(event.obj.message['from_id'])
                        menu_orders = []
                        for order in orders_list:
                            if order is not None:
                                menu_orders.append(f'{order[0]}) {order[1][:16]}')
                        vk_send_text(event.obj.message['from_id'], f"Выберите какой заказ хотите отменить", menu_gener(menu_orders, 0, 5).get_keyboard())

                    elif event.obj.message['text'] != '':
                        order_id = event.obj.message['text'].split(')')[0]
                        date = event.obj.message['text'].split(')')[1]
                        db.cancel_order(order_id)
                        vk_send_text(event.obj.message['from_id'], f'Заказ на время: {date}; отменен.')

        elif event.type == VkBotEventType.MESSAGE_EVENT:
            if event.object.payload.get('type') in CALLBACK_TYPES:
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=event.object.user_id,
                    peer_id=event.object.peer_id,
                    event_data=json.dumps(event.object.payload))

            elif event.object.payload.get('type') == 'A':
                products['product'] = event.object.payload.get('prod')
                products['amount'] = event.object.payload.get('amount')
                keyboard_menu = VkKeyboard(**settings2)
                keyboard_menu.add_callback_button(label="Назад в категории", color=VkKeyboardColor.PRIMARY,
                                                  payload={"type": 0, "menu": 1})
                db.add_products_to_cart_row(event.obj.peer_id, products['product'], products['amount'])
                vk_send_text(event.obj.peer_id, 'Успешно добавлено в корзину', keyboard_menu.get_keyboard())

            elif event.object.payload.get('type') == 'B':
                keyboard_menu = VkKeyboard(**settings2)
                keyboard_menu.add_button(label="Карта", color=VkKeyboardColor.SECONDARY,
                                         payload={"type": 'text'})
                keyboard_menu.add_line()
                keyboard_menu.add_button(label="Наличность", color=VkKeyboardColor.SECONDARY,
                                         payload={"type": 'text'})
                vk_send_text(event.obj.peer_id, 'способы оплаты', keyboard_menu.get_keyboard())

            elif event.object.payload.get('type') == 'C':
                vk_send_text(event.obj.peer_id, 'Введите адрес доставки')

            elif event.object.payload.get('type') == 'D':
                print(event.object.payload)
                if event.object.payload.get('adress') is None:
                    vk_send_text(event.obj.peer_id, 'Заполните адрес доставки')
                elif event.object.payload.get('type_payment') is None:
                    vk_send_text(event.obj.peer_id, 'Выберите способ оплаты')
                else:
                    db.add_delivery(event.obj.peer_id, [user_delivery['adress'],
                                                        user_delivery['type_payment']])
                    db.add_to_order(event.obj.peer_id)
                    vk_send_text(event.obj.peer_id, 'Заказ принят')
                    user_delivery['adress'] = None
                    user_delivery['type_payment'] = None

            elif event.object.payload.get('type') == 'E':
                mark = event.object.payload.get('label')
                product_rat['mark'] = mark
                vk_send_text(event.obj.peer_id, 'Ваша отметка принята, напишите пожалуйста отзыв')

            elif event.object.payload.get('type') == 'F':
                mark = event.object.payload.get('label')
                ord_rating['mark'] = mark
                vk_send_text(event.obj.peer_id, 'Ваша отметка принята, напишите пожалуйста отзыв')

            elif event.object.payload.get('menu') == 1:
                name = event.object.payload.get('label')
                num1 = int(event.object.payload.get('type'))
                vk_edit_message(event.obj.peer_id, 'Выбирай категорию', event.obj.conversation_message_id,
                                menu_gener(menu_1, num1, 1, name).get_keyboard())

            elif event.object.payload.get('menu') == 3:
                num1 = int(event.object.payload.get('type'))
                total = db.get_cart_row(event.obj.peer_id)[1]
                vk_edit_message(event.obj.peer_id, f"Стоимость корзины: {total}р.\n Выберите товар для удаления",
                                event.obj.conversation_message_id, menu_gener(label_list, num1, 3).get_keyboard())

            elif event.object.payload.get('menu') == 4:
                num1 = int(event.object.payload.get('type'))
                vk_edit_message(event.obj.peer_id, f"Выберите заказ для изменени", event.obj.conversation_message_id,
                                menu_gener(label_list, num1, 4).get_keyboard())

            elif event.object.payload.get('menu') == 5:
                num1 = int(event.object.payload.get('type'))
                vk_edit_message(event.obj.peer_id, f"Выберите заказ, который хотите отменить", event.obj.conversation_message_id,
                                menu_gener(label_list, num1, 5).get_keyboard())

            else:
                name = event.object.payload.get('label')[0]
                num1 = int(event.object.payload.get('type'))
                vk_edit_message(event.obj.peer_id, 'Выбирай блюдо',event.obj.conversation_message_id,
                                menu_gener(db.get_products(name), num1, 2, name).get_keyboard())


if __name__ == '__main__':
    print()
    vk_bot()
