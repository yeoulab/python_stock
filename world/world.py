# 국가별 시세

import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify

world_bp = Blueprint('world_bp', __name__)

@world_bp.route("/index", methods=['GET'])
def getGlobalIndex():
    return_result = []

    kor_url_list = [
        'https://m.stock.naver.com/sise/siseIndex.nhn?code=KOSPI',
        'https://m.stock.naver.com/sise/siseIndex.nhn?code=KOSDAQ'
        ]

    for url in kor_url_list:
        res = requests.get(url)
        print(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        index_name = soup.select("#header > div.major_info_wrp > div > div.item_wrp > h2")
        index = soup.select("#header > div.major_info_wrp > div > div.stock_wrp > div.price_wrp > strong")
        highest_index = soup.select("#content > div > div.ct_box.total_info.total_ul2 > ul:nth-child(2) > li:nth-child(3) > span")
        lowest_index = soup.select("#content > div > div.ct_box.total_info.total_ul2 > ul:nth-child(3) > li:nth-child(3) > span")

        index_nm = index_name[0].text
        float_index = float(index[0].text.replace(",", ""))
        float_highest_index = float(highest_index[0].text.replace(",", ""))
        float_lowest_index = float(lowest_index[0].text.replace(",", ""))
        float_ratio_highest = round(float_index / float_highest_index * 100, 2)
        float_ratio_lowest = round(float_index / float_lowest_index * 100, 2)

        return_result.append({'index_nm': index_nm,
                              'float_index': format(float_index, ","),
                              'float_highest_index': format(float_highest_index, ","),
                              'float_lowest_index': format(float_lowest_index, ","),
                              'float_ratio_highest': format(float_ratio_highest, ","),
                              'float_ratio_lowest': format(float_ratio_lowest, ",")
                              })

    url_list = [
        'https://m.stock.naver.com/world/item.nhn?symbol=DJI@DJI', # 다우존스
        'https://m.stock.naver.com/world/item.nhn?symbol=NAS@IXIC', # 나스닥
        'https://m.stock.naver.com/world/item.nhn?symbol=NII@NI225', # 니케이
        'https://m.stock.naver.com/world/item.nhn?symbol=SHS@000001', # 상해종합
        'https://m.stock.naver.com/world/item.nhn?symbol=XTR@DAX30', # 독일
        'https://m.stock.naver.com/world/item.nhn?symbol=LNS@FTSE100', # 영국
        'https://m.stock.naver.com/world/item.nhn?symbol=ITI@FTSEMIB', # 이탈리아
        'https://m.stock.naver.com/world/item.nhn?symbol=PAS@CAC40'
    ]

    for url in url_list:
        res = requests.get(url)
        #
        print(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        index_name = soup.select("#header > div.major_info_wrp.no_code > div.major_info > div.item_wrp > div > h2")
        index = soup.select("#header > div.major_info_wrp.no_code > div.major_info > div.stock_wrp > div.price_wrp > strong")
        highest_index = soup.select("#content > div > div.ct_box.total_info.total_ul2 > ul:nth-child(2) > li:nth-child(3) > span")
        lowest_index = soup.select("#content > div > div.ct_box.total_info.total_ul2 > ul:nth-child(3) > li:nth-child(3) > span")

        index_nm = index_name[0].text
        float_index = float(index[0].text.replace(",", ""))
        float_highest_index = float(highest_index[0].text.replace(",", ""))
        float_lowest_index = float(lowest_index[0].text.replace(",", ""))
        float_ratio_highest = round(float_index / float_highest_index * 100, 2)
        float_ratio_lowest = round(float_index / float_lowest_index * 100, 2)

        return_result.append({'index_nm': index_nm,
                              'float_index': format(float_index, ","),
                              'float_highest_index': format(float_highest_index, ","),
                              'float_lowest_index': format(float_lowest_index, ","),
                              'float_ratio_highest': format(float_ratio_highest, ","),
                              'float_ratio_lowest': format(float_ratio_lowest, ",")
                              })
    #print(return_result)
    return jsonify(return_result)
