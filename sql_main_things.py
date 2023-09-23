import sqlite3 as sl
from io import BytesIO
from base64 import b64decode
from PIL import Image
from datetime import datetime, timedelta


def convert_to_pic(str1):
    image = BytesIO(b64decode(str1))
    pillow = Image.open(image)
    return pillow
    # x = pillow.show()


con = sl.connect('db.sqlite', check_same_thread=False)

def get_cart_id(user_id):
    cart_id = con.execute(f"""SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id 
    WHERE cart_status = 1 and (vk_id={user_id} or tg_id={user_id})""").fetchone()[0]
    return cart_id

def get_category():
    """получение категорий, используйте для меню категорий"""
    list_cat = []
    data = con.execute(f"""SELECT name FROM category """)
    for x in data.fetchall():
        for y in x:
            list_cat.append(y)
    return list_cat


def get_products(category):
    """получение названий блюд по категории, используйте для меню блюд"""
    category_id = con.execute(f'SELECT id FROM category WHERE name = "{category}"')
    category_id = category_id.fetchone()[0]
    list_prod = []
    data = con.execute(f"""SELECT name FROM products WHERE category_id = {category_id} and status = 1""")
    for x in data.fetchall():
        for y in x:
            list_prod.append(y)
    return list_prod


def add_user(vk_id, tg_id, name):
    """ для добавления пользователя в список пользователей. используйте None вместо переменной, в которую вам не надо
    записывать  Пример add_user(None, 1333, 'Giordani Jovanovic')"""
    con.execute('''INSERT INTO users (vk_id, tg_id, name) VALUES (?, ?,  ?)''', (vk_id, tg_id, name))
    con.commit()
    if vk_id is None:
        vk_id = "null"
    elif tg_id is None:
        tg_id = "null"
    user_id = con.execute(f"""SELECT id FROM users WHERE vk_id ={vk_id} or tg_id={tg_id}""").fetchone()[0]
    con.execute("""INSERT INTO cart (user_id, total, cart_status) VALUES (?, ?, ?)""", (user_id, 0, 1))
    con.commit()


def add_delivery(user_id, list1):
    """Добавление адреса доставки и способа оплаты, нужен id пользователя и список["Адрес доставки", выбранный типом оплаты
    0-наличность 1-карта]"""
    id_user = con.execute(f"""SELECT id FROM users WHERE vk_id ={user_id} or tg_id={user_id}""").fetchone()[0]
    if con.execute(f"""SELECT user_address, payment FROM delivery WHERE user_id ={id_user}""").fetchone() is None:
        con.execute('''INSERT INTO delivery (user_id, user_address, payment) VALUES (?, ?,  ?)''', (id_user, list1[0], list1[1]))
        con.commit()
    else:
        con.execute(f"""UPDATE delivery SET user_address = '{list1[0]}' WHERE user_id = {id_user}""")
        con.execute(f"""UPDATE delivery SET payment = {list1[1]} WHERE user_id = {id_user}""")
        con.commit()


def add_products_to_cart_row(user_id, product, amount):
    """ для добавления продуктов в корзину вам нужен id пользователя, название продукта и его количество.
    Пример(331, 'Жаркое', 1) """
    cart_id = get_cart_id(user_id)
    total = con.execute(
        f"""SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id
         WHERE cart.id = {cart_id} and (vk_id={user_id} or tg_id={user_id})""").fetchone()[0]
    product_id = con.execute(f"SELECT id FROM products WHERE name = '{product}'").fetchone()[0]
    con.execute('''INSERT INTO cart_row (cart_id, product_id, amount) VALUES (?, ?, ?)''',
                (cart_id, product_id, amount))
    con.commit()
    new_total = con.execute(
        f"""SELECT SUM(amount*price) as total FROM cart_row
         INNER JOIN products ON cart_row.product_id = products.id WHERE cart_id = {cart_id}""").fetchone()[0]
    con.execute(f"""UPDATE cart SET total = {new_total} WHERE total = {total} and id = {cart_id}""")
    con.commit()




