import pymysql

def get_connection():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="rootroot",
        database="excel_validator",
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
