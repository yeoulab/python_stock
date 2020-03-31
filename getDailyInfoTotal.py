import urllib
import time

from urllib.request import urlopen
from bs4 import BeautifulSoup

stockCode = '065450' # 065450 빅텍

trendOfInvestorUrl = 'http://finance.naver.com/item/frgn.nhn?code=' + stockCode
trendOfInvestorHtml = urlopen(trendOfInvestorUrl)
trendOfInvestorSource = BeautifulSoup(trendOfInvestorHtml.read(), "html.parser")

trendOfInvestorPageNavigation = trendOfInvestorSource.find_all("table", align="center")
trendOfInvestorMaxPageSection = trendOfInvestorPageNavigation[0].find_all("td", class_="pgRR")
trendOfInvestorMaxPageNum = int(trendOfInvestorMaxPageSection[0].a.get('href')[-3:])

for page in range(1, trendOfInvestorMaxPageNum + 1):
    url = 'http://finance.naver.com/item/frgn.nhn?code=' + stockCode + '&page=' + str(page)
    html = urlopen(url)
    source = BeautifulSoup(html.read(), "html.parser")
    dataSection = source.find("table", summary="외국인 기관 순매매 거래량에 관한표이며 날짜별로 정보를 제공합니다.")
    dayDataList = dataSection.find_all("tr")

    # day: 날짜
    # institutionPureDealing: 기관순매매
    # foreignerPureDealing: 외인순매매
    # ownedVolumeByForeigner: 외인보유 주식수
    # ownedRateByForeigner : 외인 보유율

    for i in range(3, len(dayDataList)):

        if(len(dayDataList[i].find_all("td", class_="tc")) != 0 and len(dayDataList[i].find_all("td", class_="num")) != 0):
            day = dayDataList[i].find_all("td", class_="tc")[0].text
            institutionPureDealing = dayDataList[i].find_all("td", class_="num")[4].text
            foreignerPureDealing = dayDataList[i].find_all("td", class_="num")[5].text
            ownedVolumeByForeigner = dayDataList[i].find_all("td", class_="num")[6].text
            ownedRateByForeigner = dayDataList[i].find_all("td", class_="num")[7].text
            print("날짜: " + day, end=" ")
            print("기관순매매: " + institutionPureDealing, end=" ")
            print("외인순매매: " + foreignerPureDealing, end=" ")
            print("외인보유 주식수: " + ownedVolumeByForeigner, end=" ")
            print("외인 보유율: " + ownedRateByForeigner)
