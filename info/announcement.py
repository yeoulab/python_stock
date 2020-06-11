##########################################
# 프로그램 설명 : krx 공시정보 api 호출    #
##########################################
import requests
import pandas as pd
from datetime import datetime
import json
import xmltodict

def getDisList(item_code):
    url = 'http://asp1.krx.co.kr/servlet/krx.asp.DisList4MainServlet'

    params = {'code': item_code, 'gubun': 'K'}
    #print("params: {}".format(params))
    response = requests.get(url, params=params)
    print(response.text[2])

    # strip 을 써서 공백을 지운다
    jsonString = json.dumps(xmltodict.parse(response.text.strip()))

    print(jsonString)

getDisList('086980')