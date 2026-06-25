from utils.db_connect import get_connection

connection = get_connection()

print("Connected successfully!")

connection.close()