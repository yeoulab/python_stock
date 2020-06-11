import database
from flask import request, Blueprint, jsonify

diary_bp = Blueprint('diary_bp', __name__)

@diary_bp.route("/diary", methods=['GET', 'POST', 'PUT', 'DELETE'])
def process_diary():
    print("METHOD 종류 : {}".format(request.method))
    try:
        db_class = database.Database()
    except Exception as ex:
        print("에러 발생 : {}".format(ex))

    input_body = request.get_json()
    result = {}

    if request.method == 'GET':
        sql = "SELECT jongmok_code, DATE_FORMAT(start_date,'%Y-%m-%d') AS start_date, " \
              "company_name, buy_reason, sell_reason, suc_reason, fail_reason FROM tb_l_diary"
        result = db_class.execute_all(sql, None)

    elif request.method == 'POST':
        str_space = ""
        sql = "INSERT INTO tb_l_diary VALUES('%s','%s','%s','%s','%s','%s','%s')" \
              % (input_body.get('jongmok_code'), input_body.get('start_date'), input_body.get('company_name'), input_body.get('buy_reason'),
                 str_space,str_space,str_space)
        db_class.execute(sql)
        db_class.commit()

    elif request.method == 'PUT':
        print("Start updateDiaryDb")
        start_date = input_body.get('start_date').replace("-","")
        sql = "UPDATE tb_l_diary SET buy_reason='%s', sell_reason='%s', suc_reason='%s', fail_reason='%s' " \
              "WHERE jongmok_code='%s' AND start_date='%s'" % (input_body.get('buy_reason'), input_body.get('sell_reason'), input_body.get('suc_reason'), input_body.get('fail_reason'), input_body.get('jongmok_code'), start_date)
        db_class.execute(sql)
        db_class.commit()

    return jsonify(result)
