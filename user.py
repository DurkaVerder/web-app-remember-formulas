from flask import Blueprint, jsonify, request, session
from models import db, Modul, Formula, User, UsersFormulas, UsersModuls
import service

user = Blueprint('user', __name__)

# Регистрация пользователя
@user.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    login = data.get('login')
    password = data.get('password')
    nickname = data.get('nickname')
    status = 'beginner'

    if not service.check_login(login) and service.check_password(password):
        return jsonify({"message": "Invalid login or password"}), 401
    new_user = User(login=login, password=password, nickname=nickname, status=status)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

# Вход пользователя
@user.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    login_input = data.get('login')
    password_input = data.get('password')

    user = User.query.filter_by(login=login_input, password=password_input).first()

    if user:
        session['user_id'] = user.id
        session['nickname'] = user.nickname
        return jsonify({"message": "Login successful!", "nickname": user.nickname}), 200
    else:
        return jsonify({"message": "Invalid login or password."}), 401