def del_cart_line(user_id, cart_row_id):
    """ удаление из записи из корзины вам нужен id записи в корзини, который можно получить из функции get_cart_row и id
    пользователя """
    total = con.execute(
        f"""SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id 
        WHERE cart_status = 1 and (vk_id={user_id} or tg_id={user_id})""").fetchone()[0]
    cart_id = get_cart_id(user_id)
    amount = con.execute(f'SELECT amount FROM cart_row WHERE id ={cart_row_id}').fetchone()[0]
    price = con.execute(
        f"SELECT price FROM products INNER JOIN cart_row ON cart_row.product_id=products.id WHERE cart_row.id = {cart_row_id}").fetchone()[0]
    new_total = total - (amount * price)
    con.execute(f"""DELETE FROM cart_row WHERE cart_id={cart_id} and id={cart_row_id}""")
    con.execute(f"""UPDATE cart SET total = {new_total} WHERE total ={total} and id = {cart_id}""")
    con.commit()


def delete_by_dish(user_id, product):
    """ удаление записи из корзины по id пользователя и нзванию продукта """
    total = con.execute(
        f"""SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id 
        WHERE  cart_status = 1 and (vk_id={user_id} or tg_id={user_id})""").fetchone()[0]
    cart_id = get_cart_id(user_id)
    product_id = con.execute(f"""SELECT id FROM products WHERE name = '{product}'""").fetchone()[0]
    amount = con.execute(f'SELECT amount FROM cart_row WHERE product_id ={product_id}').fetchone()[0]
    cart_row_id = con.execute(f'SELECT id FROM cart_row WHERE product_id = {product_id} and cart_id={cart_id}').fetchone()[0]
    price = con.execute(f"SELECT price FROM products WHERE name = '{product}'").fetchone()[0]
    new_total = total - (amount * price)
    con.execute(f"""DELETE FROM cart_row WHERE cart_id={cart_id} and id={cart_row_id} """)
    con.commit()
    con.execute(f"""UPDATE cart SET total = {new_total} WHERE total ={total} and id = {cart_id}""")
    con.commit()


def get_cart_row(user_id):
    """используйте для просмотра строк корзины клиента (cart_row_id, блюдо, количество, номер корзины привязанный к
    пользователю) - (7, 'Кальмары на гриле', 1, 2) """
    cart_id = get_cart_id(user_id)
    carts = con.execute(
        f"""SELECT id,  (SELECT name FROM products WHERE id = product_id), amount, cart_id FROM cart_row WHERE cart_id={cart_id} 
        and status_in_order=1 """).fetchall()
    total = con.execute(f"SELECT total From cart WHERE id = {cart_id}").fetchone()[0]
    return carts, total


def get_description_dish(str1):
    """Вводит основные параметры блюда и объект картинки. Примерно так: (('Борщ', 'Говядина, картофель, лук, марковь,
    свекла, капуста, чеснок, томатная паста, уксус, лавровый лист ', 12.0, '55:00'),
    <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=2500x1250 at 0x22613F8DD00>) """
    product_desc = con.execute(
        f'SELECT name, description, price, time_to_cook FROM products WHERE name ="{str1}"').fetchone()
    pic = convert_to_pic(con.execute(f'SELECT pictures FROM products WHERE name ="{str1}"').fetchone()[0])
    return product_desc, pic


def add_to_order(user_id):
    """ для добавления заказа в БД нужно id пользователя  """
    cart_id = get_cart_id(user_id)
    status = 1
    delivery_id = con.execute(f"""SELECT delivery.id FROM delivery 
     INNER JOIN users ON delivery.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}""").fetchone()[0]
    now = datetime.now()
    max_time_to_cook = max(con.execute(
        f"SELECT time_to_cook FROM products INNER JOIN cart_row ON cart_row.product_id = products.id INNER JOIN cart ON cart.id=cart_row.cart_id WHERE cart.id = {cart_id}").fetchall())[0]
    max_time_to_cook = timedelta(minutes=datetime.strptime(max_time_to_cook, "%M:%S").minute)
    time_to_cook = now + max_time_to_cook + timedelta(minutes=30)
    con.execute(
        f"""INSERT INTO orders (date_delivery, status, cart_id, delivery_id) VALUES (?, ?, ?, ?)""",
        (time_to_cook, status, cart_id, delivery_id))
    con.execute(f"""UPDATE cart_row SET status_in_order = 0 WHERE status_in_order = 1 and cart_id = {cart_id}""")
    con.execute(f"""UPDATE cart SET cart_status = 0 WHERE cart_status = 1 and id = {cart_id}""")
    # ↑ изменение статуса продукта с "в корзине", на "в заказе"
    id_user_in_users = con.execute(f"""SELECT id FROM users WHERE vk_id ={user_id} or tg_id={user_id}""").fetchone()[0]
    con.execute("""INSERT INTO cart (user_id, total, cart_status) VALUES (?, ?, ?)""", (id_user_in_users, 0, 1))
    con.commit()


