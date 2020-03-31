import urllib
import time

from urllib.request import urlopen
from bs4 import BeautifulSoup

import pymysql
from sqlalchemy import create_engine

db_data = 'mysql+pymysql://' + 'root' + ':' + 'root' + '@' + 'localhost' + ':3306/' \
       + 'stock' + '?charset=UTF8MB4'
engine = create_engine(db_data, encoding='utf8')

db = pymysql.connect(host='localhost'
                     , port=3306
                     , user='root'
                     , passwd='root'
                     , db='stock'
                     , charset='utf8mb4')
sql = """insert into customer(jongmok_code,tr_date,end_amt,low_amt,hi_amt,tr_amt) values (%s,%s,%d,%d,%d,%d)"""

try:
    with db.cursor() as cursor:
        cursor.execute("select * from tb_m_jongmok where jongmok_code='086980'")
        rows = cursor.fetchall()

        for row in rows:
            #print(row[1]) 종목코드
            url = 'http://finance.naver.com/item/sise_day.nhn?code=' + row[1]
            html = urlopen(url)
            source = BeautifulSoup(html.read(), "html.parser")

            maxPage = source.find_all("table", align="center")
            mp = maxPage[0].find_all("td", class_="pgRR")
            #print("### : " +mp[0].a.get('href'))
            #mpNum = int(mp[0].a.get('href')[-3:])
            mpNum = 1

            for page in range(1, mpNum + 1):
                print(str(page))
                print(row[1])
                url = 'http://finance.naver.com/item/sise_day.nhn?code=' + row[1] + '&page=' + str(page)
                html = urlopen(url)
                source = BeautifulSoup(html.read(), "html.parser")
                srlists = source.find_all("tr")
                isCheckNone = None

                if ((page % 1) == 0):
                    time.sleep(1.50)

                for i in range(1, len(srlists) - 1):
                    if (srlists[i].span != isCheckNone):
                        srlists[i].td.text
                        # 상폐된 종목
                        if srlists[i].find_all("td", align="center")[0].text == "":
                            break
                        tr_date = srlists[i].find_all("td", align="center")[0].text.replace(".", "")
                        end_amt = int(srlists[i].find_all("td", class_="num")[0].text.replace(",", ""))
                        low_amt = int(srlists[i].find_all("td", class_="num")[3].text.replace(",", ""))
                        hi_amt = int(srlists[i].find_all("td", class_="num")[4].text.replace(",", ""))
                        tr_amt = int(srlists[i].find_all("td", class_="num")[5].text.replace(",", ""))
                        print(row[1])
                        print(tr_date)
                        print(type(end_amt))
                        print(low_amt)
                        print(hi_amt)
                        print(tr_amt)
                        cursor.execute(sql, (row[1], tr_date, end_amt, low_amt, hi_amt, tr_amt))


                db.commit()

finally:
    db.close()
