import requests
import pandas as pd
from datetime import datetime

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
    #print("params: {}".format(params))
    response = requests.get(url, params=params)
    res = response.json()
    #print(response.json())
    #print(len(response['result']))
    #print(response['result'][0]['change_val'])


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

    for row in res['result']:
      sum_acc_quant += row['acc_quant']
    #print("sum_acc_quant : {}".format(sum_acc_quant))

    for row in res['result']:
        biz_date = row['bizdate']
        biz_date = pd.to_datetime(biz_date)
        if end_date < biz_date:
            continue

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


    print("외국인 보유 주수 : {}".format(sum_real_frgn_pure_buy_quant))
    print("기관 보유 주수 : {}".format(sum_real_organ_pure_buy_quant))
    print("개인 보유 주수 : {}".format(sum_real_indi_pure_buy_quant))
    print("외국인 평단 : {}".format(sum_frgn_unit_price/sum_frgn_pure_buy_quant))
    print("기관 평단 : {}".format(sum_organ_unit_price/sum_organ_pure_buy_quant))
    print("개인 평단 : {}".format(sum_indi_unit_price/sum_indi_pure_buy_quant))
    print("거래량별 평단 : {}".format(sum_total_unit_price/sum_acc_quant))

    return_value = {}
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
