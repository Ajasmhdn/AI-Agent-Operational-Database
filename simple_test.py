import pymysql

print("starting")

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="admin123",
    database="manufacturing_operations_db"
)

print("connected")

conn.close()