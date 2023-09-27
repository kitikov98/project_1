import sqlite3
from io import BytesIO
from base64 import b64decode
from PIL import Image
from datetime import datetime, timedelta


def convert_to_pic(str1):
    image = BytesIO(b64decode(str1))
    pillow = Image.open(image)
    return pillow

def convert_to_pic_b(str1):
    image = BytesIO(b64decode(str1))
    return image

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        # self.connection = self.connection.connection()
        self.create_tables()

    def create_tables(self):
        self.connection.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, vk_id INTEGER UNIQUE, 
        tg_id INTEGER UNIQUE, name TEXT, category TINYINT DEFAULT 0 CHECK(category >=0 AND category <= 2))''')

        self.connection.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, 
        date_delivery DATETIME, status BOOL, cart_id INTEGER, delivery_id INTEGER, rating_mark BOOL,
        FOREIGN KEY (cart_id) REFERENCES cart(id)ON DELETE RESTRICT ON UPDATE CASCADE, 
        FOREIGN KEY (delivery_id) REFERENCES delivery(id)ON DELETE RESTRICT ON UPDATE CASCADE)  ''')

        self.connection.execute('''CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY, user_id INTEGER, 
        total INTEGER DEFAULT 0, cart_status BOOL, FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE)''')

        self.connection.execute('''CREATE TABLE IF NOT EXISTS cart_row (id INTEGER PRIMARY KEY, product_id INTEGER,
        amount INTEGER, cart_id INTEGER, status_in_order BOOL DEFAULT 1, FOREIGN KEY (cart_id) REFERENCES cart(id)
        ON DELETE RESTRICT ON UPDATE CASCADE, FOREIGN KEY(product_id) REFERENCES products(id)
        ON DELETE RESTRICT ON UPDATE CASCADE)''')

        self.connection.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, category_id 
        INTEGER, price FLOAT, description TEXT, time_to_cook TIME, pictures BLOB, status BOOL, FOREIGN KEY(
        category_id) REFERENCES category(id) ON DELETE RESTRICT ON UPDATE CASCADE)''')

        self.connection.execute('''CREATE TABLE IF NOT EXISTS category
                            (id INTEGER PRIMARY KEY, name TEXT, description TEXT)''')

        self.connection.execute('''CREATE TABLE IF NOT EXISTS products_rating (id INTEGER PRIMARY KEY, user_id INTEGER, 
        product_id INTEGER, rating TINYINT DEFAULT 4 CHECK(rating >=0 AND rating <= 5), comment TEXT, status TINYTEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE RESTRICT ON UPDATE CASCADE)''')

        self.connection.execute('''CREATE TABLE IF NOT EXISTS orders_rating (id INTEGER PRIMARY KEY, user_id INTEGER, 
        order_id INTEGER, rating TINYINT DEFAULT 4 CHECK(rating >=0 AND rating <= 5), comment TEXT, status TINYTEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE, 
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE RESTRICT ON UPDATE CASCADE)''')

        self.connection.execute('''CREATE TABLE IF NOT EXISTS delivery(id INTEGER PRIMARY KEY, user_id INTEGER,
         user_address TEXT, payment BOOL,
         FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE)''')
        self.connection.commit()

    def add_category(self, list1):
        with self.connection:
            self.connection.execute('''INSERT INTO category (name, description) VALUES (?, ?)''', list1)
            self.connection.commit()

    def add_products(self, list1):
        with self.connection:
            self.connection.execute('''INSERT INTO products (name, category_id, price, description, time_to_cook, pictures, 
            status) VALUES (?, ?,?,?,?,?,?)''', list1)
            self.connection.commit()

    def get_cart_id(self, user_id):
        with self.connection:
            cart_id = self.connection.execute(f"""SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id 
            WHERE cart_status = 1 and (vk_id={user_id} or tg_id={user_id})""").fetchone()[0]
            return cart_id

    def get_category(self):
        """получение категорий, используйте для меню категорий"""
        with self.connection:
            list_cat = []
            data = self.connection.execute(f"""SELECT name FROM category """)
            for x in data.fetchall():
                for y in x:
                    list_cat.append(y)
            return list_cat

    def get_products(self, category):
        """получение названий блюд по категории, используйте для меню блюд"""
        with self.connection:
            category_id = self.connection.execute(f'SELECT id FROM category WHERE name = "{category}"')
            category_id = category_id.fetchone()[0]
            list_prod = []
            data = self.connection.execute(f"""SELECT name FROM products WHERE category_id = {category_id} and status = 1""")
            for x in data.fetchall():
                for y in x:
                    list_prod.append(y)
            return list_prod

    def list_products(self):
        with self.connection:
            list_prod = self.connection.execute(f'SELECT name FROM products').fetchall()
            return list_prod

    def add_user(self, vk_id, tg_id, name):
        """ для добавления пользователя в список пользователей. используйте None вместо переменной, в которую вам не надо
        записывать  Пример add_user(None, 1333, 'Giordani Jovanovic')"""
        with self.connection:
            self.connection.execute('''INSERT INTO users (vk_id, tg_id, name) VALUES (?, ?,  ?)''', (vk_id, tg_id, name))
            self.connection.commit()
            if vk_id is None:
                vk_id = "null"
            elif tg_id is None:
                tg_id = "null"
            user_id = self.connection.execute(f"""SELECT id FROM users WHERE vk_id ={vk_id} or tg_id={tg_id}""").fetchone()[0]
            self.connection.execute("""INSERT INTO cart (user_id, total, cart_status) VALUES (?, ?, ?)""", (user_id, 0, 1))
            self.connection.commit()

    def add_delivery(self, user_id, list1):
        """Добавление адреса доставки и способа оплаты, нужен id пользователя и список["Адрес доставки", выбранный типом оплаты
        0-наличность 1-карта]"""
        with self.connection:
            id_user = self.connection.execute(f"""SELECT id FROM users WHERE vk_id ={user_id} or tg_id={user_id}""").fetchone()[0]
            if self.connection.execute(f"""SELECT user_address, payment FROM delivery WHERE user_id ={id_user}""").fetchone() is None:
                self.connection.execute('''INSERT INTO delivery (user_id, user_address, payment) VALUES (?, ?,  ?)''',
                            (id_user, list1[0], list1[1]))
                self.connection.commit()
            else:
                self.connection.execute(f"""UPDATE delivery SET user_address = '{list1[0]}' WHERE user_id = {id_user}""")
                self.connection.execute(f"""UPDATE delivery SET payment = {list1[1]} WHERE user_id = {id_user}""")
                self.connection.commit()

    def add_products_to_cart_row(self, user_id, product, amount):
        """ для добавления продуктов в корзину вам нужен id пользователя, название продукта и его количество.
        Пример(331, 'Жаркое', 1) """
        with self.connection:
            cart_id = self.get_cart_id(user_id)
            total = self.connection.execute(
                f"""SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id
                 WHERE cart.id = {cart_id} and (vk_id={user_id} or tg_id={user_id})""").fetchone()[0]
            product_id = self.connection.execute(f"SELECT id FROM products WHERE name = '{product}'").fetchone()[0]
            self.connection.execute('''INSERT INTO cart_row (cart_id, product_id, amount) VALUES (?, ?, ?)''',
                        (cart_id, product_id, amount))
            self.connection.commit()
            new_total = self.connection.execute(
                f"""SELECT SUM(amount*price) as total FROM cart_row
                 INNER JOIN products ON cart_row.product_id = products.id WHERE cart_id = {cart_id}""").fetchone()[0]
            self.connection.execute(f"""UPDATE cart SET total = {new_total} WHERE total = {total} and id = {cart_id}""")
            self.connection.commit()

    def del_cart_line(self, user_id, cart_row_id):
        """ удаление из записи из корзины вам нужен id записи в корзини, который можно получить из функции get_cart_row и id
        пользователя """
        with self.connection:
            total = self.connection.execute(
                f"""SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id 
                WHERE cart_status = 1 and (vk_id={user_id} or tg_id={user_id})""").fetchone()[0]
            cart_id = self.get_cart_id(user_id)
            amount = self.connection.execute(f'SELECT amount FROM cart_row WHERE id ={cart_row_id}').fetchone()[0]
            price = self.connection.execute(
                f"SELECT price FROM products INNER JOIN cart_row ON cart_row.product_id=products.id WHERE cart_row.id = {cart_row_id}").fetchone()[
                0]
            new_total = total - (amount * price)
            self.connection.execute(f"""DELETE FROM cart_row WHERE cart_id={cart_id} and id={cart_row_id}""")
            self.connection.execute(f"""UPDATE cart SET total = {new_total} WHERE total ={total} and id = {cart_id}""")
            self.connection.commit()

    def delete_by_dish(self, user_id, product):
        """ удаление записи из корзины по id пользователя и нзванию продукта """
        with self.connection:
            total = self.connection.execute(
                f"""SELECT total FROM cart INNER JOIN users ON cart.user_id = users.id 
                WHERE  cart_status = 1 and (vk_id={user_id} or tg_id={user_id})""").fetchone()[0]
            cart_id = self.get_cart_id(user_id)
            product_id = self.connection.execute(f"""SELECT id FROM products WHERE name = '{product}'""").fetchone()[0]
            amount = self.connection.execute(f'SELECT amount FROM cart_row WHERE product_id ={product_id}').fetchone()[0]
            cart_row_id = \
            self.connection.execute(f'SELECT id FROM cart_row WHERE product_id = {product_id} and cart_id={cart_id}').fetchone()[0]
            price = self.connection.execute(f"SELECT price FROM products WHERE name = '{product}'").fetchone()[0]
            new_total = total - (amount * price)
            self.connection.execute(f"""DELETE FROM cart_row WHERE cart_id={cart_id} and id={cart_row_id} """)
            self.connection.commit()
            self.connection.execute(f"""UPDATE cart SET total = {new_total} WHERE total ={total} and id = {cart_id}""")
            self.connection.commit()

    def get_cart_row(self, user_id):
        """используйте для просмотра строк корзины клиента (cart_row_id, блюдо, количество, номер корзины привязанный к
        пользователю) - (7, 'Кальмары на гриле', 1, 2) """
        with self.connection:
            cart_id = self.get_cart_id(user_id)
            carts = self.connection.execute(
                f"""SELECT id,  (SELECT name FROM products WHERE id = product_id), amount, cart_id FROM cart_row WHERE cart_id={cart_id} 
                and status_in_order=1 """).fetchall()
            total = self.connection.execute(f"SELECT total From cart WHERE id = {cart_id}").fetchone()[0]
            return carts, total

    def get_description_dish(self, str1):
        """Вводит основные параметры блюда и объект картинки. Примерно так: (('Борщ', 'Говядина, картофель, лук, марковь,
        свекла, капуста, чеснок, томатная паста, уксус, лавровый лист ', 12.0, '55:00'),
        <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=2500x1250 at 0x22613F8DD00>) """
        with self.connection:
            product_desc = self.connection.execute(
                f'SELECT name, description, price, time_to_cook FROM products WHERE name ="{str1}"').fetchone()
            pic = convert_to_pic(self.connection.execute(f'SELECT pictures FROM products WHERE name ="{str1}"').fetchone()[0])
            pic2 = convert_to_pic_b(self.connection.execute(f'SELECT pictures FROM products WHERE name ="{str1}"').fetchone()[0])
            return product_desc, pic, pic2

    def add_to_order(self, user_id):
        """ для добавления заказа в БД нужно id пользователя  """
        with self.connection:
            cart_id = self.get_cart_id(user_id)
            status = 1
            delivery_id = self.connection.execute(f"""SELECT delivery.id FROM delivery 
             INNER JOIN users ON delivery.user_id = users.id WHERE vk_id={user_id} or tg_id={user_id}""").fetchone()[0]
            now = datetime.now()
            max_time_to_cook = max(self.connection.execute(
                f"SELECT time_to_cook FROM products INNER JOIN cart_row ON cart_row.product_id = products.id INNER JOIN cart ON cart.id=cart_row.cart_id WHERE cart.id = {cart_id}").fetchall())[
                0]
            max_time_to_cook = timedelta(minutes=datetime.strptime(max_time_to_cook, "%M:%S").minute)
            time_to_cook = now + max_time_to_cook + timedelta(minutes=30)
            self.connection.execute(
                f"""INSERT INTO orders (date_delivery, status, cart_id, delivery_id, rating_mark) VALUES (?, ?, ?, ?, ?)""",
                (time_to_cook, status, cart_id, delivery_id, 1))
            self.connection.execute(f"""UPDATE cart_row SET status_in_order = 0 WHERE status_in_order = 1 and cart_id = {cart_id}""")
            self.connection.execute(f"""UPDATE cart SET cart_status = 0 WHERE cart_status = 1 and id = {cart_id}""")
            # ↑ изменение статуса продукта с "в корзине", на "в заказе"
            id_user_in_users = \
            self.connection.execute(f"""SELECT id FROM users WHERE vk_id ={user_id} or tg_id={user_id}""").fetchone()[0]
            self.connection.execute("""INSERT INTO cart (user_id, total, cart_status) VALUES (?, ?, ?)""", (id_user_in_users, 0, 1))
            self.connection.commit()

    def get_orders(self, user_id):
        """ получение данных заказа"""
        with self.connection:
            orders = []
            cart_id_list = self.connection.execute(f"""SELECT cart.id FROM cart INNER JOIN users ON cart.user_id = users.id 
            WHERE cart_status = 0 and (vk_id={user_id} or tg_id={user_id})""").fetchall()
            for x in cart_id_list:
                orders.append(self.connection.execute(f"SELECT * FROM orders WHERE cart_id={x[0]} and status = 1").fetchone())
            return orders

    def change_order(self, user_id, order_id):
        """ для изменения заказа нужен id пользователя и id заказа, который можно получить используя метод get_orders"""
        with self.connection:
            cart_id = self.get_cart_id(user_id)
            self.connection.execute(f"""DELETE FROM cart WHERE id ={cart_id}""")
            cart_id = self.connection.execute(f"""SELECT cart_id FROM orders WHERE id = {order_id}""").fetchone()[0]
            self.connection.execute(f"""UPDATE cart SET cart_status = 1 WHERE cart_status = 0 and id={cart_id}""")
            self.connection.execute(f"""UPDATE cart_row SET status_in_order = 1 WHERE status_in_order = 0 and cart_id = {cart_id}""")
            self.connection.execute(f"""DELETE FROM orders WHERE cart_id={cart_id} and id={order_id}""")
            self.connection.commit()

    def cancel_order(self, order_id):
        """ для отмены заказ нужен id заказа из таблицы заказов"""
        with self.connection:
            self.connection.execute(f"""DELETE FROM orders WHERE id={order_id}""")
            self.connection.commit()

    def add_product_rating(self, user_id, product, review=" ", mark=4):
        """для выставления рейтинга нужны название продукта, отметка и отзыв, id пользователя """
        with self.connection:
            id_user = self.connection.execute(f"""SELECT id FROM users WHERE vk_id ={user_id} or tg_id={user_id} """).fetchone()[0]
            product_id = self.connection.execute(f"""SELECT id FROM products WHERE name = '{product}' """).fetchone()[0]
            status = 'на рассмотрении'
            try:
                self.connection.execute(
                    f"""INSERT INTO products_rating (user_id, product_id, rating, comment, status) 
                    VALUES (?, ?, ?, ?, ?)""", (id_user, product_id, mark, review, status))
                self.connection.commit()
                return f'спасибо, ваш отзыв принят'
            except:
                return f'неверно выставлено значение отметки рейтинга'

    def get_product_rating(self, product):
        """ выдача среднего рейтинга на основе как минимум 10 отметок"""
        with self.connection:
            product_id = self.connection.execute(f"""SELECT id FROM products WHERE name = '{product}' """).fetchone()[0]
            product_rating = self.connection.execute(
                f'SELECT * FROM products_rating WHERE product_id = {product_id} and status = "принят"').fetchall()
            rating_list = []
            rating_texts = []
            if len(product_rating) < 10:
                return f'В данный момент недостаточно данных, чтоб сформировать рейтинг для просмотра блюда {product}'
            else:
                for item in product_rating:
                    rating_list.append(item[3])
                    rating_texts.append(item[4])
                average_rating = sum(rating_list) / len(rating_list)
                return average_rating, rating_texts

    def get_orders_rating(self):
        """ выдача среднего рейтинга и отзывов на основе как минимум 10 отметок"""
        with self.connection:
            orders_rating = self.connection.execute(f'SELECT * FROM orders_rating WHERE status = "принят"').fetchall()
            rating_list = []
            rating_texts = []
            if len(orders_rating) < 10:
                return f'В данный момент недостаточно данных, чтоб сформировать рейтинг доставок'
            else:
                for item in orders_rating:
                    rating_list.append(item[3])
                    rating_texts.append(item[4])
                average_rating = sum(rating_list) / len(rating_list)
                return average_rating, rating_texts

    def get_to_rat_ord(self, user_id):
        with self.connection:
            id_user = self.connection.execute(f"""SELECT id FROM users WHERE vk_id ={user_id} or tg_id={user_id} """).fetchone()[0]
            deliv_id = self.connection.execute(f'SELECT id FROM delivery WHERE user_id = {id_user}').fetchone()[0]
            order = self.connection.execute(f"""SELECT id, date_delivery FROM orders 
            WHERE rating_mark = 1 and status = 0 and delivery_id = {deliv_id}""").fetchall()
            return order

    def add_order_rating(self, user_id, order_id, review=" ", mark=4):
        """для выставления рейтинга нужны id заказ, отметка и отзыв, id пользователя """
        with self.connection:
            id_user = self.connection.execute(f"""SELECT id FROM users WHERE vk_id ={user_id} or tg_id={user_id} """).fetchone()[0]
            status = 'на рассмотрении'
            try:
                self.connection.execute(
                    f"""INSERT INTO orders_rating (user_id, order_id, rating, comment, status) VALUES (?, ?, ?, ?, ?)""",
                    (id_user, order_id, mark, review, status))
                self.connection.execute(f"""UPDATE orders SET rating_mark = 0 WHERE id = {order_id}""")
                self.connection.commit()
                return f'спасибо, ваш отзыв принят'
            except:
                return f'неверно выставлено значение отметки рейтинга'


####################################################
    "admin panel"

    def adm_get_ord(self):
        """ получение списка всех активных заказов"""
        with self.connection:
            orders = self.connection.execute(f'SELECT * FROM orders WHERE status = 1').fetchall()
            return orders


    def get_user_category(self, user_id):
        """ получение категори пользователя 0-пользователь, 1,2 - администары разного уравня"""
        with self.connection:
            try:
                cat = self.connection.execute(f"SELECT category FROM users WHERE tg_id = {user_id}").fetchone()[0]
                return cat
            except:
                return f'Данного пользователя не существует либо он пользуется vk-ботом'

    def adm_change_order_status(self, order_id):
        """меняет статус заказа на доставленный"""
        with self.connection:
            self.connection.execute(f"UPDATE orders SET status = 0 WHERE status = 1 and id = {order_id} ")
            self.connection.commit()

    def adm_change_to_first_rank(self, user_id):
        """наделения правми админа 1го разряда"""
        with self.connection:
            self.connection.execute(f"UPDATE users SET category = 1 WHERE (category = 0 or category = 2) and tg_id = {user_id} ")
            self.connection.commit()

    def adm_change_to_second_rank(self, user_id):
        """наделения правми админа 2го разряда"""
        with self.connection:
            self.connection.execute(f"UPDATE users SET category = 2 WHERE (category = 0 or category = 1 )and tg_id = {user_id} ")
            self.connection.commit()

    def adm_get_rating_ord(self):
        """ выдача списка отзывов, которые на рассмотрении"""
        with self.connection:
            orders = self.connection.execute(f'SELECT * FROM orders_rating WHERE status ="на рассмотрении"').fetchall()
            return orders

    def adm_get_ord_rewiew(self, order_id):
        """ выдача информации по отзыву"""
        with self.connection:
            review_mark = self.connection.execute(f'SELECT rating, comment FROM orders_rating WHERE id ={order_id}').fetchone()
            return review_mark

    def adm_accept_stat_ord(self, ord_rat_id):
        with self.connection:
            self.connection.execute(f"UPDATE orders_rating SET status='принят' WHERE id ={ord_rat_id}")
            self.connection.commit()

    def adm_refuse_stat_ord(self, ord_rat_id):
        with self.connection:
            self.connection.execute(f"UPDATE orders_rating SET status='отклонен' WHERE id ={ord_rat_id}")
            self.connection.commit()

    def adm_get_rating_prod(self):
        """ выдача списка отзывов, которые на рассмотрении"""
        with self.connection:
            orders = self.connection.execute(f'SELECT * FROM products_rating WHERE status ="на рассмотрении"').fetchall()
            return orders

    def adm_get_prod_rewiew(self, order_id):
        """ выдача информации по отзыву"""
        with self.connection:
            review_mark = self.connection.execute(f'SELECT rating, comment FROM products_rating WHERE id ={order_id}').fetchone()
            return review_mark

    def adm_accept_stat_prod(self, ord_rat_id):
        with self.connection:
            self.connection.execute(f"UPDATE products_rating SET status='принят' WHERE id ={ord_rat_id}")
            self.connection.commit()

    def adm_refuse_stat_prod(self, ord_rat_id):
        with self.connection:
            self.connection.execute(f"UPDATE products_rating SET status='отклонен' WHERE id ={ord_rat_id}")
            self.connection.commit()

    def adm_get_products_status(self):
        with self.connection:
            list_of_prod = self.connection.execute(f'SELECT name, status FROM products').fetchall()
            return list_of_prod

    def adm_stop_prod(self, product):
        with self.connection:
            self.connection.execute(f'UPDATE products SET status = 0 WHERE name ="{product}"')
            self.connection.commit()

    def adm_unstop_prod(self, product):
        with self.connection:
            self.connection.execute(f'UPDATE products SET status = 1 WHERE name ="{product}"')
            self.connection.commit()

    def adm_get_admins(self, tg_id):
        with self.connection:
            admins = self.connection.execute(
                f'SELECT tg_id, category FROM users WHERE tg_id !={tg_id} and (category = 1 or category = 2)').fetchall()
            return admins

    def adm_decrease_adm_rank(self, tg_id):
        with self.connection:
            self.connection.execute(f'UPDATE users SET category = 0 WHERE tg_id = {tg_id}')
            self.connection.commit()


db = Database('db.sqlite')

