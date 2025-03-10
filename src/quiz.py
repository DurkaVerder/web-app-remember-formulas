from flask import Blueprint, jsonify, request, session
import random
from models import db, Formula, Test, Topic, Modul
from flask_restx import Resource, fields, Namespace
from jwt_utils import IsAuthorized  
from datetime import datetime

quiz_ns = Namespace('quiz', description='Operations related to quizzes')

# Модели данных для документации
check_answers_model = quiz_ns.model('CheckAnswers', {
    'answers': fields.List(fields.String, required=True, description='Массив ответов пользователя')
})

# Маршрут для старта квиза с отправкой всех вопросов сразу
@quiz_ns.route('/start/<int:module_id>')
class StartQuiz(Resource):
    @quiz_ns.doc(tags=['Quiz'], description="Старт квиза для указанного модуля с отправкой всех вопросов.")
    def get(self, module_id):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            return {"message": auth_result["error"]}, auth_result["status"]
        
        return start_quiz(module_id)

# Маршрут для проверки ответов
@quiz_ns.route('/submit_answers')
class SubmitAnswers(Resource):
    @quiz_ns.expect(check_answers_model)
    @quiz_ns.doc(tags=['Quiz'], description="Отправить ответы на все вопросы и получить результаты квиза.")
    def post(self):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            return {"message": auth_result["error"]}, auth_result["status"]
        
        user_id = auth_result['user_id']
        return submit_answers(user_id)

# Функция для старта квиза и отправки всех вопросов
def start_quiz(module_id):
    # Получаем все формулы для модуля
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    if len(formulas) < 6:
        return {"message": "Not enough formulas in the module."}, 400

    # Случайно выбираем 6 вопросов
    selected_formulas = random.sample(formulas, 6)

    # Создаем вопросы и варианты ответов
    questions = []
    for formula in selected_formulas:
        correct_name = formula.name
        all_formulas = Formula.query.filter(Formula.id != formula.id).all()
        wrong_names = random.sample([f.name for f in all_formulas], 3)
        options = wrong_names + [correct_name]
        random.shuffle(options)

        questions.append({
            "id": formula.id,
            "question": formula.formula,  # Вопрос — это формула
            "options": options,          # Варианты — имена формул
            "correct_name": correct_name # Правильный ответ — имя формулы
        })
    
    # Сохраняем вопросы в сессии
    session['quiz'] = {
        'module_id': module_id,
        'questions': questions,
        'correct_answers': 0,
        'incorrect_answers': 0
    }
    
    return {"questions": questions}, 200

# Функция для проверки ответов
def submit_answers(user_id):
    data = request.json
    user_answers = data.get('answers', [])
    
    quiz = session.get('quiz', {})
    if not quiz:
        return {"message": "Quiz not started."}, 400
    
    correct_answers = 0
    incorrect_answers = 0
    results = []
    
    # Проверка каждого ответа
    for i, user_answer in enumerate(user_answers):
        if i >= len(quiz['questions']):
            break
        question = quiz['questions'][i]
        is_correct = user_answer == question['correct_name']  # Сравниваем с именем формулы
        if is_correct:
            correct_answers += 1
        else:
            incorrect_answers += 1
        results.append({
            "question_id": question["id"],
            "question": question["question"],
            "selected_answer": user_answer,
            "correct_answer": question["correct_name"],  # Возвращаем имя, а не LaTeX
            "is_correct": is_correct
        })
    
    # Итоговая статистика
    total_questions = len(quiz['questions'])
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Получаем модуль для определения названия раздела
    module = Modul.query.get(quiz['module_id'])
    if not module:
        return {"message": "Module not found"}, 404
    section_name = module.name

    # Сохраняем результат теста
    new_test = Test(
        user_id=user_id,
        date=datetime.now(),
        success_rate=int(accuracy),
        section=section_name
    )
    db.session.add(new_test)

    # Обновляем или создаем запись в Topic
    topic = Topic.query.filter_by(user_id=user_id, name=section_name).first()
    if topic:
        # Обновляем существующую тему
        topic.tests_passed += 1
        topic.success_rate = ((topic.success_rate * (topic.tests_passed - 1)) + accuracy) / topic.tests_passed
    else:
        # Создаем новую тему
        topic = Topic(
            user_id=user_id,
            name=section_name,
            tests_passed=1,
            success_rate=accuracy
        )
        db.session.add(topic)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"message": f"Database error: {str(e)}"}, 500

    # Возвращаем результат
    return {
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "total_questions": total_questions,
        "accuracy": accuracy,
        "results": results
    }, 200

