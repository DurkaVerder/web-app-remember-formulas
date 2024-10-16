from flask import Blueprint, jsonify, request, session
import random
from models import db, Formula, Modul

quiz = Blueprint('quiz', __name__)

# Маршрут для старта квиза по модулю
@quiz.route('/api/quiz/start/<int:module_id>', methods=['GET'])
def api_start_quiz(module_id):
    return start_quiz(module_id)

# Маршрут для получения следующего вопроса
@quiz.route('/api/quiz/next_question', methods=['GET'])
def api_next_question():
    return next_question()

# Маршрут для проверки ответа пользователя
@quiz.route('/api/quiz/check_answer', methods=['POST'])
def api_check_answer():
    return check_answer()

# Маршрут для завершения квиза
@quiz.route('/api/quiz/finish', methods=['GET'])
def api_finish_quiz():
    return finish_quiz()

# Функция для старта квиза по определенному модулю
def start_quiz(module_id):
    # Получаем 6 случайных формул из модуля
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    if len(formulas) < 6:
        return jsonify({"message": "Not enough formulas in the module."}), 400
    
    selected_formulas = random.sample(formulas, 6)
    
    # Сохраняем квиз в сессии
    session['quiz'] = {
        'module_id': module_id,
        'questions': [formula.to_dict() for formula in selected_formulas],
        'current_index': 0,
        'correct_answers': 0,
        'incorrect_answers': 0,
        'results': []
    }

    # Отправляем первый вопрос
    return next_question()

# Функция для отправки следующего вопроса
def next_question():
    quiz = session.get('quiz', {})
    if not quiz or quiz['current_index'] >= len(quiz['questions']):
        return jsonify({"message": "Quiz not started or already finished."}), 400

    current_formula = quiz['questions'][quiz['current_index']]

    # Генерация вариантов ответа
    correct_answer = current_formula['formula']
    all_formulas = Formula.query.filter(Formula.id != current_formula['id']).all()
    wrong_answers = random.sample([f.formula for f in all_formulas], 3)

    # Смешиваем правильный ответ с неправильными
    options = wrong_answers + [correct_answer]
    random.shuffle(options)

    # Отправляем вопрос и варианты
    return jsonify({
        "question": current_formula['name'],
        "description": current_formula['description'],
        "options": options,
        "correct_formula_latex": f"\\({correct_answer}\\)"  # Формат LaTeX для формулы
    }), 200

# Функция для проверки ответа пользователя
def check_answer():
    data = request.json
    selected_answer = data.get('selected_answer')

    quiz = session.get('quiz', {})
    if not quiz or quiz['current_index'] >= len(quiz['questions']):
        return jsonify({"message": "Quiz not started or already finished."}), 400

    current_formula = quiz['questions'][quiz['current_index']]
    correct_answer = current_formula['formula']

    # Проверяем ответ
    is_correct = selected_answer == correct_answer
    if is_correct:
        quiz['correct_answers'] += 1
    else:
        quiz['incorrect_answers'] += 1

    # Сохраняем результат текущего вопроса
    quiz['results'].append({
        "question": current_formula['name'],
        "selected_answer": selected_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct
    })

    session['quiz'] = quiz

    # Переходим к следующему вопросу
    quiz['current_index'] += 1
    if quiz['current_index'] >= len(quiz['questions']):
        return jsonify({"message": "Quiz finished", "results": quiz['results']}), 200
    else:
        return next_question()

# Функция для завершения квиза и отправки результатов
def finish_quiz():
    quiz = session.get('quiz', {})
    if not quiz:
        return jsonify({"message": "Quiz not started or already finished."}), 400

    correct_answers = quiz['correct_answers']
    incorrect_answers = quiz['incorrect_answers']
    results = quiz['results']

    # Отправляем результаты
    return jsonify({
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "results": results
    }), 200
