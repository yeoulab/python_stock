from flask import request, jsonify, Blueprint
import database
import bcrypt
import jwt
from datetime import datetime, timedelta

control_user_bp = Blueprint('control_user_bp', __name__)
select_query = "SELECT email, name, profile, password FROM tb_m_user WHERE email='%s'"

@control_user_bp.route("/sign-up", methods=["POST"])
def sign_up():
    new_user = request.json
    new_user['password'] = bcrypt.hashpw(new_user['password'].encode('UTF-8'), bcrypt.gensalt()).decode('utf-8')

    db_class = database.Database()

    new_user_query = """INSERT INTO tb_m_user VALUES('%s','%s','%s','%s')""" \
          % (new_user['email'], new_user['name'], new_user['profile'], new_user['password'])
    db_class.execute(new_user_query)

    data = new_user['email']
    query = select_query % data
    result = db_class.execute_one(query)

    db_class.commit()

    return jsonify(result)

@control_user_bp.route("/login", methods=["POST"])
def login():
    user = request.json
    password = user["password"]

    db_class = database.Database()
    data = user["email"]
    query = select_query % data
    result = db_class.execute_one(query)
    if result and bcrypt.checkpw(password.encode("UTF-8"), result["password"].encode("UTF-8")):
        payload = {
          "email": result['email'],
          "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }

        token = jwt.encode(payload, "AAAA", "HS256")

        return jsonify({
          "access_token": token.decode("UTF-8")
        })
    else:
        return '', 401
