# 다우지수, 나스닥, 달러, 금, 유가, 선물 -> KOSPI, KOSDAQ 예측

# 다우 https://m.stock.naver.com/api/json/world/worldIndexDay.nhn?symbol=DJI@DJI&pageSize=20&page=200
# 나스닥 https://m.stock.naver.com/api/json/world/worldIndexDay.nhn?symbol=NAS@IXIC&pageSize=20&page=200
# 달러 - api 불가 https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW&page=1
# 금  - api 불가 https://finance.naver.com/marketindex/goldDailyQuote.nhn?&page=2
# 서부텍사스유  - api 불가 https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=OIL_CL&fdtc=2&page=2
# td - class="pgRR" a href 의 page 값
# 선물  - api 불가
# KOSPI https://m.stock.naver.com/api/json/sise/dailySiseIndexListJson.nhn?code=KOSPI&pageSize=20&page=300
# KOSDAQ https://m.stock.naver.com/api/json/sise/dailySiseIndexListJson.nhn?code=KOSDAQ&pageSize=20&page=300

import requests
import database
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify

try:
    db_class = database.Database()
except Exception as ex:
    print("에러 발생 : {}".format(ex))

url_for_us_index = 'https://m.stock.naver.com/api/json/world/worldIndexDay.nhn'
url_for_kr_index = 'https://m.stock.naver.com/api/json/sise/dailySiseIndexListJson.nhn'

#pageSize = 250
#page 1 ~ 10 ( 대략 10년 치 )

#params = {'symbol': 'DJI@DJI', 'pageSize': 250, 'page': 200}
#params = {'symbol': 'NAS@IXIC', 'pageSize': 20, 'page': 200}
#params = {'code': 'KOSPI', 'pageSize': 20, 'page': 200}
#params = {'code': 'KOSDAQ', 'pageSize': 20, 'page': 200}

def getDollar():
    # 10개씩 조회... 250 * 200 / 10 = 5000 루프
    max_tr_query = "SELECT MAX(tr_date) as tr_date FROM tb_h_dollar"
    result = db_class.execute_one(max_tr_query)
    max_tr_date = str(result['tr_date']).replace("-", "")

    url = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW&page=1"
    html = requests.get(url)
    source = BeautifulSoup(html.content, "html.parser")

    result_tr = source.select("tbody > tr") # tbody 내에 tr 태그를 받아옴
    for i in range(len(result_tr)):
        result_td = result_tr[i].find_all("td")
        #print(result_td[0].text.replace(".", ""))
        #print(result_td[1].text.replace(",", ""))
        insert_query = "INSERT INTO tb_h_dollar VALUES('%s','%s')" % (result_td[0].text.replace(".", ""), result_td[1].text.replace(",", ""))
        db_class.execute(insert_query)

    db_class.commit()

def getDowJonse():
    # 1 ~ 10 까지 구하기
    max_tr_query = "SELECT MAX(tr_date) as tr_date FROM tb_h_dowjonse"
    result = db_class.execute_one(max_tr_query)
    max_tr_date = str(result['tr_date']).replace("-","")

    for i in range(1, 2):
        params = {'symbol': 'DJI@DJI', 'pageSize': 250, 'page': i}
        response = requests.get(url_for_us_index, params=params)
        res = response.json()
        #print(i)
        for data in res['result']['worldIndexDay']:
            if max_tr_date == data['dt']:
                break

            insert_query = "INSERT INTO tb_h_dowjonse VALUES('%s','%s')" % (data['dt'], data['ncv'])
            db_class.execute(insert_query)

    db_class.commit()

#getDowJonse()
#getDollar()
