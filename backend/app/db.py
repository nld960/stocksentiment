import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST, MYSQL_PORT = os.getenv("MYSQL_ADDRESS").split(":")

def add_new_user(id, nickname, weekdays, time):
    db = mysql.connector.connect(
        host=MYSQL_HOST, # use external access for debug, find in MySQL section in cloudrun weixin
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        port=MYSQL_PORT,
        database="stocksentiment"
    )

    cursor = db.cursor()

    insert_query = "INSERT INTO accessusers (id, nickname, weekdays, time) VALUES (%s, %s, %s, %s)"

    data = (id, nickname, weekdays, time)

    try:
        cursor.execute(insert_query, data)
        db.commit()
        print("Success")
    except mysql.connector.Error as error:
        print("Error: ", error)
    finally:
        cursor.close()
        db.close()

def get_table():
    db = mysql.connector.connect(
        host=MYSQL_HOST, # use external access for debug, find in MySQL section in cloudrun weixin
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        port=MYSQL_PORT,
        database="stocksentiment"
    )

    cursor = db.cursor()
    select_query = "SELECT * FROM accessusers"

    try:
        cursor.execute(select_query)
        rows = cursor.fetchall()
        for row in rows:
            yield row

    except mysql.connector.Error as error:
        print("Error selecting data from MySQL table:", error)

    finally:
        cursor.close()
        db.close()