import database
import pandas as pd
from datetime import datetime, timedelta

db_class = database.Database()
tday = pd.to_datetime(datetime.today().strftime("%Y%m%d"))
bf_1week_day = str(tday + timedelta(days=-7)).replace("-", "")[:8]

# tb_l_jongmok_stat
sql = "DELETE FROM tb_l_jongmok_stat WHERE tr_date='" + str(bf_1week_day) + "'"
print("tb_l_jongmok_stat delete sql : {}".format(sql))
db_class.execute(sql)

# tb_l_them_jongmok_stat
sql = "DELETE FROM tb_l_theme_jongmok_stat WHERE jongmok_code >= '000000'"
print("tb_l_theme_jongmok_stat delete sql : {}".format(sql))
db_class.execute(sql)
db_class.commit()
