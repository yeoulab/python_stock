# Test 프로그램

import os
import requests
from bs4 import BeautifulSoup
import getSise

#home = os.getenv('HOME')
res = requests.get('https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=086980')

soup = BeautifulSoup(res.content, 'html.parser')
result = soup.select("#cTB11 > tbody > tr:nth-child(7) > td")
#result = soup.find_all("div", class_="ct_box total_info total_ul2")
#li = result.find_all("li")

result_list = result[0].text.strip().split("/")
tot_stock_cnt = int(result_list[0].replace("주","").replace(",",""))
cir_stock_ratio = float(result_list[1].replace("%","").strip())
cir_stock_cnt = int(tot_stock_cnt * cir_stock_ratio /100)
print(cir_stock_cnt)

getSise.getSise('086980', '20200406', '20200407')

#print(res.content)
#print("home : {}".format(home))
