import database
import pandas as pd
import getSise
import time
from datetime import datetime
import logging

db_class = database.Database()

sql = "SELECT jongmok_code FROM tb_m_jongmok where jongmok_code='086980'"
result = db_class.execute_all(sql)
logging.basicConfig(filename="batch.log", level=logging.INFO)

url = 'https://m.stock.naver.com/api/item/getPriceDayList.nhn'
start_date = pd.to_datetime('20200101')
end_date = pd.to_datetime('20200301')
tday = pd.to_datetime(datetime.today().strftime("%Y%m%d"))

db_class = database.Database()
sql = "INSERT INTO tb_l_jongmok_stat VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'" \
      ",'%s','%s','%s','%s','%s','%s','%s','%s','%s')"

for item in result:
    res = getSise.getSise(item['jongmok_code'], start_date, end_date)

    i = 0
    result_list = []
    for data in res['result']:
        if i == 8 or i == 13:
            result_list.append(int(data['value'].split('/')[0].split(':')[1].replace(",","")))
        else:
            result_list.append(int(data['value'].replace(",","")))
        i = i + 1

    max_info = res['max_info']
    com_info = res['company_detail_info']

    insert_sql = sql % (item['jongmok_code']  # jongmok_code
                        , tday  # tr_date
                        , result_list[0]  # for_tr_cnt
                        , result_list[1]  # ins_tr_cnt
                        , result_list[2] # ind_tr_cnt
                        , result_list[3] # avg_tr_cnt
                        , result_list[4] # for_avg_fin_amt
                        , result_list[5]  # ins_avg_fin_amt
                        , result_list[6] # ind_avg_fin_amt
                        , result_list[7] # tr_avg_fin_amt
                        , result_list[8] # fin_amt
                        , result_list[9] # for_avg_avg_amt
                        , result_list[10] # ins_avg_avg_amt
                        , result_list[11] # ind_avg_avg_amt
                        , result_list[12]  # tr_avg_avg_amt
                        , int(max_info['max_tr_quant'].replace(",", "")) # max_tr_qunat
                        , str(max_info['max_tr_date'].replace("-","")) # max_tr_date
                        , float(max_info['max_tr_ratio']) # max_tr_ratio
                        , int(max_info['tot_tr_quant'].replace(",", "")) # tot_tr_quant
                        , float(max_info['max_cir_ratio']) # max_cir_ratio
                        , float(max_info['tot_cir_ratio']) # tot_cir_ratio
                        , int(com_info['tot_stock_cnt'].replace(",", "")) # tot_stock_cnt
                        , float(com_info['cir_stock_ratio']) # cir_stock_ratio
                        , int(com_info['cir_stock_cnt'].replace(",", "")) # cir_stock_cnt
                        )

    logging.log(logging.INFO, insert_sql)
    db_class.execute(insert_sql)
    db_class.commit()
    time.sleep(5)
