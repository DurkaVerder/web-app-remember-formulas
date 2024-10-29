from flask import Blueprint, jsonify, request, session
from models import db, User
from flask_restx import Api, Namespace, Resource, fields
import service

user_bp = Blueprint('user', __name__)
user_ns = Namespace('user', description="User operations")

# Модель для регистрации пользователя
register_model = user_ns.model('Register', {
    'login': fields.String(required=True, description='User login'),
    'password': fields.String(required=True, description='User password'),
    'nickname': fields.String(required=True, description='User nickname')
})

# Модель для логина пользователя
login_model = user_ns.model('Login', {
    'login': fields.String(required=True, description='User login'),
    'password': fields.String(required=True, description='User password')
})


# Регистрация пользователя
@user_ns.route('/register')
class Register(Resource):
    @user_ns.expect(register_model)
    @user_ns.doc(description="Register a new user.")
    def post(self):
        return register()


# Вход пользователя
@user_ns.route('/login')
class Login(Resource):
    @user_ns.expect(login_model)
    @user_ns.doc(description="Login an existing user.")
    def post(self):
        return login()


# Функция логина пользователя
def login():
    data = request.json
    login_input = data.get('login')
    password_input = data.get('password')

    user = User.query.filter_by(login=login_input, password=password_input).first()

    if user:
        session['user_id'] = user.id
        session['nickname'] = user.nickname
        return {"nickname": user.nickname}, 200
    else:
        return {"message": "Invalid login or password."}, 401


# Функция регистрации пользователя
def register():
    data = request.json  # Получаем данные из запроса
    login = data.get('login')
    password = data.get('password')
    nickname = data.get('nickname')
    status = 'beginner'

    # Проверяем правильность логина и пароля
    if not service.check_login(login) or not service.check_password(password):
        return {"message": "Invalid login or password"}, 401

    # Проверяем, существует ли уже пользователь с таким логином
    existing_user = User.query.filter_by(login=login).first()
    print(existing_user)
    if existing_user:
        return {"message": "User already exists"}, 409

    # Создаем нового пользователя
    new_user = User(login=login, password=password, nickname=nickname, status=status)
    db.session.add(new_user)
    db.session.commit()

    return {"message": "User registered successfully"}, 201
