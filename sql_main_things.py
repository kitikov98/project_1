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
    data = con.execute(f"""SELECT name FROM products WHERE category_id = {category_id}""")
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
    con.execute("""INSERT INTO cart (user_id, total) VALUES (?, ?)""", (user_id, 0))
    con.commit()


def add_products_to_cart_row(user_id, product, amount):
    """ для добавления продуктов в корзину вам нужен id пользователя, название продукта и его количество.
    Пример(331, 'Жаркое', 1) """
    total = con.execute(
        f"SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}").fetchone()[0]
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}").fetchone()[0]
    product_id = con.execute(f"SELECT id FROM products WHERE name = '{product}'").fetchone()[0]
    con.execute('''INSERT INTO cart_row (cart_id, product_id, amount) VALUES (?, ?, ?)''',
                (cart_id, product_id, amount))
    con.commit()
    new_total = con.execute(
        f"""SELECT SUM(amount*price) as total FROM cart_row INNER JOIN products ON cart_row.product_id = products.id WHERE cart_id = {cart_id}""").fetchone()[0]
    con.execute(f"""UPDATE cart SET total = {new_total} WHERE total = {total} and id = {cart_id}""")
    con.commit()


def del_cart_line(user_id, cart_row_id):
    """ удаление из записи из корзины вам нужен id записи в корзини, который можно получить из функции get_cart_row и id
    пользователя """
    total = con.execute(
        f"SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}").fetchone()[0]
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id} ").fetchone()[0]
    amount = con.execute(f'SELECT amount FROM cart_row WHERE id ={cart_row_id}').fetchone()[0]
    price = con.execute(
        f"SELECT price FROM products INNER JOIN cart_row ON cart_row.product_id=products.id WHERE cart_row.id = {cart_id}").fetchone()[0]
    new_total = total - (amount * price)
    con.execute(f"""DELETE FROM cart_row WHERE cart_id={cart_id} and id={cart_row_id}""")
    con.execute(f"""UPDATE cart SET total = {new_total} WHERE total = {total} and id = {cart_id}""")
    con.commit()

def delete_by_dish(user_id, product):
    """ удаление записи из корзины по id пользователя и нзванию продукта """
    total = con.execute(
        f"SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}").fetchone()[0]
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id} ").fetchone()[0]
    product_id = con.execute(f"""SELECT id FROM products WHERE name = '{product}'""").fetchone()[0]
    amount = con.execute(f'SELECT amount FROM cart_row WHERE product_id ={product_id}').fetchone()[0]
    cart_row_id = con.execute(f'SELECT id FROM cart_row WHERE product_id = {product_id} and cart_id={cart_id}').fetchone()[0]
    price = con.execute(
        f"SELECT price FROM products WHERE name = '{product}'").fetchone()[0]
    new_total = total - (amount * price)
    con.execute(f"""DELETE FROM cart_row WHERE cart_id={cart_id} and id={cart_row_id} """)
    con.execute(f"""UPDATE cart SET total = {new_total} WHERE total = {total} and id = {cart_id}""")
    con.commit()



def get_cart_row(user_id):
    """используйте для просмотра строк корзины клиента (cart_row_id, блюдо, количество, номер корзины привязанный к
    пользователю) - (7, 'Кальмары на гриле', 1, 2) """
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id} ").fetchone()[0]
    carts = con.execute(
        f"""SELECT id,  (SELECT name FROM products WHERE id = product_id), amount, cart_id FROM cart_row WHERE cart_id={cart_id} and status_in_order=1""").fetchall()
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


def add_to_order(user_id, list1):
    """ для добавления заказа в БД нужно имя пользователя и список [адрес доставки, выбранным типом оплаты
    0-наличность 1-карта] """
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id} ").fetchone()[0]
    status = 1
    now = datetime.now()
    max_time_to_cook = max(con.execute(
        f"SELECT time_to_cook FROM products INNER JOIN cart_row ON cart_row.product_id = products.id INNER JOIN cart ON cart.id=cart_row.cart_id WHERE cart.id = {cart_id}").fetchall())[0]
    max_time_to_cook = timedelta(minutes=datetime.strptime(max_time_to_cook, "%M:%S").minute)
    time_to_cook = now + max_time_to_cook + timedelta(minutes=30)
    con.execute(
        f"""INSERT INTO orders (user_address, date_delivery, status, cart_id, payment) VALUES (?, ?, ?, ?, ?)""",
        (list1[0], time_to_cook, status, cart_id, list1[1]))
    con.execute(f"""UPDATE cart_row SET status_in_order = 0 WHERE status_in_order = 1 and cart_id = {cart_id}""")
    # ↑ изменение статуса продукта с "в корзине", на "в заказе"
    con.commit()


def get_orders(user_id):
    """ получение данных заказа"""
    cart_id = con.execute(
        f"""SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id} """).fetchone()[0]
    orders = con.execute(f"SELECT * FROM orders WHERE cart_id={cart_id} and status = 1").fetchall()
    return orders


def change_order(user_id, order_id):
    """ для изменения заказа нужен id пользователя и id заказа, который можно получить используя метод get_orders"""
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id} ").fetchone()[0]
    con.execute(f"""UPDATE cart_row SET status_in_order = 1 WHERE status_in_order = 0 and cart_id = {cart_id}""")
    con.execute(f"""DELETE FROM orders WHERE cart_id={cart_id} and id={order_id}""")
    con.commit()


def cancel_order(user_id, order_id):
    """ для отмены заказ нужен id пользователя и id заказа из таблицы заказов"""
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id}").fetchone()[0]
    con.execute(f"""DELETE FROM orders WHERE cart_id={cart_id} and id={order_id}""")
    con.execute(f"DELETE FROM cart_row WHERE cart_id ={cart_id}")
    total = con.execute(f"""SELECT total FROM cart WHERE id = {cart_id}""").fetchone()[0]
    con.execute(f"UPDATE cart SET total=0 WHERE total={total}")
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




####################################################
"admin panel"

def change_user_category(user_id):
    pass


# print(add_product_rating(1122, 'первый', 'Борщ', 4))
# print(get_product_rating('Борщ'))
# print(add_order_rating(1122, 'быстро доставили', 1))
# print(add_product_rating(1122, 'отвратительный салат', 'Цезарь', 1))

# change_order(1122, 2)
# add_to_order(1122, ['г.Минск, ул. Сурганова 37/3', 0])
# add_user(1122, None, 'John')
# add_products_to_cart_row(1122, 'Борщ', 1)
# add_products_to_cart_row(1122, 'Цезарь', 2)
# add_products_to_cart_row(1122, 'Греческий', 1)
# add_products_to_cart_row(1122, 'Шоколадный фондан', 3)

# print(get_cart_row(1122))
# print(del_cart_line(1122, get_cart_row(1122)[1][0]))
# print(get_cart_row(1122))
# def add_user(user_id, product_id, amount, total):
#     user_id = con.execute(f'SELECT id FROM users WHERE name = "{category}"')
#     user_id = user_id.fetchone()[0]
# print(get_category())
# print(get_products('Супы'))
