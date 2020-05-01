import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import common.const as const

def getSise(item_code, start_date, end_date):
    # 정보를 가져오기 위한 url
    url = 'https://m.stock.naver.com/api/item/getTrendList.nhn'

    # 중간값을 가져오기 위한 url
    url2 = 'https://m.stock.naver.com/api/item/getPriceDayList.nhn'

    # 휴장일 값 조회
    hdays = const.hdays

    # 입력받은 일자 ~ 현재일자까지의 영업일 리스트
    start_date = pd.to_datetime(start_date)
    tday = pd.to_datetime(datetime.today().strftime("%Y%m%d"))

    # end_date 가 입력되지 않았으면 오늘날짜로
    if end_date == "":
        end_date = tday
    else:
        end_date = pd.to_datetime(end_date)

    mdays = pd.date_range(start_date, tday, freq='B')

    # 영업일 리스트에서 휴장일을 제외
    for hday in hdays:
      if start_date <= hday <= tday:
          #print("빠진 휴일은 : {}".format(hday))
          mdays = mdays.drop(hday)

    # get method 에서 가져올 param
    # 종목코드 / size 는 입력 받아 계산한다.
    params = {'code': item_code, 'size': len(mdays)}
    response = requests.get(url, params=params)
    res = response.json()

    params2 = {'code': item_code, 'pageSize': len(mdays)}
    response2 = requests.get(url2, params=params2)
    res2 = response2.json()
    #print(res['result'][0])
    #print(res2['result']['list'][0])
    price_list = res2['result']['list']

    # 외인/기관/개인 순 매수/매도 량
    sum_real_frgn_pure_buy_quant = 0
    sum_real_organ_pure_buy_quant = 0
    sum_real_indi_pure_buy_quant = 0

    # 외인/기관/개인 단가 구하기 위한 변수
    sum_frgn_pure_buy_quant = 0
    sum_organ_pure_buy_quant = 0
    sum_indi_pure_buy_quant = 0
    sum_frgn_unit_price = 0
    sum_organ_unit_price = 0
    sum_indi_unit_price = 0
    sum_total_unit_price = 0

    # 외인/기관/개인 단가 구하기 위한 변수(평균가격으로)
    sum_frgn_unit_avg_price = 0
    sum_organ_unit_avg_price = 0
    sum_indi_unit_avg_price = 0
    sum_total_unit_avg_price = 0

    sum_acc_quant = 0
    today_price = res2['result']['list'][0]['ncv']

    max_info = {"max_tr_quant": 0,
                "max_tr_date": "",
                "max_tr_ratio": 0.0,
                "tot_tr_quant": 0,
                "max_cir_ratio": 0.0,
                "tot_cir_ratio": 0.0}

    # end date 를 고려한 거래량
    for row in res['result']:
        biz_date = row['bizdate']
        biz_date = pd.to_datetime(biz_date)
        if end_date < biz_date:
            continue

        sum_acc_quant += row['acc_quant']

    #print("sum_acc_qunat : {}".format(sum_acc_quant))
    # 유통주식수 구하기 (getTest 참조)
    company_detail_info = getCompanyDetailInfo(item_code)
    #print(company_detail_info)
    max_info['tot_tr_quant'] = sum_acc_quant

    cnt = -1
    real_cnt = 0

    for row in res['result']:
        cnt = cnt + 1
        biz_date = row['bizdate']
        biz_date = pd.to_datetime(biz_date)
        if end_date < biz_date:
            continue

        # 거래량 평균을 구하기 위한 real day cnt
        real_cnt = real_cnt + 1

        # 중간값 구하기
        #price_list[cnt]['hv'] # 고가
        #price_list[cnt]['lv'] # 저가
        #price_list[cnt]['ov']  # 시가
        #price_list[cnt]['ncv'] # 종가
        avg_price = int((price_list[cnt]['lv'] + price_list[cnt]['hv']) / 2)

        # MAX 값 구하기
        if row['acc_quant'] > max_info.get("max_tr_quant"):
            max_info['max_tr_quant'] = row['acc_quant']
            max_info['max_tr_date'] = str(biz_date)[:10]

        ratio = row['acc_quant'] / sum_acc_quant

        sum_real_frgn_pure_buy_quant += row['frgn_pure_buy_quant']
        sum_real_organ_pure_buy_quant += row['organ_pure_buy_quant']
        sum_real_indi_pure_buy_quant += row['indi_pure_buy_quant']

        sum_frgn_pure_buy_quant += row['frgn_pure_buy_quant'] * ratio
        sum_organ_pure_buy_quant += row['organ_pure_buy_quant'] * ratio
        sum_indi_pure_buy_quant += row['indi_pure_buy_quant'] * ratio

        # 종가로만 판단
        frgn_unit_price = row['frgn_pure_buy_quant'] * row['close_val'] * ratio
        organ_unit_price = row['organ_pure_buy_quant'] * row['close_val'] * ratio
        indi_unit_price = row['indi_pure_buy_quant'] * row['close_val'] * ratio
        sum_frgn_unit_price += frgn_unit_price
        sum_organ_unit_price += organ_unit_price
        sum_indi_unit_price += indi_unit_price
        sum_total_unit_price += row['acc_quant'] * row['close_val']

        # 평균가격( avg(시가, 종가) )
        frgn_unit_avg_price = row['frgn_pure_buy_quant'] * avg_price * ratio
        organ_unit_avg_price = row['organ_pure_buy_quant'] * avg_price * ratio
        indi_unit_avg_price = row['indi_pure_buy_quant'] * avg_price * ratio
        sum_frgn_unit_avg_price += frgn_unit_avg_price
        sum_organ_unit_avg_price += organ_unit_avg_price
        sum_indi_unit_avg_price += indi_unit_avg_price
        sum_total_unit_avg_price += row['acc_quant'] * avg_price

    return_value = {}

    result = []
    result.append({'subject': '외국인', 'value': format(sum_real_frgn_pure_buy_quant,","), 'pre_value': 0})
    result.append({'subject': '기관', 'value': format(sum_real_organ_pure_buy_quant,","), 'pre_value': 0})
    result.append({'subject': '개인', 'value': format(sum_real_indi_pure_buy_quant,","), 'pre_value': 0})
    result.append({'subject': '평균거래량', 'value': format(int((sum_acc_quant - int(max_info.get('max_tr_quant'))) / (real_cnt-1)), ","), 'pre_value': 0})
    result.append({'subject': '외국인 평단(종가)', 'value': format(int(sum_frgn_unit_price/sum_frgn_pure_buy_quant),","), 'pre_value': 0})
    result.append({'subject': '기관 평단(종가)', 'value': format(int(sum_organ_unit_price/sum_organ_pure_buy_quant),","), 'pre_value': 0})
    result.append({'subject': '개인 평단(종가)', 'value': format(int(sum_indi_unit_price/sum_indi_pure_buy_quant),","), 'pre_value': 0})
    result.append({'subject': '거래량 평단(종가)', 'value': format(int(sum_total_unit_price/sum_acc_quant),","), 'pre_value': 0})

    end_price_ratio = int((int(sum_indi_unit_price / sum_indi_pure_buy_quant) - today_price) / today_price * 100)
    end_price_ratio_str = "종가 : " + str(format(today_price, ",")) + " / " + str(end_price_ratio) + "%"
    result.append({'subject': '비율(종가)', 'value': end_price_ratio_str, 'pre_value': ''})

    result.append({'subject': '외국인 평단(평균가)', 'value': format(int(sum_frgn_unit_avg_price / sum_frgn_pure_buy_quant), ","),'pre_value': 0})
    result.append({'subject': '기관 평단(평균가)', 'value': format(int(sum_organ_unit_avg_price / sum_organ_pure_buy_quant), ","), 'pre_value': 0})
    result.append({'subject': '개인 평단(평균가)', 'value': format(int(sum_indi_unit_avg_price / sum_indi_pure_buy_quant), ","), 'pre_value': 0})
    result.append({'subject': '거래량 평단(평균가)', 'value': format(int(sum_total_unit_avg_price / sum_acc_quant), ","), 'pre_value': 0})

    today_price_ratio = int((int(sum_indi_unit_avg_price / sum_indi_pure_buy_quant) - today_price) / today_price * 100)
    today_price_ratio_str = "종가 : " + str(format(today_price, ",")) + " / " + str(today_price_ratio)+"%"
    result.append({'subject': '비율(평균가)', 'value': today_price_ratio_str, 'pre_value': ''})
    return_value.setdefault('result', result)

    max_info['max_tr_ratio'] = round(float(int(max_info.get('max_tr_quant')) / int(max_info.get('tot_tr_quant')))*100, 2)
    max_info["max_cir_ratio"] = round(float(int(max_info["max_tr_quant"]) / int(company_detail_info.get("cir_stock_cnt"))*100), 2)
    max_info["tot_cir_ratio"] = round(float(int(max_info["tot_tr_quant"]) / int(company_detail_info.get("cir_stock_cnt")) * 100), 2)
    max_info['max_tr_quant'] = format(int(max_info.get('max_tr_quant')), ",")
    max_info['tot_tr_quant'] = format(int(max_info.get('tot_tr_quant')), ",")
    return_value.setdefault('max_info', max_info)

    company_detail_info['tot_stock_cnt'] = format(company_detail_info.get('tot_stock_cnt'), ",")
    company_detail_info['cir_stock_cnt'] = format(company_detail_info.get('cir_stock_cnt'), ",")
    return_value.setdefault('company_detail_info', company_detail_info)

    return return_value


