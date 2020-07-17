# Main Server

from flask import Flask, request
import requests
from bs4 import BeautifulSoup
from flask import jsonify
from flask_cors import CORS, cross_origin
import getSise
import statistic.stats as stats
import logging
import auth

from auth.user import control_user_bp
from diary.diary import diary_bp
from world.world import world_bp
from item.item import item_bp
from statistic.stats import stats_bp
from theme.theme import theme_bp
from theme.theme_item import theme_item_bp


logging.basicConfig(filename="project.log", level=logging.INFO)
app = Flask(__name__)
app.register_blueprint(control_user_bp) # user 권한/로그인/로그아웃/jwt
app.register_blueprint(diary_bp) # Diary 관리
app.register_blueprint(world_bp, url_prefix="/global") # Global Index, 금, 달러, 유가 등등 추가
app.register_blueprint(item_bp, url_prefix="/item") # 종목코드, 종목정보, 종목명 등
app.register_blueprint(stats_bp)
app.register_blueprint(theme_bp)
app.register_blueprint(theme_item_bp)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
@auth.login_required
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
