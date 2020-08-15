import database
from flask import request, Blueprint, jsonify

theme_item_bp = Blueprint('theme_item_bp', __name__)

@theme_item_bp.route("/themeItem", methods=['GET', 'POST', 'PUT', 'DELETE'])
def process_theme_item():
    print("process_theme_item 시작")
    print("METHOD 종류 : {}".format(request.method))
    try:
        db_class = database.Database()
    except Exception as ex:
        print("에러 발생 : {}".format(ex))

    input_body = request.get_json()
    result = {}

    if request.method == 'GET':
        sql = "SELECT t.theme_id, t.item_code, j.company_name " \
              "FROM tb_l_theme_item as t, tb_m_jongmok as j " \
              "WHERE t.theme_id = %s " \
              "AND t.item_code = j.jongmok_code" % (request.args.get('theme_id'))
        print("result : {}".format(result))
        result = db_class.execute_all(sql, None)

    elif request.method == 'POST':
        sql = "INSERT INTO tb_l_theme_item(theme_id, item_code) VALUES('%s', '%s')" \
              % (input_body.get('theme_id'), input_body.get('item_code'))
        db_class.execute(sql)
        db_class.commit()

    elif request.method == 'DELETE':
        print("theme_id : {}".format(request.args.get('theme_id')));
        print("item_code : {}".format(request.args.get('item_code')));
        sql = "DELETE FROM tb_l_theme_item WHERE theme_id = %s AND item_code = '%s'" \
              % (request.args.get('theme_id'), request.args.get('item_code'))
        db_class.execute(sql)

        # theme item 삭제 시, 기존에 저장돼 있던 계산내역도 같이 삭제한다.
        calc_del_sql = "DELETE FROM tb_l_theme_jongmok_stat WHERE jongmok_code = '%s'" \
              % (request.args.get('item_code'))
        db_class.execute(calc_del_sql)
        db_class.commit()

    return jsonify(result)
