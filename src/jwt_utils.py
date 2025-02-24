import jwt
from config import Config
from datetime import datetime, timedelta
from flask import request

def create_token(user_id, nickname):
    payload = {
        "user_id": user_id,
        "nickname": nickname,
        "exp": datetime.utcnow() + timedelta(hours=72)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    try:
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired", "status": 401}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token", "status": 401}

def IsAuthorized():
    token = request.headers.get("Authorization")
    if not token:
        return {"message": "Token is missing"}, 401

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    return verify_token(token)