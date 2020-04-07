import pandas as pd
import pymysql
import os
#from sqlalchemy import create_engine


#db_data = 'mysql+pymysql://' + 'root' + ':' + 'Rkakrnl1!' + '@' + 'localhost' + ':3306/' \
#       + 'test' + '?charset=UTF8MB4'
#engine = create_engine(db_data, encoding='utf8')

mysql_addr = os.getenv('MYSQL_PORT_33060_TCP_ADDR')
if mysql_addr == "":
    mysql_addr = 'localhost'

mysql_config = {
    'host': mysql_addr,
    'port': 3306,
    'user': 'root',
    'passwd': 'Rkakrnl1!',
    'db': 'stock',
    'charset': 'utf8mb4' }

def getCodeInfo(code):
    db = pymysql.connect(host=mysql_config.get('host')
                         , port=mysql_config.get('port')
                         , user=mysql_config.get('user')
                         , passwd=mysql_config.get('passwd')
                         , db=mysql_config.get('db')
                         , charset=mysql_config.get('charset'))

    res = []

    try:
        with db.cursor() as cursor:
            sql = "select * from tb_m_jongmok where jongmok_code=%s"
            cursor.execute(sql, code)
            result = cursor.fetchall()
            print(result[0][0])
            res.append({'subject': '회사명', 'value': result[0][0]})
            res.append({'subject': '업종', 'value': result[0][2]})
            res.append({'subject': '메인상품', 'value': result[0][3]})
            res.append({'subject': '대표명', 'value': result[0][5]})
            res.append({'subject': '홈페이지', 'value': result[0][6]})

    finally:
        db.close()

    return res

def getCodeName(code_name):
    print("code_name : {}".format(code_name))
    db = pymysql.connect(host=mysql_config.get('host')
                         , port=mysql_config.get('port')
                         , user=mysql_config.get('user')
                         , passwd=mysql_config.get('passwd')
                         , db=mysql_config.get('db')
                         , charset=mysql_config.get('charset'))

    res = []

    try:
        with db.cursor() as cursor:
            sql = "select * from tb_m_jongmok where company_name = %s"
            cursor.execute(sql, code_name)
            res = cursor.fetchall()

    finally:
        db.close()

    return res[0][1]

#getCodeInfo("086980")
