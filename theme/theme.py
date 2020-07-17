# Diary 에 저장하는 모듈
# status 관리 필요
import database
from flask import request, Blueprint, jsonify

theme_bp = Blueprint('theme_bp', __name__)

@theme_bp.route("/theme", methods=['GET', 'POST', 'PUT', 'DELETE'])
def process_theme():
    print("METHOD 종류 : {}".format(request.method))
    try:
        db_class = database.Database()
    except Exception as ex:
        print("에러 발생 : {}".format(ex))

    input_body = request.get_json()
    print("input_body : {}".format(input_body))
    result = {}

    if request.method == 'GET':
        sql = "SELECT * FROM tb_m_theme"
        result = db_class.execute_all(sql, None)

    elif request.method == 'POST':
        str_space = ""
        sql = "INSERT INTO tb_m_theme(theme_name) VALUES('%s')" \
              % (input_body.get('theme_name'))
        db_class.execute(sql)
        db_class.commit()

    elif request.method == 'PUT':
        sql = "UPDATE tb_m_theme SET theme_name='%s' " \
              "WHERE id='%s'" % (input_body.get('id'), input_body.get('theme_name'))
        db_class.execute(sql)
        db_class.commit()

    elif request.method == 'DELETE':
        print("/theme 내 delete 메소드 호출")
        sql = "DELETE FROM tb_m_theme WHERE id=%s" % (request.args.get('id'))
        db_class.execute(sql)
        sql2 = "DELETE FROM tb_l_theme_item where them_id=%s" %  (request.args.get('id'))
        db_class.execute(sql2)
        db_class.commit()

    return jsonify(result)
