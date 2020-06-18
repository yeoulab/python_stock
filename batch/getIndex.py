import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import database
from sqlalchemy import create_engine


cnt = 1
db_class = database.Database()

df_dollar = pd.read_csv(os.path.join('E:/dev', 'USD_KRW 내역.csv'), encoding='utf8') # tb_h_dollar
df_snp = pd.read_csv(os.path.join('E:/dev', 'S&P 500 내역.csv'), encoding='utf8') # tb_h_snp
df_oil = pd.read_csv(os.path.join('E:/dev', 'WTI유 선물 내역.csv'), encoding='utf8') # tb_h_oil
df_gold = pd.read_csv(os.path.join('E:/dev', '금 선물 내역.csv'), encoding='utf8') # tb_h_gold
df_nasdaq = pd.read_csv(os.path.join('E:/dev', '나스닥 100 내역.csv'), encoding='utf8') # tb_h_nasdaq
df_dowjonse = pd.read_csv(os.path.join('E:/dev', '다우존스 내역.csv'), encoding='utf8') # tb_h_dowjonse
df_kosdaq = pd.read_csv(os.path.join('E:/dev', '코스닥 내역.csv'), encoding='utf8') # tb_h_kosdaq
df_kospi = pd.read_csv(os.path.join('E:/dev', '코스피지수 내역.csv'), encoding='utf8') # tb_h_kospi

dollar_insert_sql = "INSERT INTO tb_h_dollar VALUES ('%s','%s')"
snp_insert_sql = "INSERT INTO tb_h_snp VALUES ('%s','%s')"
oil_insert_sql = "INSERT INTO tb_h_oil VALUES ('%s','%s')"
gold_insert_sql = "INSERT INTO tb_h_gold VALUES ('%s','%s')"
nasdaq_insert_sql = "INSERT INTO tb_h_nasdaq VALUES ('%s','%s')"
dowjonse_insert_sql = "INSERT INTO tb_h_dowjonse VALUES ('%s','%s')"
kosdaq_insert_sql = "INSERT INTO tb_h_kosdaq VALUES ('%s','%s')"
kospi_insert_sql = "INSERT INTO tb_h_kospi VALUES ('%s','%s')"

for i in range(len(df_dollar)):
    insert_sql = dollar_insert_sql % (df_dollar['날짜'][i].replace("년","").replace("월","").replace("일","").replace(" ",""),
                                     float(df_dollar['종가'][i].replace(",","")))
    db_class.execute(insert_sql)

for i in range(len(df_snp)):
    insert_sql = snp_insert_sql % (df_snp['날짜'][i].replace("년","").replace("월","").replace("일","").replace(" ",""),
                                     float(df_snp['종가'][i].replace(",","")))
    db_class.execute(insert_sql)

for i in range(len(df_oil)):
    insert_sql = oil_insert_sql % (df_oil['날짜'][i].replace("년","").replace("월","").replace("일","").replace(" ",""),
                                     float(df_oil['종가'][i]))
    db_class.execute(insert_sql)

for i in range(len(df_gold)):
    insert_sql = gold_insert_sql % (df_gold['날짜'][i].replace("년","").replace("월","").replace("일","").replace(" ",""),
                                     float(df_gold['종가'][i].replace(",","")))
    db_class.execute(insert_sql)

for i in range(len(df_nasdaq)):
    insert_sql = nasdaq_insert_sql % (df_nasdaq['날짜'][i].replace("년","").replace("월","").replace("일","").replace(" ",""),
                                     float(df_nasdaq['종가'][i].replace(",","")))
    db_class.execute(insert_sql)

for i in range(len(df_dowjonse)):
    insert_sql = dowjonse_insert_sql % (df_dowjonse['날짜'][i].replace("년","").replace("월","").replace("일","").replace(" ",""),
                                     float(df_dowjonse['종가'][i].replace(",","")))
    db_class.execute(insert_sql)

for i in range(len(df_kosdaq)):
    insert_sql = kosdaq_insert_sql % (df_kosdaq['날짜'][i].replace("년","").replace("월","").replace("일","").replace(" ",""),
                                     float(df_kosdaq['종가'][i]))
    db_class.execute(insert_sql)

for i in range(len(df_kospi)):
    insert_sql = kospi_insert_sql % (df_kospi['날짜'][i].replace("년","").replace("월","").replace("일","").replace(" ",""),
                                     float(df_kospi['종가'][i].replace(",","")))
    db_class.execute(insert_sql)

db_class.commit()


#print(df_dollar['날짜'][0].replace("년","").replace("월","").replace("일","").replace(" ",""))
#print(df_dollar['종가'][0].replace(",",""))
#print(len(df_dollar))