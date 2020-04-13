import pymysql
import os
import database

def getCodeInfo(code):
    db_class = database.Database()
    res = []

    sql = "select * from tb_m_jongmok where jongmok_code='%s'" % (code)
    result = db_class.execute_all(sql)
    print(result)

    res.append({'subject': '회사명', 'value': result[0].get('company_name')})
    res.append({'subject': '업종', 'value': result[0].get('business_kind')})
    res.append({'subject': '메인상품', 'value': result[0].get('main_product')})
    res.append({'subject': '대표명', 'value': result[0].get('ceo_name')})
    res.append({'subject': '홈페이지', 'value': result[0].get('homepage')})

    return res

def getCodeName(code_name):
    db_class = database.Database()

    sql = "select * from tb_m_jongmok where company_name = '%s'" % (code_name)
    result = db_class.execute_all(sql)

    print(result)

    return result[0].get('jongmok_code')

#getCodeInfo("086980")
