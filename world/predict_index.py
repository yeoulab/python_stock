# 다우지수, 나스닥, 달러, 금, 유가, 선물 -> KOSPI, KOSDAQ 예측

# 다우 https://m.stock.naver.com/api/json/world/worldIndexDay.nhn?symbol=DJI@DJI&pageSize=20&page=200
# 나스닥 https://m.stock.naver.com/api/json/world/worldIndexDay.nhn?symbol=NAS@IXIC&pageSize=20&page=200
# 달러 - api 불가 https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW&page=1
# 금  - api 불가 https://finance.naver.com/marketindex/goldDailyQuote.nhn?&page=2
# 서부텍사스유  - api 불가 https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=OIL_CL&fdtc=2&page=2
# td - class="pgRR" a href 의 page 값
# 선물  - api 불가
# KOSPI https://m.stock.naver.com/api/json/sise/dailySiseIndexListJson.nhn?code=KOSPI&pageSize=20&page=300
# KOSDAQ https://m.stock.naver.com/api/json/sise/dailySiseIndexListJson.nhn?code=KOSDAQ&pageSize=20&page=300
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers import LSTM

import requests
import database
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify


# 20 개의 데이터로 1개의 미래데이터를 예측하기 위한 data set
def make_dataset(data, label, window_size=20):
    feature_list = []
    label_list = []
    for i in range(len(data) - window_size):
        feature_list.append(np.array(data.iloc[i:i+window_size]))
        label_list.append(np.array(label.iloc[i+window_size]))
    return np.array(feature_list), np.array(label_list)

# 정규화 작업한 부분을 역정규화 해주는 메소드
def make_unnomalization(data, min, max):
    unnomalization_list = []
    for i in range(len(data)-1):
        unnomalization_list.append(data[i][0] * (max - min) + min)

    return np.array(unnomalization_list)

def predict_stock():
    # 데이터 로드하기
    TEST_LENGTH = 200 # 학습으로 예측치 구하기
    WINDOW_SIZE = 20 # 몇개 단위로 예측할 것인지

    # csv 에서 데이터 읽어오기
    df_price = pd.read_csv(os.path.join('D:/11. Python Code/predict_stock', 'sec_asc.csv'), encoding='utf8')
    # 날짜를 구하기 위해 TEST_LENGTH 만큼 array 저장
    test_price = df_price[-TEST_LENGTH:]

    # 그래프 x 축
    x_axis = []

    # len(df_price) = 9288 / TEST_LENGTH = 200 / 9288 - 200 = 9088 + 20(window size) -> TEST_LENGTH - window size 만큼
    test_price['tr_date'][len(df_price) - TEST_LENGTH]
    for i in range(TEST_LENGTH - WINDOW_SIZE - 1):
        x_axis.append(pd.to_datetime(str(test_price['tr_date'][len(df_price) - TEST_LENGTH + i]), format='%Y%m%d'))

    # 역정규화를 위해 종가의 min/max 값 세팅
    end_amt_max = int(df_price.describe()['end_amt']['max'])
    end_amt_min = int(df_price.describe()['end_amt']['min'])

    # -1 ~ 1 사이로의 정규화
    scaler = MinMaxScaler()
    #scale_cols = ['시가','고가','저가','종가','거래량']
    scale_cols = ['start_amt','hi_amt','low_amt','end_amt','tr_cnt']
    df_scaled = scaler.fit_transform(df_price[scale_cols])
    df_scaled = pd.DataFrame(df_scaled)
    df_scaled.columns = scale_cols

    # data 의 column 명 세팅
    feature_cols = ['start_amt','hi_amt','low_amt','tr_cnt']
    label_cols = ['end_amt']

    train = df_scaled[:-TEST_LENGTH] # 과거 ~ 200일 전
    test = df_scaled[-TEST_LENGTH:] # 실제 데이터 200일 전 ~ 현재

    # 시가/고가/저가/거래량(입력 데이터)
    train_feature = train[feature_cols]
    # 종가(결과 데이터)
    train_label = train[label_cols]
    # feature(입력) 을 20개 씩 묶고, label(결과) 도 20개씩 묶는다
    train_feature, train_label = make_dataset(train_feature, train_label, 20)

    x_train, x_valid, y_train, y_valid = train_test_split(train_feature, train_label, test_size=0.2)

    # 학습의 input 을 위한 test_feature 와 비교를 위한 test_label
    test_feature = test[feature_cols]
    test_label = test[label_cols]
    test_feature, test_label = make_dataset(test_feature, test_label, 20)

    #선형 모델을 선언
    model = Sequential()

    # 모델에 대한 구체적인 입력값을 넣는다.
    model.add(LSTM(
         16,
         input_shape=(train_feature.shape[1], train_feature.shape[2]),
         activation='relu',
         return_sequences=False)
    )
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    early_stop = EarlyStopping(monitor='val_loss', patience=5)
    filename = os.path.join('D:/11. Python Code/predict_stock', 'tmp_checkpoint.h5')
    checkpoint = ModelCheckpoint(filename, monitor='val_loss', verbose=1, save_best_only=True, mode='auto')
    # #
    history = model.fit(x_train, y_train, epochs=200, batch_size=16,
                          validation_data=(x_valid, y_valid),
                          callbacks=[early_stop, checkpoint])
    #
    model.load_weights(filename)

    # 모델에 input data 를 넣는다.
    pred = model.predict(test_feature)
    un_pred = make_unnomalization(pred, end_amt_min, end_amt_max)
    un_test_label = make_unnomalization(test_label, end_amt_min, end_amt_max)

    # 그래프 그리기
    plt.figure(figsize=(12, 9))
    plt.plot(x_axis, un_test_label, label='actual')
    plt.plot(x_axis, un_pred, label='prediction')
    plt.legend()
    plt.show()

