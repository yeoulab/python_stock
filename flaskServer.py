# Main Server

from flask import Flask, request
import requests
from bs4 import BeautifulSoup
from flask import jsonify
from flask_cors import CORS, cross_origin
import getSise, getJongmokInfo, getDailyInfoTotal, getDiary
import statistic.getStats as stats
import logging


logging.basicConfig(filename="project.log", level=logging.INFO)
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def test():
    return "test"

@app.route("/unitPrice")
def getUnitPrice():
    print(request.args)
    item_code = request.args.get("item_code")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    print("start_date : {}".format(start_date))
    print("end_date : {}".format(end_date))
    dic_res = getSise.getSise(item_code, start_date, end_date)
    response = jsonify(dic_res)
    return response

@app.route("/codeInfo")
def getCodeInfo():
    print(request.args)
    item_code = request.args.get("item_code")
    dic_res = getJongmokInfo.getCodeInfo(item_code)
    response = jsonify(dic_res)
    return response

@app.route("/code")
def getCodeName():
    item_name = request.args.get("item_name")
    dic_res = getJongmokInfo.getCodeName(item_name)
    response = jsonify(dic_res)

    return response

@app.route("/globalIndex")
def getGlobalIndex():
    dic_res = getDailyInfoTotal.getGlobalIndex()
    response = jsonify(dic_res)

    return response

@app.route("/search/diary")
def searchDiary():
    print("searchDiary Start")
    dic_res = getDiary.getDiaryDb()
    response = jsonify(dic_res)
    return response

@app.route("/update/diary", methods=['POST'])
@cross_origin(origin='*')
def updateDiary():
    print("updateDiary Start")
    data = request.get_json()
    getDiary.updateDiaryDb(data)
    response = {}
    return response

@app.route("/insert/diary", methods=['POST'])
@cross_origin(origin='*')
def insertDiary():
    print("insertDiary Start")
    data = request.get_json()
    getDiary.insertDiaryDb(data)
    response = {}
    return response

@app.route("/search/stats", methods=['GET'])
def searchStats():
    dic_res = stats.getStatsDb()
    response = jsonify(dic_res)
    return response

@app.after_request
def add_headers(response):
    response.headers.add('Content-Type', 'application/json')
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Type,Content-Length,Authorization,X-Pagination')
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

if __name__ =="__main__":
    app.run(host='0.0.0.0', port=8090)
