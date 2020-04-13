import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def getSise(item_code, start_date, end_date):
    # 정보를 가져오기 위한 url
    url = 'https://m.stock.naver.com/api/item/getTrendList.nhn'

    # 2016 ~ 2020년도의 휴장일
    df = pd.DataFrame({'hdays':['2020-01-01','2020-01-24','2020-01-27','2020-04-15',
                              '2020-04-30','2020-05-01','2020-05-05','2020-09-30','2020-10-01',
                              '2020-10-02','2020-10-09','2020-12-25','2020-12-31',
                              '2019-01-01','2019-02-04','2019-02-05','2019-02-06','2019-03-01',
                              '2019-05-01','2019-05-06','2019-06-06','2019-08-15','2019-09-12','2019-09-13',
                              '2019-10-03','2019-10-09','2019-12-25','2019-12-31','2018-01-01','2018-02-15',
                              '2018-02-16','2018-03-01','2018-05-01','2018-05-07','2018-05-22','2018-06-06',
                              '2018-06-13','2018-08-15','2018-09-24','2018-09-25','2018-09-26','2018-10-03',
                              '2018-10-09','2018-12-25','2018-12-31','2017-01-27','2017-01-30','2017-03-01',
                              '2017-05-01','2017-05-03','2017-05-05','2017-05-09','2017-06-06','2017-08-15',
                              '2017-10-02','2017-10-03','2017-10-04','2017-10-05','2017-10-06','2017-10-09',
                              '2017-12-25','2017-12-29','2016-01-01','2016-02-08','2016-02-09','2016-02-10',
                              '2016-03-01','2016-04-13','2016-05-05','2016-05-06','2016-06-06','2016-08-15',
                              '2016-09-14','2016-09-15','2016-09-16','2016-10-03','2016-12-30']})
    hdays = pd.to_datetime(df['hdays'])

    # 입력받은 일자 ~ 현재일자까지의 영업일 리스트
    start_date = pd.to_datetime(start_date)
    tday = pd.to_datetime(datetime.today().strftime("%Y%m%d"))

    # end_date 가 입력되지 않았으면 오늘날짜로
    if end_date == "":
        end_date = tday
    else:
        end_date = pd.to_datetime(end_date)

    print("start_date : {}".format(start_date))
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

    sum_real_frgn_pure_buy_quant = 0
    sum_real_organ_pure_buy_quant = 0
    sum_real_indi_pure_buy_quant = 0

    sum_frgn_pure_buy_quant = 0
    sum_organ_pure_buy_quant = 0
    sum_indi_pure_buy_quant = 0

    sum_frgn_unit_price = 0
    sum_organ_unit_price = 0
    sum_indi_unit_price = 0

    sum_acc_quant = 0
    sum_total_unit_price = 0

    max_info = {"max_tr_quant": 0,
                "max_tr_date": "",
                "max_tr_ratio": 0.0,
                "tot_tr_quant": 0,
                "max_cir_ratio": 0.0,
                "tot_cir_ratio": 0.0}

    for row in res['result']:
      sum_acc_quant += row['acc_quant']
    #print("sum_acc_quant : {}".format(sum_acc_quant))

    # 유통주식수 구하기 (getTest 참조)
    company_detail_info = getCompanyDetailInfo(item_code)
    #print(company_detail_info)
    max_info['tot_tr_quant'] = sum_acc_quant

    for row in res['result']:
        biz_date = row['bizdate']
        biz_date = pd.to_datetime(biz_date)
        if end_date < biz_date:
            continue

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
        #print("organ_pure_buy_quant :{}".format(row['organ_pure_buy_quant'] * ratio))

        frgn_unit_price = row['frgn_pure_buy_quant'] * row['close_val'] * ratio
        organ_unit_price = row['organ_pure_buy_quant'] * row['close_val'] * ratio
        indi_unit_price = row['indi_pure_buy_quant'] * row['close_val'] * ratio
        #print("organ_pure_buy_quant : {}".format(row['organ_pure_buy_quant']))
        #print("ratio : {}".format(ratio))
        #print("organ_utni_price : {}".format(row['organ_pure_buy_quant'] * row['close_val'] * ratio))
        sum_frgn_unit_price += frgn_unit_price
        sum_organ_unit_price += organ_unit_price
        sum_indi_unit_price += indi_unit_price

        sum_total_unit_price += row['acc_quant'] * row['close_val']

    #print("외국인 보유 주수 : {}".format(sum_real_frgn_pure_buy_quant))
    #print("기관 보유 주수 : {}".format(sum_real_organ_pure_buy_quant))
    #print("개인 보유 주수 : {}".format(sum_real_indi_pure_buy_quant))
    #print("외국인 평단 : {}".format(sum_frgn_unit_price/sum_frgn_pure_buy_quant))
    #print("기관 평단 : {}".format(sum_organ_unit_price/sum_organ_pure_buy_quant))
    #print("개인 평단 : {}".format(sum_indi_unit_price/sum_indi_pure_buy_quant))
    #print("거래량별 평단 : {}".format(sum_total_unit_price/sum_acc_quant))
    return_value = {}

    max_info['max_tr_ratio'] = round(float(int(max_info.get('max_tr_quant')) / int(max_info.get('tot_tr_quant')))*100, 2)
    max_info["max_cir_ratio"] = round(float(int(max_info["max_tr_quant"]) / int(company_detail_info.get("cir_stock_cnt"))*100), 2)
    max_info["tot_cir_ratio"] = round(
        float(int(max_info["tot_tr_quant"]) / int(company_detail_info.get("cir_stock_cnt")) * 100), 2)
    max_info['max_tr_quant'] = format(int(max_info.get('max_tr_quant')), ",")
    max_info['tot_tr_quant'] = format(int(max_info.get('tot_tr_quant')), ",")
    return_value.setdefault('max_info', max_info)

    company_detail_info['tot_stock_cnt'] = format(company_detail_info.get('tot_stock_cnt'), ",")
    company_detail_info['cir_stock_cnt'] = format(company_detail_info.get('cir_stock_cnt'), ",")
    return_value.setdefault('company_detail_info', company_detail_info)
    print(max_info)

    result = []
    result.append({'subject': '외국인', 'value': format(sum_real_frgn_pure_buy_quant,","), 'pre_value': 0})
    result.append({'subject': '기관', 'value': format(sum_real_organ_pure_buy_quant,","), 'pre_value': 0})
    result.append({'subject': '개인', 'value': format(sum_real_indi_pure_buy_quant,","), 'pre_value': 0})
    result.append({'subject': '가중치 외국인 평단', 'value': format(int(sum_frgn_unit_price/sum_frgn_pure_buy_quant),","), 'pre_value': 0})
    result.append({'subject': '가중치 기관 평단', 'value': format(int(sum_organ_unit_price/sum_organ_pure_buy_quant),","), 'pre_value': 0})
    result.append({'subject': '가중치 개인 평단', 'value': format(int(sum_indi_unit_price/sum_indi_pure_buy_quant),","), 'pre_value': 0})
    result.append({'subject': '가중치 거래량 평단', 'value': format(int(sum_total_unit_price/sum_acc_quant),","), 'pre_value': 0})
    #print(result)
    return_value.setdefault('result', result)

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