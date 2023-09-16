import sqlite3 as sl
from io import BytesIO
from base64 import b64decode
from PIL import Image

con = sl.connect('db.sqlite')
typ = 'heliport'
with con:
    data = con.execute(f"""SELECT municipality, name, type, gps_code, iata_code, ident, iso_country, iso_region, 
    local_code, continent, coordinates_x, coordinates_y, elevation_ft FROM Airhub JOIN Geolocation ON 
    Airhub.id_geolocation = Geolocation.id JOIN Code_list ON Airhub.id_codelist = Code_list.id WHERE type = '{typ}' """)
    # print(data.fetchall())
    print(data.fetchone())

def convert_to_pic(str1):
    image = BytesIO(b64decode(str1))
    pillow = Image.open(image)
    return pillow
    # x = pillow.show()