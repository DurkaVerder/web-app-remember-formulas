from flask import Blueprint, jsonify, request, session
import random
from models import db, Formula
from flask_restx import Api, Resource, fields, Namespace

quiz = Blueprint('quiz', __name__)
quiz_ns = Namespace('quiz', description='Operations related to quizzes')

# Модели данных для документации
check_answer_model = quiz_ns.model('CheckAnswer', {
    'selected_answer': fields.String(required=True, description='Выбранный пользователем ответ')
})

start_quiz_model = quiz_ns.model('StartQuiz', {
    'module_id': fields.Integer(required=True, description='ID модуля для старта квиза')
})


# Маршрут для старта квиза по модулю
@quiz_ns.route('/api/quiz/start/<int:module_id>')
class StartQuiz(Resource):
    @quiz_ns.doc(tags=['Quiz'], description="Старт квиза для указанного модуля.")
    def get(self, module_id):
        return start_quiz(module_id)


# Маршрут для получения следующего вопроса
@quiz_ns.route('/api/quiz/next_question')
class NextQuestion(Resource):
    @quiz_ns.doc(tags=['Quiz'], description="Получить следующий вопрос в текущем квизе.")
    def get(self):
        return next_question()


# Маршрут для проверки ответа пользователя
@quiz_ns.route('/api/quiz/check_answer')
class CheckAnswer(Resource):
    @quiz_ns.expect(check_answer_model)
    @quiz_ns.doc(tags=['Quiz'], description="Проверить ответ пользователя на текущий вопрос.")
    def post(self):
        return check_answer()


# Маршрут для завершения квиза
@quiz_ns.route('/api/quiz/finish')
class FinishQuiz(Resource):
    @quiz_ns.doc(tags=['Quiz'], description="Завершить квиз и получить результаты.")
    def get(self):
        return finish_quiz()


# Функция для старта квиза по определенному модулю
def start_quiz(module_id):
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    if len(formulas) < 6:
        return {"message": "Not enough formulas in the module."}, 400

    selected_formulas = random.sample(formulas, 6)
    session['quiz'] = {
        'module_id': module_id,
        'questions': [formula.to_dict() for formula in selected_formulas],
        'current_index': 0,
        'correct_answers': 0,
        'incorrect_answers': 0,
        'results': []
    }

    return next_question()


# Функция для отправки следующего вопроса
def next_question():
    quiz = session.get('quiz', {})
    if not quiz or quiz['current_index'] >= len(quiz['questions']):
        return {"message": "Quiz not started or already finished."}, 400

    current_formula = quiz['questions'][quiz['current_index']]
    correct_answer = current_formula['formula']
    all_formulas = Formula.query.filter(Formula.id != current_formula['id']).all()
    wrong_answers = random.sample([f.formula for f in all_formulas], 3)

    options = wrong_answers + [correct_answer]
    random.shuffle(options)

    return {
        "question": current_formula['name'],
        "description": current_formula['description'],
        "options": options,
        "correct_formula_latex": f"\\({correct_answer}\\)"
    }, 200


# Функция для проверки ответа пользователя
def check_answer():
    data = request.json
    selected_answer = data.get('selected_answer')

    quiz = session.get('quiz', {})
    if not quiz or quiz['current_index'] >= len(quiz['questions']):
        return {"message": "Quiz not started or already finished."}, 400

    current_formula = quiz['questions'][quiz['current_index']]
    correct_answer = current_formula['formula']

    is_correct = selected_answer == correct_answer
    if is_correct:
        quiz['correct_answers'] += 1
    else:
        quiz['incorrect_answers'] += 1

    quiz['results'].append({
        "question": current_formula['name'],
        "selected_answer": selected_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct
    })

    session['quiz'] = quiz
    quiz['current_index'] += 1

    if quiz['current_index'] >= len(quiz['questions']):
        return {"results": quiz['results']}, 200
    else:
        return next_question()


# Функция для завершения квиза и отправки результатов
def finish_quiz():
    quiz = session.get('quiz', {})
    if not quiz:
        return {"message": "Quiz not started or already finished."}, 400

    correct_answers = quiz['correct_answers']
    incorrect_answers = quiz['incorrect_answers']
    results = quiz['results']

    return {
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "results": results
    }, 200
