#-------------- history --------------
# 2020.05.29  신규 생성
# 주의사항 : pymysql 을 이용하여 변수 입력하는 부분 잘 볼 것
import database
from flask import request, Blueprint, jsonify

stats_bp = Blueprint('stats_bp', __name__)

@stats_bp.route("/stats", methods=['GET'])
def getStatsDb():
    print("Start getStatsDb")
    try:
        db_class = database.Database()
    except Exception as ex:
        print("에러 발생 : {}".format(ex))

    print("Start getStatsDb222")
    # jongmok_code
    # tr_date
    # ind_tr_cnt
    # ind_avg_avg_amt
    # fin_amt
    # max_cir_ratio : 하루거래량 / 유통주식수
    # tot_cir_ratio : 총거래량 / 유통주식수
    jongmok_code = request.args.get('item')
    if jongmok_code == "":
        jongmok_code = "%%"

    tr_date = request.args.get('tr_date')
    max_cir_ratio = float(request.args.get('max_cir_ratio'))
    tot_cir_ratio = float(request.args.get('tot_cir_ratio'))

    print("jongmok_code1 : {}".format(jongmok_code))
    print("tr_date1 : {}".format(tr_date))
    print("max_cir_ratio1 : {}".format(max_cir_ratio))
    print("tot_cir_ratio1 : {}".format(tot_cir_ratio))
    data = tr_date, jongmok_code, max_cir_ratio, tot_cir_ratio

    sql = "SELECT jongmok_code, company_name, DATE_FORMAT(start_date,'%%Y-%%m-%%d') AS start_date, " \
    "ind_tr_cnt, ind_avg_avg_amt, fin_amt, max_cir_ratio, tot_cir_ratio "\
    "FROM tb_l_jongmok_stat " \
    "WHERE tr_date=%s " \
    "AND jongmok_code LIKE %s " \
    "AND max_cir_ratio > %s " \
    "AND tot_cir_ratio > %s " \
    "AND ind_avg_avg_amt > fin_amt " \
    "AND ind_tr_cnt > 0 " \
    "ORDER BY (ind_avg_avg_amt / fin_amt) DESC"

    result = db_class.execute_all(sql, data)
    print(result)

    return jsonify(result)
