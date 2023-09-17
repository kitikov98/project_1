import sqlite3
from base64 import b64encode


class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, vk_id INTEGER UNIQUE, 
        tg_id INTEGER UNIQUE, name TEXT, category TINYINT DEFAULT 0 CHECK(category >=0 AND category <= 2))''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, 
        user_address TEXT, date_delivery DATETIME, status BOOL, cart_id INTEGER, payment BOOL, 
        FOREIGN KEY (user_id) REFERENCES users(id)ON DELETE RESTRICT ON UPDATE CASCADE, FOREIGN KEY (cart_id) REFERENCES 
        cart(id)ON DELETE RESTRICT ON UPDATE CASCADE)  ''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY, user_id INTEGER, 
        total INTEGER DEFAULT 0, FOREIGN KEY (user_id) REFERENCES users(id)ON DELETE RESTRICT ON UPDATE CASCADE)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cart_row (id INTEGER PRIMARY KEY, product_id INTEGER,
        amount INTEGER, cart_id INTEGER, FOREIGN KEY (cart_id) REFERENCES cart(id)ON DELETE RESTRICT ON 
        UPDATE CASCADE, FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE RESTRICT ON UPDATE CASCADE)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, category_id 
        INTEGER, price FLOAT, description TEXT, time_to_cook TIME, pictures BLOB, status BOOL, FOREIGN KEY(
        category_id) REFERENCES category(id) ON DELETE RESTRICT ON UPDATE CASCADE)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS category
                            (id INTEGER PRIMARY KEY, name TEXT, description TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products_rating (id INTEGER PRIMARY KEY, user_id INTEGER, 
        product_id INTEGER, rating TINYINT DEFAULT 4 CHECK(rating >=0 AND rating <= 5), comment INTEGER, FOREIGN KEY( 
        user_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE, FOREIGN KEY(product_id) REFERENCES 
        products(id) ON DELETE RESTRICT ON UPDATE CASCADE)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS orders_rating (id INTEGER PRIMARY KEY, user_id INTEGER, 
        order_id INTEGER, rating TINYINT DEFAULT 4 CHECK(rating >=0 AND rating <= 5), comment INTEGER, FOREIGN KEY( 
        user_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE, FOREIGN KEY(order_id) REFERENCES orders(
        id) ON DELETE RESTRICT ON UPDATE CASCADE)''')
        self.connection.commit()

    def add_user(self, vk_id, tg_id, name):
        self.cursor.execute('''INSERT INTO users (vk_id, tg_id, name) VALUES (?, ?,  ?)''', (vk_id, tg_id, name))
        self.connection.commit()

    def add_category(self, list1):
        self.cursor.execute('''INSERT INTO category (name, description) VALUES (?, ?)''', list1)
        self.connection.commit()

    def add_products(self, list1):
        self.cursor.execute('''INSERT INTO products (name, category_id, price, description, time_to_cook, pictures, 
        status) VALUES (?, ?,?,?,?,?,?)''', list1)
        self.connection.commit()


db = Database('db.sqlite')


def convert_to_binary_data(filename):  # filename - название папки с картинками
    with open(filename, 'rb') as file:
        blob_data = b64encode(file.read())
    return blob_data


list_category = [['Закуски',
                  """Тип блюд, которые подаются на стол перед основными блюдами. Могут служить и отдельным перекусом. Закуски к столу часто сопровождают прием небольшого количества спиртного для аппетита."""],
                 ['Супы',
                  """Жидкое блюдо, первое блюдо. Многие разновидности супов получили самостоятельные наименования,некоторые сохранили в своем названии слово «суп»"""],
                 ['Блюда из мяса',
                  """Блюда из мяса занимают особое место в рационе современного человека. В состав мяса входят минеральные вещества и белки, содержащие незаменимые аминокислоты."""],
                 ['Блюда из рыбы и морепродуктов',
                  """Блюда из морепродуктов и рыбы намного нежнее мяса, в них меньше соединительной ткани, поэтому они готовятся быстрее, хорошо усваиваются и легче перевариваются. Кроме того рыбные блюда низкокалорийные. Калорийность рыбы ниже, чем у  мяса животных в 5 раз, поэтому блюда из морепродуктов и рыбы входят в большинство диет. В рыбьем жире и рыбьей печени содержатся  много витаминов А и Д."""],
                 ['Паста и пицца',
                  """Пицца — итальянское блюдо с плоской круглой хлебной основой, покрытой томатным соусом, сыром и различными ингредиентами, запеченное в высокотемпературной духовке. Паста — это блюдо итальянской кухни, которое готовят из пшеничной муки и воды, придают ей различные формы и размеры и обычно подают с соусом или другими добавками"""],
                 ['Салаты',
                  """Холодное блюдо, состоящее из одного вида или смеси разных видов сочетающихся между собой нарезанных продуктов в заправке"""],
                 ['Десерты',
                  """Завершающее блюдо стола, предназначенное для получения приятных вкусовых ощущений в конце обеда или ужина, обычно — сладкие деликатесы (не фрукты)."""],
                 ['Барбекю',
                  """Способ приготовления пищевых продуктов, чаще всего мяса (стейков, сосисок), на жаре тлеющих углей, горящего газа или электронагревателя"""],
                 ['Рис и лапша',
                  """Рис — зёрна одноимённого растения. Он является основным пищевым продуктом для большей части населения Земли, хотя по объёму производимого пищевого зерна уступает пшенице. Лапша́ — макаронное изделие лентообразной формы. Тесто раскатывают в пласт и нарезают на полоски, затем отваривают. Изготавливается из муки (пшеничной, рисовой, гречневая мука гречневой), замешанной на воде. Некоторые сорта могут содержать различные добавки, например, яйца или яичный порошок («яичная лапша»)."""],
                 ['Вегетарианские блюда',
                  """Вегетариа́нство — система питания преимущественно либо исключительно растительной пищей"""], ]

prod_list = [['Брускетки', 1, 12, """Белый хлеб, помидоры, оливковое масло, чеснок, бальзамический крем, свежемолотый черный перец, соль, зелень""", "15:00",
              convert_to_binary_data('pictures/brusketi.jpg'), 1],
             ['Сырные тарелки', 1, 15, 'белый сыр, томм, овечий сыр, бри, зрелый твёрдый сыр, голубой сыр',
              "10:00", convert_to_binary_data('pictures/sirni_tarelki.jpg'), 1],
             ['Суши и роллы', 1, 22, """Филадельфия, Калифорния, Канада, Сякэ маки""", "25:00",
              convert_to_binary_data('pictures/sushi.jpg'), 1],
             ['Борщ', 2, 12, """Говядина, картофель, лук, марковь, свекла, капуста, чеснок, томатная паста, уксус, лавровый лист """,
              "55:00", convert_to_binary_data('pictures/borsch.jpg'), 1],
             ['Грибной суп', 2, 12, """Белые грибы, картофель, молотый черный перец, репчатый лук, оливковое масло, зелень, морковь""",
              "25:00", convert_to_binary_data('pictures/mushrum_soup.jpg'), 1],
             ['Томатный суп с морепродуктами', 2, 14, """Коктейль из морепродуктов, репчатый лук, ченок, сладкий перец, помидоры, томатный сок, шафран, сушеный базилик, прованские травы, лимонный сок, куриное яйцо""",
              "35:00", convert_to_binary_data('pictures/tomato_fish_soup.jpg'), 1],
             ['Стейк', 3, 22, """Говядина, соль, перец, растительное масло""", "35:00",
              convert_to_binary_data('pictures/steak.jpg'), 1],
             ['Жаркое', 3, 43, """Свинина, масло подсолнечное, лук репчатый, морковь, картофель, перец сладкий, зелеь петрушки, томаты, перец черный молотый, лист лавровый""",
              "42:00", convert_to_binary_data('pictures/zharkoe.jpg'), 1],
             ['Котлеты', 3, 22, """Фарш(говядина+свинина), лук репчатый, яйцо, белый хлеб, молоко, мука, сливочное масло, свежемолотый перец""",
              "55:00", convert_to_binary_data('pictures/kotleti.jpg'), 1],
             ['Пельмени', 3, 22, """фарш мясной, лук репчатый, соль, перец, мука, яйцо""", "15:00",
              convert_to_binary_data('pictures/pelmeni.jpg'), 1],
             ['Запеченный лосось', 4, 21, """Филе лосося, оливковое масло, лимон, чеснок, розмарин, 
                 молотый черный перец""", "35:00", convert_to_binary_data('pictures/losos.jpg'), 1],
             ['Креветки в сливочном соусе', 4, 31, """Креветки, ченок, оливковое масло, лимоны, сливки, белое сухое вино, розмарни свежий, петрушка""",
              "35:00", convert_to_binary_data('pictures/krevetki.jpg'), 1],
             ['Кальмары на гриле', 4, 41, """Кальмар, лимон, чеснок, перец черный молотый, зира, оливкове масло, кинза, помидор Черри""",
              "35:00", convert_to_binary_data('pictures/kalmari.jpg'), 1],
             ['Спагетти болоньезе', 5, 15, """Спагетти, репчатый лук, чеснок, оливковое масло, мясной фарш, сладкий перец, консервироанные помидоры, твердый сыр""",
              "35:00", convert_to_binary_data('pictures/bolonezi.jpg'), 1],
             ['Пенне аррабьята', 5, 15, """Паста пенне, помидоры черри, помидоры, перец чили, чеснок, лук репчатый, вино белое, базилик, оливковое масло""",
              "25:00", convert_to_binary_data('pictures/arabiata.jpg'), 1],
             ['Пицца Маргарита', 5, 17, """Основа для пиццы, томатная паста, оливковое масло, чеснок, базилик, моцарелла, помидоры черри""",
              "25:00", convert_to_binary_data('pictures/margarita.jpg'), 1],
             ['Пицца с морепродуктами', 5, 18, """Основа для пиццы, томатный соус, коктейль из морепродуктов, каперсы, свежий желтый перец, майоран, орегано, сыр моцарелла, сыр пармезан, маслины""",
              "25:00", convert_to_binary_data('pictures/sea_pizza.jpg'), 1],
             ['Цезарь', 6, 12, """Салат Ромэн, куриное филе. хлебные крошки, пармезан, яйца, анчоусы, майонез, чеснок, лимонный сок""",
              "15:00", convert_to_binary_data('pictures/cesar.jpg'), 1],
             ['Греческий', 6, 12, """Огуры, помидор, фета, красный лук, маслины, оливковое масло, лимонный сок""",
              "15:00", convert_to_binary_data('pictures/greek_salad.jpg'), 1],
             ['Тунец с картофельным пюре', 6, 14,
              """Тунец, картофельное пюре, лук зеленый, майонез, лимонный сок""",
              "35:00", convert_to_binary_data('pictures/tunets_potato.jpg'), 1],
             ['Тирамису', 7, 8, """Савоярди, кофе, маскарпоне, сахар, яйца, какао""",
              "33:00", convert_to_binary_data('pictures/tiramisu.jpg'), 1],
             ['Панакотта', 7, 9, """Сливки, сахар, ваниль, желатин""",
              "30:00", convert_to_binary_data('pictures/panakotta.jpg'), 1],
             ['Шоколадный фондан', 7, 7, """Шоколад, масло сливочное, сахар, яйа, мука""",
              "30:00", convert_to_binary_data('pictures/chocolate_fondan.jpg'), 1],
             ['Ассорти гриля', 8, 33, """Свиной брквички, куриные крылья, говяжие стейки, картофель""",
              "57:00", convert_to_binary_data('pictures/ass_or_tea_grill.jpg'), 1],
             ['Шашлык из свинины', 8, 30, """Свинина, лук репчатый, майонез, соль, перец""",
              "39:00", convert_to_binary_data('pictures/shashlik.jpg'), 1],
             ['Куриные крылья с барбекю-глазурью', 8, 26, """Куриный крылья, барбекю-соус""",
              "19:00", convert_to_binary_data('pictures/kriliya.jpg'), 1],
             ['Паэлья', 9, 22, """Рис, курица, креветки, мидии, перец болгарский, лук репчатый, чеснок, томаты, шафран""",
              "32:00", convert_to_binary_data('pictures/paelia.jpg'), 1],
             ['Кунг пао', 9, 20, """Куриное филе, лапша, орехи кешью, перец чили, лук зеленый, соевый соус""",
              "35:00", convert_to_binary_data('pictures/kung_lao.jpg'), 1],
             ['Лапша с куриной грудкой', 9, 12, """Лапша, куриное филе, морковь, лук репчатый, соевый соус""",
              "25:00", convert_to_binary_data('pictures/lapsha_s_grudkoi.jpg'), 1],
             ['Овощной гриль', 10, 17, """Баклажаны, кабачки, перец болгарский, грибы, лук репчатый""",
              "33:00", convert_to_binary_data('pictures/ovosch_grill.jpg'), 1],
             ['Рататуй', 10, 15, """Баклажаны, кабачки, томаты, лук репчатый, перец болгарский""",
              "25:00", convert_to_binary_data('pictures/ratatui.jpg'), 1],
             ['Овощное карри', 10, 15, """Картофель, морковь, лук репчатый, кокосовое молоко, карри-паста""",
              "35:00", convert_to_binary_data('pictures/ovosch_kari.jpg'), 1]]




for item in list_category:
    db.add_category(item)

for item in prod_list:
    db.add_products(item)
