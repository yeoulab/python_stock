# ------------------- history ----------------------
# 20/05/28   getSise 에서 종가기준 정보를 삭제함
# 20/07/18   maxDate 를 start_date 로 변경
# --------------------------------------------------
import pandas as pd
import time
from datetime import datetime, timedelta
import logging
import sys
import requests
from bs4 import BeautifulSoup
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import common.const as const
import database
import getSise

def checkPer(code):
    base_url = 'https://m.stock.naver.com/api/html/item/getOverallInfo.nhn?code=' + code
    res = requests.get(base_url)
    soup = BeautifulSoup(res.content, 'html.parser')
    result = soup.find_all("li")
    per_data = result[10].find_all("span")

    if str(per_data[0].text) == 'N/A':
        return False
    else:
        return True

# 파라미터 입력을 받지 않았으면, 프로그램 종료
if len(sys.argv) == 1:
    sys.exit()

db_class = database.Database()
sql = "INSERT INTO tb_l_jongmok_stat VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'" \
      ",'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
file_name = "/home/yeoulab_ga/batch_" + str(datetime.today().strftime("%Y%m%d")) +"_" + sys.argv[1] + "_" + sys.argv[2] + ".log"
logging.basicConfig(filename=file_name, level=logging.INFO)

# 입력 받은 조건으로 종목 조회하기
# sosok = 0(코스피), 17Page 까지있음
# sosok = 1(코스닥), 15Page 까지 있음
url = "https://m.stock.naver.com/api/json/sise/siseListJson.nhn"
params = {}

# 2020/06/10 평일 하락종목들 체크
if sys.argv[3] is None:
    params = {"menu": "market_sum", "sosok": sys.argv[1], "pageSize": 100, "page": sys.argv[2]}
else:
    params = {"menu": "fall", "sosok": sys.argv[1], "pageSize": 100}

response = requests.get(url, params=params)
res = response.json()
# res['result']['itemList'] -> ItemList 의 'cd' 값이 code, 'nm' 값이 종목명

# 시작일자를 어떻게 정할 것인가?
# 1. 직전 6개월 ~ 직전 1개월 이내에 거래량이 가장 많은 일자
tday = pd.to_datetime(datetime.today().strftime("%Y%m%d"))
now_before_six_month = tday + timedelta(days=-180)
now_before_one_month = tday + timedelta(days=-30)
#print("tday : {}".format(tday))
#print("now_before_six_month : {}".format(now_before_six_month))
#print("now_before_one_month : {}".format(now_before_one_month))

# 2. 직전 6개월 ~ 현재 까지의 일수를 구함
mdays = pd.date_range(now_before_six_month, tday, freq='B')

# 3. 휴장일 제외
# 영업일 리스트에서 휴장일을 제외
hdays = const.hdays
for hday in hdays:
    if now_before_six_month <= hday <= tday:
        mdays = mdays.drop(hday)
#print("mdays after : {}".format(len(mdays)))

# 거래량 구하기
url = 'https://m.stock.naver.com/api/item/getPriceDayList.nhn'
for item in res['result']['itemList']:
    # PER 이 '+' 인 회사만 가져온다.
    perPlusYn = checkPer(item['cd'])

    # 2020/06/10 PER + check
    if not perPlusYn:
        time.sleep(1)
        continue

    # 총거래량 / 유통주식수가 400% 일 때의 시작일자를 구하기 위해 한번 더 메소드를 호출한다.
    company_detail_info = getSise.getCompanyDetailInfo(item['cd'])
    cir_stock_cnt = int(company_detail_info.get("cir_stock_cnt")) # 유통 거래량

    # 직전 6개월 ~ 현재 까지의 가격 구하기
    params = {'code': item['cd'], 'pageSize': len(mdays)}
    response = requests.get(url, params=params)
    res = response.json()

    # 최대 거래량 발생한 일자 구하기
    max_tr_dt = ""
    max_tr_cnt = int(0)
    tot_tr_cnt = int(0)
    for data in res['result']['list']:
        biz_date = data['dt']
        biz_date = pd.to_datetime(biz_date)

        # 매일 거래량을 더해서, 유통주식수의 4배가 될때 까지 구한다.
        tot_tr_cnt = tot_tr_cnt + int(data['aq'])

        # 400% ~ 500% 사이에 거래량이 가장 많은 날을 기준을 시작점으로 잡는다.
        if cir_stock_cnt * 4 < tot_tr_cnt < cir_stock_cnt * 5:
            if max_tr_cnt < int(data['aq']):
                max_tr_cnt = int(data['aq'])
                max_tr_dt = biz_date

        if tot_tr_cnt > cir_stock_cnt * 5:
            if max_tr_dt == "":
                max_tr_dt = biz_date
                break
            else:
                break

    # 최근 6개월 이내에 400% 가 안됐다면, 6개월 전 날자로 세팅
    if max_tr_dt == "":
        max_tr_dt = now_before_six_month

    res = getSise.getSise(item['cd'], max_tr_dt, tday)

    i = 0
    result_list = []
    for data in res['result']:
        if i == 8:
            result_list.append(int(data['value'].split('/')[0].split(':')[1].replace(",","")))
        else:
            try:
                result_list.append(int(data['value'].replace(",","")))
            except:
                result_list.append(int(data['value']))

        i = i + 1

    max_info = res['max_info']
    com_info = res['company_detail_info']

    insert_sql = sql % (item['cd']  # jongmok_code
                        , tday  # tr_date
                        , max_tr_dt # start_date
                        , item['nm'] # company_name
                        , result_list[0]  # for_tr_cnt
                        , result_list[1]  # ins_tr_cnt
                        , result_list[2] # ind_tr_cnt
                        , result_list[3] # avg_tr_cnt
                        , 0 #result_list[4] # for_avg_fin_amt
                        , 0 #result_list[5]  # ins_avg_fin_amt
                        , 0 #result_list[6] # ind_avg_fin_amt
                        , 0 #result_list[7] # tr_avg_fin_amt
                        , result_list[8] # fin_amt
                        , result_list[4] # for_avg_avg_amt
                        , result_list[5] # ins_avg_avg_amt
                        , result_list[6] # ind_avg_avg_amt
                        , result_list[7]  # tr_avg_avg_amt
                        , int(max_info['max_tr_quant'].replace(",", "")) # max_tr_qunat
                        , str(max_info['max_tr_date'].replace("-","")) # max_tr_date
                        , float(max_info['max_tr_ratio']) # max_tr_ratio
                        , int(max_info['tot_tr_quant'].replace(",", "")) # tot_tr_quant
                        , float(max_info['max_cir_ratio']) # max_cir_ratio
                        , float(max_info['tot_cir_ratio']) # tot_cir_ratio
                        , int(com_info['tot_stock_cnt'].replace(",", "")) # tot_stock_cnt
                        , float(com_info['cir_stock_ratio']) # cir_stock_ratio
                        , int(com_info['cir_stock_cnt'].replace(",", "")) # cir_stock_cnt
                        )

    logging.log(logging.INFO, insert_sql)
    db_class.execute(insert_sql)
    db_class.commit()
    time.sleep(3)

