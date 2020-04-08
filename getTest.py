# Test 프로그램

import os
import requests
from bs4 import BeautifulSoup

#home = os.getenv('HOME')
res = requests.get('https://m.stock.naver.com/world/item.nhn?symbol=DJI@DJI')

soup = BeautifulSoup(res.content, 'html.parser')
result = soup.select("#content > div > div.ct_box.total_info.total_ul2 > ul:nth-child(2) > li:nth-child(3) > span")
#result = soup.find_all("div", class_="ct_box total_info total_ul2")
#li = result.find_all("li")

print(result[0].text)

#print(res.content)
#print("home : {}".format(home))