def predict_stock_for_kospi():
    # 데이터 로드하기
    TEST_LENGTH = 200 # 학습으로 예측치 구하기
    WINDOW_SIZE = 20 # 몇개 단위로 예측할 것인지

    # csv 에서 데이터 읽어오기
    df_price = getDatafromDatabase()
    #print(len(df_price))
    # 날짜를 구하기 위해 TEST_LENGTH 만큼 array 저장
    test_price = df_price[-TEST_LENGTH:]

    #print(len(test_price))
    #print(test_price)

    # 그래프 x 축
    x_axis = []

    #len(df_price)
    # len(df_price) = 9288 / TEST_LENGTH = 200 / 9288 - 200 = 9088 + 20(window size) -> TEST_LENGTH - window size 만큼
    #print(str(test_price['tr_date'][len(df_price) - TEST_LENGTH]).replace("-",""))
    for i in range(TEST_LENGTH - WINDOW_SIZE - 1):
        x_axis.append(pd.to_datetime(str(test_price['tr_date'][len(df_price) - TEST_LENGTH + i]).replace("-",""), format='%Y%m%d'))

    # 역정규화를 위해 종가의 min/max 값 세팅
    end_amt_max = int(df_price.describe()['kospi']['max'])
    end_amt_min = int(df_price.describe()['kospi']['min'])

    # -1 ~ 1 사이로의 정규화
    scaler = MinMaxScaler()
    #scale_cols = ['시가','고가','저가','종가','거래량']
    scale_cols = ['dollar', 'dowjonse', 'gold', 'nasdaq', 'oil', 'snp', 'kosdaq', 'kospi']
    df_scaled = scaler.fit_transform(df_price[scale_cols])
    df_scaled = pd.DataFrame(df_scaled)
    df_scaled.columns = scale_cols

    # data 의 column 명 세팅
    feature_cols = ['dollar', 'dowjonse', 'gold', 'nasdaq', 'oil', 'snp']
    label_cols = ['kosdaq', 'kospi']

    train = df_scaled[:-TEST_LENGTH] # 과거 ~ 200일 전
    test = df_scaled[-TEST_LENGTH:] # 실제 데이터 200일 전 ~ 현재

    # 시가/고가/저가/거래량(입력 데이터)
    train_feature = train[feature_cols]
    # 종가(결과 데이터)
    train_label = train[label_cols]
    # feature(입력) 을 20개 씩 묶고, label(결과) 도 20개씩 묶는다
    train_feature, train_label = make_dataset(train_feature, train_label, 20)

    x_train, x_valid, y_train, y_valid = train_test_split(train_feature, train_label, test_size=0.2)

    # 학습의 input 을 위한 test_feature 와 비교를 위한 test_label
    test_feature = test[feature_cols]
    test_label = test[label_cols]
    test_feature, test_label = make_dataset(test_feature, test_label, 20)

    #선형 모델을 선언
    model = Sequential()

    # 모델에 대한 구체적인 입력값을 넣는다.
    model.add(LSTM(
         16,
         input_shape=(train_feature.shape[1], train_feature.shape[2]),
         activation='relu',
         return_sequences=False)
    )
    model.add(Dense(2))
    model.compile(loss='mean_squared_error', optimizer='adam')
    early_stop = EarlyStopping(monitor='val_loss', patience=5)
    filename = os.path.join('D:/11. Python Code/predict_stock', 'tmp_checkpoint.h5')
    checkpoint = ModelCheckpoint(filename, monitor='val_loss', verbose=1, save_best_only=True, mode='auto')
    # #
    history = model.fit(x_train, y_train, epochs=200, batch_size=16,
                          validation_data=(x_valid, y_valid),
                          callbacks=[early_stop, checkpoint])
    #
    model.load_weights(filename)

    # 모델에 input data 를 넣는다.
    pred = model.predict(test_feature)
    un_pred = make_unnomalization(pred, end_amt_min, end_amt_max)
    un_test_label = make_unnomalization(test_label, end_amt_min, end_amt_max)

    # 그래프 그리기
    plt.figure(figsize=(12, 9))
    plt.plot(x_axis, un_test_label, label='actual')
    plt.plot(x_axis, un_pred, label='prediction')
    plt.legend()
    plt.show()

