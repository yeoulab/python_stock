from flask import request, Response, g
from functools import wraps
import jwt

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        print("access_token : {}".format(access_token))
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, "AAAA", "HS256")
            except jwt.InvalidTokenError:
                payload = None

            if payload is None:
                return Response(status=401)

            email = payload["email"]
            g.email = email
            #g.user = get_user_info(user_id) if user_id else None
        else:
            return Response(status=401)

        return f(*args, **kwargs)

    return decorated_function
