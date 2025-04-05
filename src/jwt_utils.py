import jwt
from config import Config
from datetime import datetime, timedelta
from flask import request
from logger import log_info, log_error, log_debug 

def create_token(user_id, nickname):
    try:
        payload = {
            "user_id": user_id,
            "nickname": nickname,
            "exp": datetime.utcnow() + timedelta(hours=72)
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
        log_info(f"Token created for user_id: {user_id}, nickname: {nickname}")
        return token
    except Exception as e:
        log_error(f"Failed to create token for user_id: {user_id}: {str(e)}")
        raise  # Повторно выбрасываем исключение, если нужно обработать выше

def verify_token(token):
    try:
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        log_info(f"Token verified successfully for user_id: {decoded_token['user_id']}")
        return decoded_token
    except jwt.ExpiredSignatureError:
        log_error(f"Token verification failed: Token expired")
        return {"error": "Token expired", "status": 401}
    except jwt.InvalidTokenError:
        log_error(f"Token verification failed: Invalid token")
        return {"error": "Invalid token", "status": 401}
    except Exception as e:
        log_error(f"Unexpected error during token verification: {str(e)}")
        return {"error": "Token verification error", "status": 500}

def IsAuthorized():
    token = request.headers.get("Authorization")
    if not token:
        log_error("Authorization attempt failed: Token is missing in request headers")
        return {"error": "Token is missing", "status": 401}

    if token.startswith("Bearer "):
        token = token.split(" ")[1]
        log_debug(f"Extracted Bearer token: {token[:10]}...") 

    result = verify_token(token)
    if "error" in result:
        log_error(f"Authorization failed: {result['error']}")
    else:
        log_info(f"User authorized successfully: user_id {result['user_id']}")
    return result