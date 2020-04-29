import database
import logging


logging.basicConfig(filename="batch.log", level=logging.WARNING)
db_class = database.Database()

sql = "SELECT jongmok_code FROM tb_m_jongmok"
result = db_class.execute_all(sql)

for item in result:
    print(item['jongmok_code'])
    # get Max Transaction Count( from 6 months to 1 month )

    # call getSise

    # Insert DB

    # sleep 3 sec
