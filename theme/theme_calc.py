import database
from flask import request, Blueprint, jsonify
import common.const as const
import pandas as pd
import time
from datetime import datetime, timedelta
import logging
import requests
import getSise

theme_calc_bp = Blueprint('theme_calc_bp', __name__)

@theme_calc_bp.route("/themeCalc", methods=['GET', 'POST', 'PUT', 'DELETE'])
def calc_theme():
    print("themeCalc 시작")
    print("METHOD 종류 : {}".format(request.method))

    db_class = database.Database()

    if request.method == 'GET':
        item_sql = "SELECT t.theme_id, t.item_code, j.company_name " \
              "FROM tb_l_theme_item as t, tb_m_jongmok as j " \
              "WHERE t.theme_id = %s " \
              "AND t.item_code = j.jongmok_code" % (request.args.get('theme_id'))
        result = db_class.execute_all(item_sql, None)

        # 테마주로 검색
        res = result.json()

        check_sql = "SELECT count(*) FROM tb_l_jongmok_stat WHERE jongmok_code = '%s' AND tr_date = '%s' AND start_date = '%s'"

        sql = "INSERT INTO tb_l_jongmok_stat VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'" \
              ",'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"



        # 시작일자를 어떻게 정할 것인가?
        # 1. 직전 6개월 ~ 직전 1개월 이내에 거래량이 가장 많은 일자
        tday = pd.to_datetime(datetime.today().strftime("%Y%m%d"))
        now_before_six_month = tday + timedelta(days=-180)
        now_before_one_month = tday + timedelta(days=-30)

        # 2. 직전 6개월 ~ 현재 까지의 일수를 구함
        mdays = pd.date_range(now_before_six_month, tday, freq='B')

        # 3. 휴장일 제외
        # 영업일 리스트에서 휴장일을 제외
        hdays = const.hdays
        for hday in hdays:
            if now_before_six_month <= hday <= tday:
                mdays = mdays.drop(hday)

        # 거래량 구하기
        url = 'https://m.stock.naver.com/api/item/getPriceDayList.nhn'
        for item in res['result']['itemList']:
            # PER 이 '+' 인 회사만 가져온다.
            per_plus_yn = const.check_per(item['cd'])

            # 2020/06/10 PER + check
            if not per_plus_yn:
                time.sleep(0.1)
                continue

            # 총거래량 / 유통주식수가 400% 일 때의 시작일자를 구하기 위해 한번 더 메소드를 호출한다.
            company_detail_info = getSise.getCompanyDetailInfo(item['cd'])
            cir_stock_cnt = int(company_detail_info.get("cir_stock_cnt"))  # 유통 거래량

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

            # 최근 6개월 이내에 400% 가 안됐다면, 6개월 전 날자로 세팅
            if max_tr_dt == "":
                max_tr_dt = now_before_six_month


            db_class.execute(check_sql, item['cd'], max_tr_dt, tday);

            res = getSise.getSise(item['cd'], max_tr_dt, tday)

            i = 0
            result_list = []
            for data in res['result']:
                if i == 8:
                    result_list.append(int(data['value'].split('/')[0].split(':')[1].replace(",", "")))
                else:
                    result_list.append(int(data['value'].replace(",", "")))
                i = i + 1

            max_info = res['max_info']
            com_info = res['company_detail_info']

            insert_sql = sql % (item['cd']  # jongmok_code
                                , tday  # tr_date
                                , max_tr_dt  # start_date
                                , item['nm']  # company_name
                                , result_list[0]  # for_tr_cnt
                                , result_list[1]  # ins_tr_cnt
                                , result_list[2]  # ind_tr_cnt
                                , result_list[3]  # avg_tr_cnt
                                , 0  # result_list[4] # for_avg_fin_amt
                                , 0  # result_list[5]  # ins_avg_fin_amt
                                , 0  # result_list[6] # ind_avg_fin_amt
                                , 0  # result_list[7] # tr_avg_fin_amt
                                , result_list[8]  # fin_amt
                                , result_list[4]  # for_avg_avg_amt
                                , result_list[5]  # ins_avg_avg_amt
                                , result_list[6]  # ind_avg_avg_amt
                                , result_list[7]  # tr_avg_avg_amt
                                , int(max_info['max_tr_quant'].replace(",", ""))  # max_tr_qunat
                                , str(max_info['max_tr_date'].replace("-", ""))  # max_tr_date
                                , float(max_info['max_tr_ratio'])  # max_tr_ratio
                                , int(max_info['tot_tr_quant'].replace(",", ""))  # tot_tr_quant
                                , float(max_info['max_cir_ratio'])  # max_cir_ratio
                                , float(max_info['tot_cir_ratio'])  # tot_cir_ratio
                                , int(com_info['tot_stock_cnt'].replace(",", ""))  # tot_stock_cnt
                                , float(com_info['cir_stock_ratio'])  # cir_stock_ratio
                                , int(com_info['cir_stock_cnt'].replace(",", ""))  # cir_stock_cnt
                                )

            logging.log(logging.INFO, insert_sql)
            db_class.execute(insert_sql)
            db_class.commit()
            time.sleep(0.5)

        return jsonify(result)