# Модель данных остаётся прежней
symbol_quiz_model = quiz_ns.model('SymbolQuizAnswers', {
    'answers': fields.List(fields.List(fields.String), required=True, description='Массив ответов пользователя (массив символов для каждой формулы)')
})

# Маршрут для старта квиза с разбиением на символы
@quiz_ns.route('/start_symbol_quiz/<int:module_id>')
class StartSymbolQuiz(Resource):
    @quiz_ns.doc(tags=['Quiz'], description="Старт квиза с разбиением формул на символы для указанного модуля.")
    def get(self, module_id):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            return {"message": auth_result["error"]}, auth_result["status"]
        
        return start_symbol_quiz(module_id)

# Маршрут для проверки ответов квиза с символами
@quiz_ns.route('/submit_symbol_answers')
class SubmitSymbolAnswers(Resource):
    @quiz_ns.expect(symbol_quiz_model)
    @quiz_ns.doc(tags=['Quiz'], description="Отправить ответы для квиза с символами и получить результаты.")
    def post(self):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            return {"message": auth_result["error"]}, auth_result["status"]
        
        user_id = auth_result['user_id']
        return submit_symbol_answers(user_id)

# Функция для старта квиза с символами
def start_symbol_quiz(module_id):
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    if len(formulas) < 6:
        return {"message": "Not enough formulas in the module."}, 400

    selected_formulas = random.sample(formulas, 6)
    questions = []
    
    for formula in selected_formulas:
        # Убираем пробелы из формулы перед разбиением
        formula_cleaned = formula.formula.replace(" ", "")
        # Разбиваем формулу на символы
        symbols = list(formula_cleaned)
        # Создаем дополнительные "мусорные" символы для усложнения
        extra_symbols = ['+', '-', '=', '(', ')', '*', '/', '^', 'x', 'y', 'z']
        # Исключаем дубликаты символов из правильной формулы
        distractors = random.sample([sym for sym in extra_symbols if sym not in symbols], min(5, len(symbols)))
        
        # Все символы для выбора
        all_symbols = symbols + distractors
        random.shuffle(all_symbols)
        
        questions.append({
            "id": formula.id,
            "name": formula.name,
            "correct_formula": formula_cleaned,  # Сохраняем формулу без пробелов
            "symbols": all_symbols,
            "length": len(symbols)  # Длина без пробелов
        })
    
    session['symbol_quiz'] = {
        'module_id': module_id,
        'questions': questions,
        'correct_answers': 0,
        'incorrect_answers': 0
    }
    
    return {"questions": questions}, 200

# Функция для проверки ответов квиза с символами
def submit_symbol_answers(user_id):
    data = request.json
    user_answers = data.get('answers', [])
    
    quiz = session.get('symbol_quiz', {})
    if not quiz:
        return {"message": "Symbol quiz not started."}, 400
    
    correct_answers = 0
    incorrect_answers = 0
    results = []
    
    for i, user_answer in enumerate(user_answers):
        if i >= len(quiz['questions']):
            break
        question = quiz['questions'][i]
        # Преобразуем массив символов пользователя в строку, исключая пробелы
        user_formula = ''.join(user_answer).replace(" ", "")
        is_correct = user_formula == question['correct_formula']
        
        if is_correct:
            correct_answers += 1
        else:
            incorrect_answers += 1
            
        results.append({
            "question_id": question["id"],
            "question_name": question["name"],
            "selected_answer": user_formula,
            "correct_answer": question["correct_formula"],
            "is_correct": is_correct
        })
    
    total_questions = len(quiz['questions'])
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    module = Modul.query.get(quiz['module_id'])
    if not module:
        return {"message": "Module not found"}, 404
    section_name = module.name

    # Сохраняем результат теста
    new_test = Test(
        user_id=user_id,
        date=datetime.now(),
        success_rate=int(accuracy),
        section=section_name + " (Symbol Quiz)"
    )
    db.session.add(new_test)

    # Обновляем или создаем запись в Topic
    topic_name = section_name + " (Symbol Quiz)"
    topic = Topic.query.filter_by(user_id=user_id, name=topic_name).first()
    if topic:
        topic.tests_passed += 1
        topic.success_rate = ((topic.success_rate * (topic.tests_passed - 1)) + accuracy) / topic.tests_passed
    else:
        topic = Topic(
            user_id=user_id,
            name=topic_name,
            tests_passed=1,
            success_rate=accuracy
        )
        db.session.add(topic)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"message": f"Database error: {str(e)}"}, 500

    return {
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "total_questions": total_questions,
        "accuracy": accuracy,
        "results": results
    }, 200