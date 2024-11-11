from flask import Blueprint, jsonify, request, session
import random
from models import db, Formula
from flask_restx import Resource, fields, Namespace

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
        return start_quiz(module_id)

# Маршрут для проверки ответов
@quiz_ns.route('/submit_answers')
class SubmitAnswers(Resource):
    @quiz_ns.expect(check_answers_model)
    @quiz_ns.doc(tags=['Quiz'], description="Отправить ответы на все вопросы и получить результаты квиза.")
    def post(self):
        return submit_answers()

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
        correct_answer = formula.formula
        all_formulas = Formula.query.filter(Formula.id != formula.id).all()
        wrong_answers = random.sample([f.formula for f in all_formulas], 3)
        options = wrong_answers + [correct_answer]
        random.shuffle(options)
        
        questions.append({
            "id": formula.id,
            "question": formula.name,
            "description": formula.description,
            "options": options,
            "correct_formula_latex": f"\\({correct_answer}\\)"  # Формат LaTeX для формулы
        })
    
    # Сохраняем вопросы в сессии
    session['quiz'] = {
        'module_id': module_id,
        'questions': questions,
        'correct_answers': 0,
        'incorrect_answers': 0
    }
    
    return jsonify({"questions": questions}), 200

# Функция для проверки ответов
def submit_answers():
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
        is_correct = user_answer == question['correct_formula_latex']
        if is_correct:
            correct_answers += 1
        else:
            incorrect_answers += 1
        results.append({
            "question_id": question["id"],
            "question": question["question"],
            "selected_answer": user_answer,
            "correct_answer": question["correct_formula_latex"],
            "is_correct": is_correct
        })
    
    # Итоговая статистика
    total_questions = len(quiz['questions'])
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Возвращаем результат
    return jsonify({
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "total_questions": total_questions,
        "accuracy": accuracy,
        "results": results
    }), 200