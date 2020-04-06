##### 이 파이썬 파일은 안써도 됨. ( getSise.py 로 대체 함 )
# import urllib
# import time
#
# from urllib.request import urlopen
# from bs4 import BeautifulSoup
#
# import pymysql
# from sqlalchemy import create_engine
#
# db_data = 'mysql+pymysql://' + 'root' + ':' + 'Rkakrnl1!' + '@' + 'localhost' + ':3306/' \
#        + 'stock' + '?charset=UTF8MB4'
# engine = create_engine(db_data, encoding='utf8')
#
# db = pymysql.connect(host='localhost'
#                      , port=3306
#                      , user='root'
#                      , passwd='Rkakrnl1!'
#                      , db='stock'
#                      , charset='utf8mb4')
#
# sql = "insert into tb_l_jongmok_trend(jongmok_code,tr_date,end_amt,tot_deal_cnt,ins_deal_cnt,for_deal_cnt,for_hold_cnt,for_hold_per) values (%s,%s,%s,%s,%s,%s,%s,%s)"
# sel_sql = "select * from tb_m_jongmok where jongmok_code between %s and %s"
# del_sql = "delete from tb_l_jongmok_trend where jongmok_code=%s"
#
# stockCode = '065450' # 065450 빅텍
#
# #trendOfInvestorUrl = 'http://finance.naver.com/item/frgn.nhn?code=' + stockCode
# #trendOfInvestorHtml = urlopen(trendOfInvestorUrl)
# #trendOfInvestorSource = BeautifulSoup(trendOfInvestorHtml.read(), "html.parser")
#
# #trendOfInvestorPageNavigation = trendOfInvestorSource.find_all("table", align="center")
# #trendOfInvestorMaxPageSection = trendOfInvestorPageNavigation[0].find_all("td", class_="pgRR")
# #print("trendOfInve: {}".format(trendOfInvestorMaxPageSection[0].a.get('href')))
# #trendOfInvestorMaxPageNum = int(trendOfInvestorMaxPageSection[0].a.get('href')[-3:])
# #print("trendOfInvestorMaxPageNum : {}".format(trendOfInvestorMaxPageNum))
# trendOfInvestorMaxPageNum = 2
#
# try:
#     with db.cursor() as cursor:
#         cursor.execute(sel_sql, ('065450','065450'))
#         rows = cursor.fetchall()
#
#         # 조회한 종목 loop 처리
#         for row in rows:
#             cursor.execute(del_sql, row[1])
#
#             for page in range(1, trendOfInvestorMaxPageNum + 1):
#                 url = 'http://finance.naver.com/item/frgn.nhn?code=' + row[1] + '&page=' + str(page)
#                 html = urlopen(url)
#                 source = BeautifulSoup(html.read(), "html.parser")
#                 dataSection = source.find("table", summary="외국인 기관 순매매 거래량에 관한표이며 날짜별로 정보를 제공합니다.")
#                 dayDataList = dataSection.find_all("tr")
#
#                 # day: 날짜
#                 # institutionPureDealing: 기관순매매
#                 # foreignerPureDealing: 외인순매매
#                 # ownedVolumeByForeigner: 외인보유 주식수
#                 # ownedRateByForeigner : 외인 보유율
#                 # print("dayDataList length : {}".format(len(dayDataList)))
#
#                 for i in range(3, len(dayDataList)):
#
#                     if (len(dayDataList[i].find_all("td", class_="tc")) != 0 and len(
#                             dayDataList[i].find_all("td", class_="num")) != 0):
#                         day = dayDataList[i].find_all("td", class_="tc")[0].text.replace(".","")
#                         # 종가
#                         endAmt = int(dayDataList[i].find_all("td", class_="num")[0].text.replace(",", ""))
#                         # 총 거래량
#                         totalDealing = int(dayDataList[i].find_all("td", class_="num")[3].text.replace(",", ""))
#                         # 기관 순매매
#                         institutionPureDealing = int(dayDataList[i].find_all("td", class_="num")[4].text.replace(",",""))
#                         # 외국인 순매매
#                         foreignerPureDealing = int(dayDataList[i].find_all("td", class_="num")[5].text.replace(",",""))
#                         # 외국인 보유량
#                         ownedVolumeByForeigner = int(dayDataList[i].find_all("td", class_="num")[6].text.replace(",",""))
#                         # 외국인 보유율
#                         ownedRateByForeigner = float(dayDataList[i].find_all("td", class_="num")[7].text.replace("%",""))
#                         #print("날짜: " + day, end=" ")
#                         #print("기관순매매: " + institutionPureDealing, end=" ")
#                         #print("외인순매매: " + foreignerPureDealing, end=" ")
#                         #print("외인보유 주식수: " + ownedVolumeByForeigner, end=" ")
#                         #print("외인 보유율: " + ownedRateByForeigner)
#                         #print(institutionPureDealing)
#                         #print(foreignerPureDealing)
#                                                 #print(ownedVolumeByForeigner)
#                         #print(ownedRateByForeigner)
#                         cursor.execute(sql, (row[1], day, endAmt, totalDealing, institutionPureDealing, foreignerPureDealing, ownedVolumeByForeigner, ownedRateByForeigner))
#             db.commit()
# finally:
#     db.close()
