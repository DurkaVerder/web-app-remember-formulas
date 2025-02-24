from flask import Blueprint, jsonify, request, session
from models import db, User, Test, Topic
from flask_restx import Api, Namespace, Resource, fields
import service
from jwt_utils import create_token, IsAuthorized

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

@user_ns.route('/register')
class Register(Resource):
    @user_ns.expect(register_model)
    @user_ns.doc(description="Register a new user.")
    def post(self):
        return register()

@user_ns.route('/login')
class Login(Resource):
    @user_ns.expect(login_model)
    @user_ns.doc(description="Login an existing user.")
    def post(self):
        return login()


@user_ns.route('/profile')
class Profile(Resource):
    @user_ns.doc(description="Get user profile information.")
    def get(self):
        auth_result = IsAuthorized()
        if "error" in auth_result:  # Проверяем, есть ли ошибка
            return {"message": auth_result["error"]}, auth_result["status"]
        
        # Если ошибок нет, auth_result — это словарь с данными токена
        user_id = auth_result['user_id']
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        tests = Test.query.filter_by(user_id=user_id).all()
        topics = Topic.query.filter_by(user_id=user_id).all()

        profile_data = {
            "user": {
                "name": user.nickname,
                "status": user.status,
                "avatar": user.avatar
            },
            "tests": [test.to_dict() for test in tests],
            "topics": [topic.to_dict() for topic in topics]
        }

        return profile_data, 200

def login():
    data = request.json
    login_input = data.get('login')
    password_input = data.get('password')

    user = User.query.filter_by(login=login_input, password=password_input).first()

    if user:
        token = create_token(user.id, user.nickname)
        return {"message": "Login successful", "token": token}
    else:
        return {"message": "Invalid login or password."}, 401

def register():
    data = request.json
    login = data.get('login')
    password = data.get('password')
    nickname = data.get('nickname')
    status = 'beginner'

    if not service.check_password(password):
        return {"message": "Invalid login or password"}, 401

    existing_user = User.query.filter_by(login=login).first()

    if existing_user:
        return {"message": "User already exists",
                "user": existing_user.to_dict()}, 409

    new_user = User(login=login, password=password, nickname=nickname, status=status)
    db.session.add(new_user)
    db.session.commit()

    return {"message": "User registered successfully"}, 201