import mysql.connector

def get_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Mynameisf1_',
        database='hackdb'
    )
    return conn
