import sqlite3 as sl
from io import BytesIO
from base64 import b64decode
from PIL import Image


def convert_to_pic(str1):
    image = BytesIO(b64decode(str1))
    pillow = Image.open(image)
    return pillow
    # x = pillow.show()


con = sl.connect('db.sqlite')


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
        vk_id ="null"
    elif tg_id is None:
        tg_id = "null"
    user_id = con.execute(f"""SELECT id FROM users WHERE vk_id ={vk_id} or tg_id={tg_id}""").fetchone()[0]
    con.execute("""INSERT INTO cart (user_id, total) VALUES (?, ?)""", (user_id, 0))
    con.commit()




def add_products_to_cart(user_id, product, amount):
    """ для добавления продуктов в корзину вам нужен id пользователя, название продукта и его количество.
    Пример(331, 'Жаркое', 1) """
    user_id = con.execute(f"SELECT id FROM users WHERE vk_id={user_id} or tg_id={user_id}").fetchone()[0]
    product_id = con.execute(f"SELECT id FROM products WHERE name = '{product}'").fetchone()[0]
    price = con.execute(f"SELECT price FROM products WHERE name = '{product}'").fetchone()[0]
    total = price*amount
    con.execute('''INSERT INTO cart (user_id, product_id, amount, total) VALUES (?, ?, ?, ?)''',
                (user_id, product_id, amount, total))
    con.commit()


def del_cart_line(user_id, cart_id):
    """ удаление из записи из корзины вам нужен id записи в корзини, который можно получить из функции get_cart и id
    пользователя """
    user = con.execute(f'SELECT user_id FROM cart  JOIN users ON cart.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}').fetchone()[0]
    con.execute(f"""DELETE FROM cart WHERE user_id={user}  and id = {cart_id}""")


def get_cart(user_id):
    """используйте для просмотра корзины клиента"""
    carts = con.execute(f"""SELECT cart.id, (SELECT name FROM products WHERE id = product_id),  amount, total FROM cart INNER 
    JOIN users ON cart.user_id =users.id WHERE vk_id={user_id} or tg_id={user_id}""").fetchall()
    return carts


def get_product(str1):
    """Вводит основные параметры блюда и объект картинки. Примерно так:
    (('Борщ', 'Говядина, картофель, лук, марковь, свекла, капуста, чеснок, томатная паста, уксус, лавровый лист ', 12.0, '55:00'), <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=2500x1250 at 0x22613F8DD00>)"""
    product_desc = con.execute(f'SELECT name, description, price, time_to_cook FROM products WHERE name ="{str1}"').fetchone()
    pic = convert_to_pic(con.execute(f'SELECT pictures FROM products WHERE name ="{str1}"').fetchone()[0])
    return product_desc, pic



# print(get_cart(23131))
# print(del_cart_line(23131, get_cart(23131)[1][0]))
# print(get_cart(23131))
# def add_user(user_id, product_id, amount, total):
#     user_id = con.execute(f'SELECT id FROM users WHERE name = "{category}"')
#     user_id = user_id.fetchone()[0]
# print(get_category())
# print(get_products('Супы'))


