import pymysql
import os

class Database():
    def __init__(self):
        mysql_addr = os.getenv('MYSQL_PORT_33060_TCP_ADDR')
        if mysql_addr == "":
            mysql_addr = 'localhost'

        mysql_config = {
            'host': mysql_addr,
            'port': 3306,
            'user': 'root',
            'passwd': 'Rkakrnl1!',
            'db': 'stock',
            'charset': 'utf8mb4'}

        self.db = pymysql.connect(host=mysql_config.get('host')
                         , port=mysql_config.get('port')
                         , user=mysql_config.get('user')
                         , passwd=mysql_config.get('passwd')
                         , db=mysql_config.get('db')
                         , charset=mysql_config.get('charset'))

        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def execute(self, query):
        self.cursor.execute(query)

    def execute_one(self, query):
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return row

    def execute_all(self, query, data):
        print("data : {}".format(data))
        try:
            self.cursor.execute(query, data)
        except Exception as ex:
            print("에러 발생 : {}".format(ex))

        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.db.commit()