from flask import Flask, request
import requests
from bs4 import BeautifulSoup
from flask import jsonify
from flask_cors import CORS
import getSise
import getJongmokInfo

app = Flask(__name__)
cors = CORS(app)
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
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@app.route("/codeInfo")
def getCodeInfo():
    print(request.args)
    item_code = request.args.get("item_code")
    dic_res = getJongmokInfo.getCodeInfo(item_code)
    response = jsonify(dic_res)
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@app.route("/code")
def getCodeName():
    item_name = request.args.get("item_name")
    dic_res = getJongmokInfo.getCodeName(item_name)
    response = jsonify(dic_res)

    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@app.route("/news/naver")
def getNewsFromNaver():
    res = requests.get('https://news.naver.com/', verify='C:/SDS.crt')
    soup = BeautifulSoup(res.content, 'html.parser')

    link_title = soup.find_all('a')
    #return link_title
    for num in range(len(link_title)):
        print(link_title[num].get_text().strip())

if __name__ =="__main__":
    app.run(host='0.0.0.0', port=8090)