def get_orders(user_id):
    """ получение данных заказа"""
    orders = []
    cart_id_list = con.execute(f"""SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id 
    WHERE cart_status = 0 and (vk_id={user_id} or tg_id={user_id})""").fetchall()
    for x in cart_id_list:
        orders.append(con.execute(f"SELECT * FROM orders WHERE cart_id={x[0]} and status = 1").fetchone())
    return orders


def change_order(user_id, order_id):
    """ для изменения заказа нужен id пользователя и id заказа, который можно получить используя метод get_orders"""
    cart_id = get_cart_id(user_id)
    con.execute(f"""DELETE FROM cart WHERE id ={cart_id}""")
    cart_id = con.execute(f"""SELECT cart_id FROM orders WHERE id = {order_id}""").fetchone()[0]
    con.execute(f"""UPDATE cart SET cart_status = 1 WHERE cart_status = 0 and id={cart_id}""")
    con.execute(f"""UPDATE cart_row SET status_in_order = 1 WHERE status_in_order = 0 and cart_id = {cart_id}""")
    con.execute(f"""DELETE FROM orders WHERE cart_id={cart_id} and id={order_id}""")
    con.commit()


def cancel_order(order_id):
    """ для отмены заказ нужен id заказа из таблицы заказов"""
    con.execute(f"""DELETE FROM orders WHERE id={order_id}""")
    con.commit()


def add_product_rating(user_id,  product, review=" ", mark=4):
    """для выставления рейтинга нужны название продукта, отметка и отзыв, id пользователя """
    id_user = con.execute(f"""SELECT id FROM users WHERE vk_id ={user_id} or tg_id={user_id} """).fetchone()[0]
    product_id = con.execute(f"""SELECT id FROM products WHERE name = '{product}' """).fetchone()[0]
    status = 'на рассмотрении'
    try:
        con.execute(
            f"""INSERT INTO products_rating (user_id, product_id, rating, comment, status) VALUES (?, ?, ?, ?, ?)""",
            (id_user, product_id, mark, review, status))
        con.commit()
        return f'спасибо, ваш отзыв принят'
    except:
        return f'неверно выставлено значение отметки рейтинга'


def get_product_rating(product):
    """ выдача среднего рейтинга на основе как минимум 10 отметок"""
    product_id = con.execute(f"""SELECT id FROM products WHERE name = '{product}' """).fetchone()[0]
    product_rating = con.execute(f'SELECT * FROM products_rating WHERE product_id = {product_id} and status = "принят"').fetchall()
    rating_list = []
    rating_texts = []
    if len(product_rating) < 10:
        return f'В данный момент недостаточно данных, чтоб сформировать рейтинг для просмотра блюда {product}'
    else:
        for item in product_rating:
            rating_list.append(item[3])
            rating_texts.append(item[4])
        average_rating = sum(rating_list)/len(rating_list)
        return average_rating, rating_texts


def get_orders_rating():
    """ выдача среднего рейтинга и отзывов на основе как минимум 10 отметок"""
    orders_rating = con.execute(f'SELECT * FROM orders_rating WHERE status = "принят"').fetchall()
    rating_list = []
    rating_texts = []
    if len(orders_rating) < 10:
        return f'В данный момент недостаточно данных, чтоб сформировать рейтинг доставок'
    else:
        for item in orders_rating:
            rating_list.append(item[3])
            rating_texts.append(item[4])
        average_rating = sum(rating_list)/len(rating_list)
        return average_rating, rating_texts


def add_order_rating(user_id, id_order, review=" ", mark=4):
    """для выставления рейтинга нужны id заказ, отметка и отзыв, id пользователя """
    id_user = con.execute(f"""SELECT id FROM users WHERE vk_id ={user_id} or tg_id={user_id} """).fetchone()[0]
    status = 'на рассмотрении'
    try:
        con.execute(
            f"""INSERT INTO orders_rating (user_id, order_id, rating, comment, status) VALUES (?, ?, ?, ?, ?)""",
            (id_user, id_order, mark, review, status))
        con.commit()
        return f'спасибо, ваш отзыв принят'
    except:
        return f'неверно выставлено значение отметки рейтинга'


