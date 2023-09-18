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
        f"SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}").fetchone()[
        0]
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}").fetchone()[
        0]
    product_id = con.execute(f"SELECT id FROM products WHERE name = '{product}'").fetchone()[0]
    con.execute('''INSERT INTO cart_row (cart_id, product_id, amount) VALUES (?, ?, ?)''',
                (cart_id, product_id, amount))
    con.commit()
    new_total = con.execute(
        f"""SELECT SUM(amount*price) as total FROM cart_row INNER JOIN products ON cart_row.product_id = products.id WHERE cart_id = {cart_id}""").fetchone()[
        0]
    con.execute(f"""UPDATE cart SET total = {new_total} WHERE total = {total} and id = {cart_id}""")
    con.commit()


def del_cart_line(user_id, cart_row_id):
    """ удаление из записи из корзины вам нужен id записи в корзини, который можно получить из функции get_cart_row и id
    пользователя """
    total = con.execute(
        f"SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}").fetchone()[
        0]
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id} ").fetchone()[
        0]
    amount = con.execute(f'SELECT amount FROM cart_row WHERE id ={cart_row_id}').fetchone()[0]
    price = con.execute(
        f"SELECT price FROM products INNER JOIN cart_row ON cart_row.product_id=products.id WHERE cart_row.id = {cart_id}").fetchone()[
        0]
    new_total = total - (amount * price)
    con.execute(f"""DELETE FROM cart_row WHERE cart_id={cart_id} and id={cart_row_id}""")
    con.execute(f"""UPDATE cart SET total = {new_total} WHERE total = {total} and id = {cart_id}""")
    con.commit()


def get_cart_row(user_id):
    """используйте для просмотра строк корзины клиента (cart_row_id, блюдо, количество, номер корзины привязанный к
    пользователю) - (7, 'Кальмары на гриле', 1, 2) """
    cart_id = con.execute(
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id} ").fetchone()[
        0]
    carts = con.execute(
        f"""SELECT id,  (SELECT name FROM products WHERE id = product_id), amount, cart_id FROM cart_row WHERE cart_id={cart_id}""").fetchall()
    return carts


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
        f"SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id WHERE vk_id ={user_id} or tg_id={user_id} ").fetchone()[
        0]
    status = 1
    now = datetime.now()
    max_time_to_cook = max(con.execute(
        f"SELECT time_to_cook FROM products INNER JOIN cart_row ON cart_row.product_id = products.id INNER JOIN cart ON cart.id=cart_row.cart_id WHERE cart.id = {cart_id}").fetchall())[
        0]
    max_time_to_cook = timedelta(minutes=datetime.strptime(max_time_to_cook, "%M:%S").minute)
    time_to_cook = now + max_time_to_cook+timedelta(minutes=30)
    con.execute(
        f"""INSERT INTO orders (user_address, date_delivery, status, cart_id, payment) VALUES (?, ?, ?, ?, ?)""",
        (list1[0], time_to_cook, status, cart_id, list1[1]))
    con.commit()


def del_order(user_id):
    pass

# add_to_order(1122, ['г.Минск, ул. Сурганова 37/3', 0])
# add_user(1122, None, 'John')
# add_products_to_cart_row(1122, 'Шоколадный фондан', 1)
# print(get_cart_row(1122))
# print(del_cart_line(1122, get_cart_row(1122)[1][0]))
# print(get_cart_row(1122))
# def add_user(user_id, product_id, amount, total):
#     user_id = con.execute(f'SELECT id FROM users WHERE name = "{category}"')
#     user_id = user_id.fetchone()[0]
# print(get_category())
# print(get_products('Супы'))
