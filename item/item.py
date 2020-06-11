import pymysql
import os
import database
from flask import request, Blueprint, jsonify

item_bp = Blueprint('item_bp', __name__)

@item_bp.route("/info", methods=['GET'])
def getCodeInfo():
    print("Start getcodeInfo")
    try:
        db_class = database.Database()
    except Exception as ex:
        print("에러 발생 : {}".format(ex))

    item = request.args.get("item_code")
    res = []

    sql = "select * from tb_m_jongmok where jongmok_code=%s" #% (code)
    result = db_class.execute_all(sql, item)
    print(result)

    res.append({'subject': '회사명', 'value': result[0].get('company_name')})
    res.append({'subject': '업종', 'value': result[0].get('business_kind')})
    res.append({'subject': '메인상품', 'value': result[0].get('main_product')})
    res.append({'subject': '대표명', 'value': result[0].get('ceo_name')})
    res.append({'subject': '홈페이지', 'value': result[0].get('homepage')})

    return jsonify(res)

@item_bp.route("/code", methods=['GET'])
def getCodeName():
    db_class = database.Database()
    item_name = request.args.get("item_name")
    sql = "select * from tb_m_jongmok where company_name = %s"# % (code_name)
    result = db_class.execute_all(sql, item_name)

    return jsonify(result[0].get('jongmok_code'))

#getCodeInfo("086980")