# add_order_rating(463971847, 3, 'всё крута', 5)
####################################################
"admin panel"


def adm_get_ord():
    """ получение списка всех активных заказов"""
    orders = con.execute(f'SELECT * FROM orders WHERE status = 1').fetchall()
    return orders


def get_user_category(user_id):
    """ получение категори пользователя 0-пользователь, 1,2 - администары разного уравня"""
    try:
        cat = con.execute(f"SELECT category FROM users WHERE tg_id = {user_id}").fetchone()[0]
        return cat
    except:
        return f'Данного пользователя не существует либо он пользуется vk-ботом'


def adm_change_order_status(order_id):
    """меняет статус заказа на доставленный"""
    con.execute(f"UPDATE orders SET status = 0 WHERE status = 1 and id = {order_id} ")
    con.commit()


def adm_change_to_first_rank(user_id):
    """наделения правми админа 1го разряда"""
    con.execute(f"UPDATE users SET category = 1 WHERE category = 0 or category = 2 and tg_id = {user_id} ")
    con.commit()


def adm_change_to_second_rank(user_id):
    """наделения правми админа 2го разряда"""
    con.execute(f"UPDATE users SET category = 2 WHERE category = 0 or category = 1 and tg_id = {user_id} ")
    con.commit()


def adm_get_rating_ord():
    """ выдача списка отзывов, которые на рассмотрении"""
    orders = con.execute(f'SELECT * FROM orders_rating WHERE status ="на рассмотрении"').fetchall()
    return orders


def adm_get_ord_rewiew(order_id):
    """ выдача информации по отзыву"""
    review_mark = con.execute(f'SELECT rating, comment FROM orders_rating WHERE id ={order_id}').fetchone()
    return review_mark


def adm_accept_stat_ord(ord_rat_id):
    con.execute(f"UPDATE orders_rating SET status='принят' WHERE id ={ord_rat_id}")
    con.commit()


def adm_refuse_stat_ord(ord_rat_id):
    con.execute(f"UPDATE orders_rating SET status='отклонен' WHERE id ={ord_rat_id}")
    con.commit()


def adm_get_rating_prod():
    """ выдача списка отзывов, которые на рассмотрении"""
    orders = con.execute(f'SELECT * FROM products_rating WHERE status ="на рассмотрении"').fetchall()
    return orders


def adm_get_prod_rewiew(order_id):
    """ выдача информации по отзыву"""
    review_mark = con.execute(f'SELECT rating, comment FROM products_rating WHERE id ={order_id}').fetchone()
    return review_mark


def adm_accept_stat_prod(ord_rat_id):
    con.execute(f"UPDATE products_rating SET status='принят' WHERE id ={ord_rat_id}")
    con.commit()


def adm_refuse_stat_prod(ord_rat_id):
    con.execute(f"UPDATE products_rating SET status='отклонен' WHERE id ={ord_rat_id}")
    con.commit()


def adm_get_products_status():
    list_of_prod = con.execute(f'SELECT name, status FROM products').fetchall()
    return list_of_prod


def adm_stop_prod(product):
    con.execute(f'UPDATE products SET status = 0 WHERE name ="{product}"')
    con.commit()


def adm_unstop_prod(product):
    con.execute(f'UPDATE products SET status = 1 WHERE name ="{product}"')
    con.commit()



# add_user(None, 1122, 'Павлович Илья')
# add_delivery(1122, ['Сурганова 37/3', 0])
# print(add_product_rating(1122, 'первый', 'Борщ', 4))
# add_order_rating(463971847,1,'всё нормуль', 5)
# print(get_product_rating('Борщ'))
# print(add_order_rating(1122, 'быстро доставили', 1))
# print(add_product_rating(463971847, 'Цезарь', 'отвратительный салат', 1))
# print(adm_get_products_status())
# change_order(1122, 2)
# add_to_order(1122)
# add_user(1122, None, 'John')
# add_products_to_cart_row(1122, 'Борщ', 1)
# add_products_to_cart_row(1122, 'Цезарь', 1)
# delete_by_dish(1122, "Цезарь")
# add_products_to_cart_row(1122, 'Греческий', 1)
# add_products_to_cart_row(1122, 'Шоколадный фондан', 1)
# delete_by_dish(1122, 'Шоколадный фондан')