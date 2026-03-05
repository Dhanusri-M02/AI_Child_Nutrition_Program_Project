import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="MSdhanu@29",
        database="child_nutrition"
    )