#print("종목코드를 입력하세요 ↓↓↓↓")
#item_code = input()
#print("조회 시작일자를 입력하세요 ↓↓↓↓")
#start_date = input()

#getSise(item_code, start_date)

def getCompanyDetailInfo(code):

    return_result = {"tot_stock_cnt": 0, "cir_stock_ratio": 0.0, "cir_stock_cnt": 0}
    base_url = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=' + code
    res = requests.get(base_url)

    soup = BeautifulSoup(res.content, 'html.parser')
    result = soup.select("#cTB11 > tbody > tr:nth-child(7) > td")

    result_list = result[0].text.strip().split("/")
    tot_stock_cnt = int(result_list[0].replace("주", "").replace(",", ""))
    cir_stock_ratio = float(result_list[1].replace("%", "").strip())
    cir_stock_cnt = int(tot_stock_cnt * cir_stock_ratio / 100)

    #return_result['tot_stock_cnt'] = format(tot_stock_cnt, ",")
    #return_result['cir_stock_ratio'] = cir_stock_ratio
    #return_result['cir_stock_cnt'] = format(cir_stock_cnt, ",")
    return_result['tot_stock_cnt'] = tot_stock_cnt
    return_result['cir_stock_ratio'] = cir_stock_ratio
    return_result['cir_stock_cnt'] = cir_stock_cnt

    return return_result