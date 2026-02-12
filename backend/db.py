import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",        # your mysql username
        password="MSdhanu@29",    # your mysql password
        database="child_nutrition"
    )
    return conn