try:
    db_class = database.Database()
except Exception as ex:
    print("에러 발생 : {}".format(ex))

url_for_us_index = 'https://m.stock.naver.com/api/json/world/worldIndexDay.nhn'
url_for_kr_index = 'https://m.stock.naver.com/api/json/sise/dailySiseIndexListJson.nhn'

#pageSize = 250
#page 1 ~ 10 ( 대략 10년 치 )

#params = {'symbol': 'DJI@DJI', 'pageSize': 250, 'page': 200}
#params = {'symbol': 'NAS@IXIC', 'pageSize': 20, 'page': 200}
#params = {'code': 'KOSPI', 'pageSize': 20, 'page': 200}
#params = {'code': 'KOSDAQ', 'pageSize': 20, 'page': 200}
def getDatafromDatabase():

    search_query = "select dollar.tr_date" \
         ", dollar.dollar" \
         ", dowjonse.dowjonse" \
         ", gold.gold" \
         ", nasdaq.nasdaq" \
         ", oil.oil" \
         ", snp.snp" \
         ", kosdaq.kosdaq" \
         ", kospi.kospi" \
     " from tb_h_dollar as dollar" \
         ", tb_h_dowjonse as dowjonse" \
         ", tb_h_gold as gold" \
         ", tb_h_nasdaq as nasdaq" \
         ", tb_h_oil as oil" \
         ", tb_h_snp as snp" \
         ", tb_h_kosdaq as kosdaq" \
         ", tb_h_kospi as kospi" \
     " where dollar.tr_date = dowjonse.tr_date" \
       " and dollar.tr_date = gold.tr_date" \
       " and dollar.tr_date = nasdaq.tr_date" \
       " and dollar.tr_date = oil.tr_date" \
       " and dollar.tr_date = snp.tr_date" \
       " and dollar.tr_date = kosdaq.tr_date" \
       " and dollar.tr_date = kospi.tr_date" \
       " and dollar.tr_date between '20190102' and '20200606'"
    result = db_class.execute_all(search_query, None)
    #print(result)
    df_result = pd.DataFrame.from_dict(result)
    #print("df_result's length : {}".format(len(df_result)))
    return df_result

def getDollar():
    # 10개씩 조회... 250 * 200 / 10 = 5000 루프
    max_tr_query = "SELECT MAX(tr_date) as tr_date FROM tb_h_dollar"
    result = db_class.execute_one(max_tr_query)
    max_tr_date = str(result['tr_date']).replace("-", "")

    url = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW&page=1"
    html = requests.get(url)
    source = BeautifulSoup(html.content, "html.parser")

    result_tr = source.select("tbody > tr") # tbody 내에 tr 태그를 받아옴
    for i in range(len(result_tr)):
        result_td = result_tr[i].find_all("td")
        #print(result_td[0].text.replace(".", ""))
        #print(result_td[1].text.replace(",", ""))
        insert_query = "INSERT INTO tb_h_dollar VALUES('%s','%s')" % (result_td[0].text.replace(".", ""), result_td[1].text.replace(",", ""))
        db_class.execute(insert_query)

    db_class.commit()

def getDowJonse():
    # 1 ~ 10 까지 구하기
    max_tr_query = "SELECT MAX(tr_date) as tr_date FROM tb_h_dowjonse"
    result = db_class.execute_one(max_tr_query)
    max_tr_date = str(result['tr_date']).replace("-","")

    for i in range(1, 2):
        params = {'symbol': 'DJI@DJI', 'pageSize': 250, 'page': i}
        response = requests.get(url_for_us_index, params=params)
        res = response.json()
        #print(i)
        for data in res['result']['worldIndexDay']:
            if max_tr_date == data['dt']:
                break

            insert_query = "INSERT INTO tb_h_dowjonse VALUES('%s','%s')" % (data['dt'], data['ncv'])
            db_class.execute(insert_query)

    db_class.commit()

#getDowJonse()
#getDollar()
#getDatafromDatabase()
predict_stock_for_kospi()