# Test 프로그램

import os
import requests
from bs4 import BeautifulSoup
import getSise
import re

#home = os.getenv('HOME')
#res = requests.get('https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=086980')

#soup = BeautifulSoup(res.content, 'html.parser')
#result = soup.select("#cTB11 > tbody > tr:nth-child(7) > td")
#result = soup.find_all("div", class_="ct_box total_info total_ul2")
#li = result.find_all("li")

#result_list = result[0].text.strip().split("/")
#tot_stock_cnt = int(result_list[0].replace("주","").replace(",",""))
#cir_stock_ratio = float(result_list[1].replace("%","").strip())
#cir_stock_cnt = int(tot_stock_cnt * cir_stock_ratio /100)
#print(cir_stock_cnt)

res = getSise.getSise('256630', '20191101', '20200509')
print(res)

i = 0
result_list = []
for data in res['result']:
    if i == 8 or i == 13:
        result_list.append(int(data['value'].split('/')[0].split(':')[1].replace(",","")))
    else:
        result_list.append(int(re.sub(",", "", data['value'])))
    i = i + 1

print(result_list)
#print(res.content)
#print("home : {}".format(home))
