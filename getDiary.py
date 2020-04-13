import database
from flask import request

def getDiaryDb():
    db_class = database.Database()

    sql = "SELECT jongmok_code, DATE_FORMAT(START_DATE,'%Y-%m-%d') AS start_date, " \
          "company_name, buy_reason, sell_reason, suc_reason, fail_reason FROM TB_L_DIARY"
    result = db_class.execute_all(sql)
    print(result)

    return result

def insertDiaryDb(data):
    values = request.get_json()
    print(data)
    print(data.get('sell_reason'))
    db_class = database.Database()
    str_space = ""
    sql = "INSERT INTO TB_L_DIARY VALUES('%s','%s','%s','%s','%s','%s','%s')" \
          % (data.get('jongmok_code'), data.get('start_date'), data.get('company_name'),data.get('buy_reason'),
             str_space,str_space,str_space)
    db_class.execute(sql)
    db_class.commit()

def updateDiaryDb(data):
    print(data)
    db_class = database.Database()
    start_date = data.get('start_date').replace("-","")
    sql = "UPDATE TB_L_DIARY SET BUY_REASON='%s', SELL_REASON='%s', SUC_REASON='%s', FAIL_REASON='%s' " \
          "WHERE JONGMOK_CODE='%s' AND START_DATE='%s'" % (data.get('buy_reason'), data.get('sell_reason'), data.get('suc_reason'), data.get('fail_reason'), data.get('jongmok_code'), start_date)
    print(sql)
    db_class.execute(sql)
    db_class.commit()