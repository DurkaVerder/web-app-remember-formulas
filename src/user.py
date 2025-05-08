from flask import Blueprint, jsonify, request, session
from models import db, User, Test, Topic, Achievement
from flask_restx import Api, Namespace, Resource, fields
import service
from jwt_utils import create_token, IsAuthorized
from logger import log_info, log_error, log_debug  # Импорт функций из logger.py

user_ns = Namespace('user', description="User operations")

register_model = user_ns.model('Register', {
    'login': fields.String(required=True, description='User login'),
    'password': fields.String(required=True, description='User password'),
    'nickname': fields.String(required=True, description='User nickname')
})

login_model = user_ns.model('Login', {
    'login': fields.String(required=True, description='User login'),
    'password': fields.String(required=True, description='User password')
})

download_avatar_model = user_ns.model('DownloadAvatar', {
    'path': fields.String(required=True, description='Path to avatar file')
})

@user_ns.route('/register')
class Register(Resource):
    @user_ns.expect(register_model)
    @user_ns.doc(description="Register a new user.")
    def post(self):
        log_info("User registration attempt")
        return register()

@user_ns.route('/login')
class Login(Resource):
    @user_ns.expect(login_model)
    @user_ns.doc(description="Login an existing user.")
    def post(self):
        log_info("User login attempt")
        return login()

@user_ns.route('/profile')
class Profile(Resource):
    @user_ns.doc(description="Get user profile information.")
    def get(self):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            log_error(f"Profile access failed: {auth_result['error']}")
            return {"message": auth_result["error"]}, auth_result["status"]
        
        user_id = auth_result['user_id']
        log_info(f"Fetching profile for user {user_id}")
        try:
            user = User.query.get(user_id)
            if not user:
                log_error(f"User {user_id} not found for profile request")
                return {"message": "User not found"}, 404

            tests = Test.query.filter_by(user_id=user_id).all()
            topics = Topic.query.filter_by(user_id=user_id).all()
            achievements = Achievement.query.filter_by(user_id=user_id).all()

            profile_data = {
                "user": {
                    "name": user.nickname,
                    "status": user.status,
                    "avatar": user.avatar
                },
                "tests": [test.to_dict_with_time() for test in tests],
                "topics": [topic.to_dict() for topic in topics],
                "achievements": [achievements.to_dict() for achievements in achievements]
            }
            log_info(f"Profile retrieved successfully for user {user_id}")
            return profile_data, 200
        except Exception as e:
            log_error(f"Error retrieving profile for user {user_id}: {str(e)}")
            return {"message": "Internal server error"}, 500

@user_ns.route('/validjwt')
class ValidJWT(Resource):
    @user_ns.doc(description="Check if JWT token from Authorization header is valid.")
    def get(self):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            log_error(f"JWT validation failed: {auth_result['error']}")
            return {"message": auth_result["error"]}, auth_result["status"]
        log_info(f"JWT token validated successfully for user {auth_result['user_id']}")
        return {"message": "Token is valid"}, 200

def login():
    try:
        data = request.json
        login_input = data.get('login')
        password_input = data.get('password')

        if not login_input or not password_input:
            log_error("Login failed: Missing login or password")
            return {"message": "Login and password are required"}, 400

        user = User.query.filter_by(login=login_input, password=password_input).first()

        if user:
            token = create_token(user.id, user.nickname)
            log_info(f"User {login_input} logged in successfully, user_id: {user.id}")
            return {"message": "Login successful", "token": token}
        else:
            log_error(f"Login failed for {login_input}: Invalid credentials")
            return {"message": "Invalid login or password."}, 401
    except Exception as e:
        log_error(f"Error during login for {login_input}: {str(e)}")
        return {"message": "Internal server error"}, 500

def register():
    try:
        data = request.json
        login = data.get('login')
        password = data.get('password')
        nickname = data.get('nickname')
        status = 'beginner'

        if not login or not password or not nickname:
            log_error("Registration failed: Missing login, password, or nickname")
            return {"message": "Login, password, and nickname are required"}, 400

        if not service.check_password(password):
            log_error(f"Registration failed for {login}: Invalid password")
            return {"message": "Invalid login or password"}, 401

        existing_user = User.query.filter_by(login=login).first()
        if existing_user:
            log_info(f"Registration attempt for existing login: {login}")
            return {"message": "User already exists", "user": existing_user.to_dict()}, 409

        new_user = User(login=login, password=password, nickname=nickname, status=status)
        db.session.add(new_user)
        db.session.commit()
        log_info(f"User {login} registered successfully, user_id: {new_user.id}")
        return {"message": "User registered successfully"}, 201
    except Exception as e:
        db.session.rollback()
        log_error(f"Error registering user {login}: {str(e)}")
        return {"message": "Database error"}, 500

@user_ns.route('/upload-avatar')
class Download(Resource):
    @user_ns.expect(download_avatar_model)
    @user_ns.doc(description="Download a file.")
    def post(self):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            log_error(f"Avatar download failed: {auth_result['error']}")
            return {"message": auth_result["error"]}, auth_result["status"]
        
        user_id = auth_result['user_id']
        data = request.json
        path = data.get('path')
        
        if not path:
            log_error(f"Avatar download failed for user {user_id}: Missing path")
            return {"message": "Path is required"}, 400
        
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                log_error(f"User {user_id} not found for avatar download")
                return {"message": "User not found"}, 404
            
            user.avatar = path
            db.session.commit()
            log_info(f"Avatar downloaded successfully for user {user_id}, path: {path}")
            return {"message": "Avatar downloaded successfully"}, 200
        except Exception as e:
            db.session.rollback()
            log_error(f"Error downloading avatar for user {user_id}: {str(e)}")
            return {"message": "Database error"}, 500
