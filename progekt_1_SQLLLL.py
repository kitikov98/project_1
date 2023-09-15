import sqlite3

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()
    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY, vk_id INTEGER UNIQUE, tg_id INTEGER UNIQUE, name TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS orders
                            (id INTEGER PRIMARY KEY, user_id INTEGER, date DATETIME, status TEXT, delivery_address TEXT,
                            delivery_time DATETIME, FOREIGN KEY(user_id) REFERENCES users(id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS order_items
                            (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER,
                            FOREIGN KEY(order_id) REFERENCES orders(id), FOREIGN KEY(product_id) REFERENCES products(id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products
                            (id INTEGER PRIMARY KEY, name TEXT, description TEXT, price REAL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS admins
                            (id INTEGER PRIMARY KEY, vk_id INTEGER UNIQUE, tg_id INTEGER UNIQUE)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS comments
                            (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER, text TEXT, rating INTEGER,
                            FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(product_id) REFERENCES products(id))''')
        self.connection.commit()
    def add_user(self, vk_id, tg_id, name):
        self.cursor.execute('''INSERT INTO users (vk_id, tg_id, name) VALUES (?, ?, ?)''', (vk_id, tg_id, name))
        self.connection.commit()
    def get_user_by_vk_id(self, vk_id):
        self.cursor.execute('''SELECT * FROM users WHERE vk_id=?''', (vk_id,))
        return self.cursor.fetchone()
    def get_user_by_tg_id(self, tg_id):
        self.cursor.execute('''SELECT * FROM users WHERE tg_id=?''', (tg_id,))
        return self.cursor.fetchone()
    def add_order(self, user_id, date, status, delivery_address, delivery_time):
        self.cursor.execute('''INSERT INTO orders (user_id, date, status, delivery_address, delivery_time)
                            VALUES (?, ?, ?, ?, ?)''', (user_id, date, status, delivery_address, delivery_time))
        self.connection.commit()
    def get_orders_by_user_id(self, user_id):
        self.cursor.execute('''SELECT * FROM orders WHERE user_id=?''', (user_id,))
        return self.cursor.fetchall()
    def add_order_item(self, order_id, product_id, quantity):
        self.cursor.execute('''INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)''',
                            (order_id, product_id, quantity))
        self.connection.commit()
    def get_order_items_by_order_id(self, order_id):
        self.cursor.execute('''SELECT * FROM order_items WHERE order_id=?''', (order_id,))
        return self.cursor.fetchall()
    def add_product(self, name, description, price):
        self.cursor.execute('''INSERT INTO products (name, description, price) VALUES (?, ?, ?)''',
                            (name, description, price))
        self.connection.commit()
    def get_all_products(self):
        self.cursor.execute('''SELECT * FROM products''')
        return self.cursor.fetchall()
    def add_admin(self, vk_id, tg_id):
        self.cursor.execute('''INSERT INTO admins (vk_id, tg_id) VALUES (?, ?)''', (vk_id, tg_id))
        self.connection.commit()
    def get_admin_by_vk_id(self, vk_id):
        self.cursor.execute('''SELECT * FROM admins WHERE vk_id=?''', (vk_id,))
        return self.cursor.fetchone()
    def get_admin_by_tg_id(self, tg_id):
        self.cursor.execute('''SELECT * FROM admins WHERE tg_id=?''', (tg_id,))
        return self.cursor.fetchone()
    def add_comment(self, user_id, product_id, text, rating):
        self.cursor.execute('''INSERT INTO comments (user_id, product_id, text, rating) VALUES (?, ?, ?, ?)''',
                            (user_id, product_id, text, rating))
        self.connection.commit()
    def get_comments_by_product_id(self, product_id):
        self.cursor.execute('''SELECT * FROM comments WHERE product_id=?''', (product_id,))
        return self.cursor.fetchall()