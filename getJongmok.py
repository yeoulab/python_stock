import pandas as pd
import pymysql
from sqlalchemy import create_engine

#pymysql.install_as_MySQLdb()
#import MySQLdb

db_data = 'mysql+pymysql://' + 'root' + ':' + 'root' + '@' + 'localhost' + ':3306/' \
       + 'stock' + '?charset=UTF8MB4'
engine = create_engine(db_data, encoding='utf8')

db = pymysql.connect(host='localhost'
                     , port=3306
                     , user='root'
                     , passwd='root'
                     , db='stock'
                     , charset='utf8mb4')


df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]

df = df.rename(columns={'종목코드' : 'jongmok_code', '회사명' : 'company_name', '업종' : 'business_kind', '주요제품' : 'main_product', '상장일' : 'register_date','결산월' : 'fin_month', '대표자명' : 'ceo_name', '홈페이지' : 'homepage', '지역' : 'company_region'})

#print(df.loc[0]['company_name'])
#print(df.loc[1])

try:
    with db.cursor() as cursor:
        #cursor.execute("INSERT INTO tb_m_jongmok VALUES('삼성전자','caaaab','','','','','','','')")
        df.to_sql('tb_m_jongmok', engine, if_exists='append', index=False)
        #cursor.execute("SELECT * FROM tb_m_jongmok")
        #result = cursor.fetchall()
        #print(result[0])
        cursor.execute("update tb_m_jongmok set jongmok_code = lpad(jongmok_code,6,'0') where jongmok_code > '1';")
        db.commit()

finally:
    db.close()
