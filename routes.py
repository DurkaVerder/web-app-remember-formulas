from flask import Blueprint, jsonify, request, session
from models import db, Modul, Formula, User, UsersFormulas, UsersModuls
import service
import random

main = Blueprint('main', __name__)

# Получение всех модулей
@main.route('/api/modules', methods=['GET'])
def api_list_modules():
    modules = Modul.query.all()
    return jsonify([module.to_dict() for module in modules])

# Получение всех формул по ID модуля
@main.route('/api/module/<int:module_id>/formulas', methods=['GET'])
def api_list_formulas(module_id):
    module = Modul.query.get_or_404(module_id)
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    return jsonify([formula.to_dict() for formula in formulas])


# Регистрация пользователя
@main.route('/api/register', methods=['POST'])
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
@main.route('/api/login', methods=['POST'])
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

# Назначить формулу пользователю
@main.route('/api/assign_formula_to_user/<int:user_id>/<int:formula_id>', methods=['POST'])
def assign_formula_to_user(user_id, formula_id):
    user_formula = UsersFormulas(iduser=user_id, idformula=formula_id)
    db.session.add(user_formula)
    db.session.commit()
    return jsonify({"message": f"Formula {formula_id} assigned to user {user_id}"}), 200

# Назначить модуль пользователю
@main.route('/api/assign_module_to_user/<int:user_id>/<int:module_id>', methods=['POST'])
def assign_module_to_user(user_id, module_id):
    user_module = UsersModuls(iduser=user_id, idmodul=module_id)
    db.session.add(user_module)
    db.session.commit()
    return jsonify({"message": f"Module {module_id} assigned to user {user_id}"}), 200




# Это пробник квиза, он будет совершенно другой



