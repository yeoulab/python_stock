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
    input_body = request.get_json()
    result = {}

    # GET 은 계산 결과 조회
    if request.method == 'GET':
        print("theme Id : {}".format(request.args.get('theme_id')))
        search_sql = "SELECT a.company_name, a.jongmok_code, a.max_cir_ratio, a.tot_cir_ratio, DATE_FORMAT(a.start_date, '%Y-%m-%d') AS start_date " \
                     "FROM tb_l_theme_jongmok_stat as a, tb_l_theme_item as b " \
                     "WHERE a.jongmok_code = b.item_code AND b.theme_id = '" + (request.args.get('theme_id')) + "'"
        print("search_sql : {}".format(search_sql))
        result = db_class.execute_all(search_sql, None)
        print("GET result : {}".format(result))

    elif request.method == 'POST':
        item_sql = "SELECT t.theme_id, t.item_code, j.company_name " \
              "FROM tb_l_theme_item as t, tb_m_jongmok as j " \
              "WHERE t.theme_id = %s " \
              "AND t.item_code = j.jongmok_code" % (input_body.get('theme_id'))
        result = db_class.execute_all(item_sql, None)
        print("result : {}".format(result))
        # 테마주로 검색

        check_sql = "SELECT jongmok_code FROM tb_l_theme_jongmok_stat WHERE jongmok_code = '%s'"

        sql = "INSERT INTO tb_l_theme_jongmok_stat VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'" \
              ",'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
        print("11111111111111")
        # 시작일자를 어떻게 정할 것인가?
        # 1. 직전 6개월 ~ 직전 1개월 이내에 거래량이 가장 많은 일자
        tday = pd.to_datetime(datetime.today().strftime("%Y%m%d")) # 오늘날짜
        now_before_six_month = tday + timedelta(days=-180) # 6개월 전

        print("222222222222")
        # 2. 직전 6개월 ~ 현재 까지의 일수를 구함
        mdays = pd.date_range(now_before_six_month, tday, freq='B')

        # 3. 휴장일 제외
        # 영업일 리스트에서 휴장일을 제외
        hdays = const.hdays
        for hday in hdays:
            if now_before_six_month <= hday <= tday:
                mdays = mdays.drop(hday)

        # theme Item 돌면서
        # 거래량 구하기
        print("for 문 전 시작")
        url = 'https://m.stock.naver.com/api/item/getPriceDayList.nhn'
        for item in result:
            # 계산된 이력이 있는지 확인
            print("itme : {}".format(item['item_code']))
            check_sql2 = check_sql % (item['item_code'])
            print("check_sql : {}".format(check_sql2))
            chk_result = db_class.execute_all(check_sql2, None)
            print("chk_result : {}".format(len(chk_result)))

            # 계산된 이력이 DB 에 저장 돼 있으면 continue 한다.
            if len(chk_result) > 0:
                print("이미 존재함")
                continue
            print("3")
            # PER 이 '+' 인 회사만 가져온다.
            per_plus_yn = const.check_per(item['item_code'])

            # 2020/06/10 PER + check
            if not per_plus_yn:
                time.sleep(0.1)
                continue
            print("4")
            # 총거래량 / 유통주식수가 400% 일 때의 시작일자를 구하기 위해 한번 더 메소드를 호출한다.
            company_detail_info = getSise.getCompanyDetailInfo(item['item_code'])
            cir_stock_cnt = int(company_detail_info.get("cir_stock_cnt"))  # 유통 거래량

            # 직전 6개월 ~ 현재 까지의 가격 구하기
            params = {'code': item['item_code'], 'pageSize': len(mdays)}
            response = requests.get(url, params=params)
            res = response.json()
            print("5")
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
            print("6")
            res = getSise.getSise(item['item_code'], max_tr_dt, tday)

            i = 0
            result_list = []
            print("7")
            for data in res['result']:
                print(data)
                if i == 8:
                    result_list.append(int(data['value'].split('/')[0].split(':')[1].replace(",", "")))
                else:
                    result_list.append(int(data['value'].replace(",", "")))

                i = i + 1

            max_info = res['max_info']
            com_info = res['company_detail_info']
            print("8")
            insert_sql = sql % (item['item_code']  # jongmok_code
                                , max_tr_dt  # start_date
                                , item['company_name']  # company_name
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

            #logging.log(logging.INFO, insert_sql)
            print("9")
            db_class.execute(insert_sql)
            db_class.commit()
            time.sleep(0.5)

    return jsonify(result)
