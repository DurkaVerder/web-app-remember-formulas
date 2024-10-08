from flask import Blueprint, jsonify, request, session
from models import db, Modul, Formula, User, UsersFormulas, UsersModuls
import service
import random

main = Blueprint('main', __name__)

# Главная страница
@main.route('/')
def home():
    return jsonify({"message": "Welcome to the Formula Memory App!"})

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

# Добавление новой формулы
@main.route('/api/add_formula', methods=['POST'])
def api_add_formula():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    formula = data.get('formula')
    module_id = data.get('module_id')

    new_formula = Formula(name=name, description=description, formula=formula, idmodul=module_id)
    db.session.add(new_formula)
    db.session.commit()

    return jsonify({"message": "Formula added successfully!"}), 201

# Регистрация пользователя
@main.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    login = data.get('login')
    password = data.get('password')
    nickname = data.get('nickname')
    status = data.get('status')

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

# Старт квиза по модулю
@main.route('/api/quiz/<int:module_id>', methods=['GET'])
def start_quiz(module_id):
    session['current_module'] = module_id
    formulas = Formula.query.filter_by(idmodul=module_id).all()

    # Перемешиваем формулы
    random.shuffle(formulas)

    # Сохраняем перемешанные формулы в сессии
    session['shuffled_formulas'] = [formula.to_dict() for formula in formulas]
    session['quiz_index'] = 0
    session['correct_answers'] = 0

    return jsonify({"formulas": session['shuffled_formulas']}), 200

# Квиз - отвечать на вопросы
@main.route('/api/take_quiz', methods=['POST'])
def take_quiz():
    data = request.json
    answer = data.get('answer')
    correct = data.get('correct')

    # Проверка правильности ответа
    if answer.strip() == correct.strip():
        session['correct_answers'] += 1

    session['quiz_index'] += 1

    quiz_index = session.get('quiz_index', 0)
    shuffled_formulas = session.get('shuffled_formulas', [])

    if quiz_index >= len(shuffled_formulas):
        return jsonify({"message": "Quiz complete", "correct_answers": session['correct_answers']}), 200

    next_formula = shuffled_formulas[quiz_index]
    return jsonify({"next_formula": next_formula}), 200

# Завершение квиза
@main.route('/api/quiz_complete', methods=['GET'])
def quiz_complete():
    correct_answers = session.get('correct_answers', 0)
    total_questions = len(session.get('shuffled_formulas', []))

    return jsonify({
        "message": "Quiz complete!",
        "correct_answers": correct_answers,
        "total_questions": total_questions
    }), 200
