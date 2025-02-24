from flask import Blueprint, jsonify, request, session
import random
from models import db, Formula, Test, Topic, Modul
from flask_restx import Resource, fields, Namespace
from jwt_utils import IsAuthorized  # Предполагаем, что файл называется jwt.py
from datetime import datetime

quiz_ns = Namespace('quiz', description='Operations related to quizzes')

check_answers_model = quiz_ns.model('CheckAnswers', {
    'answers': fields.List(fields.String, required=True)
})

@quiz_ns.route('/start/<int:module_id>')
class StartQuiz(Resource):
    @quiz_ns.doc(tags=['Quiz'])
    def get(self, module_id):
        return start_quiz(module_id)

@quiz_ns.route('/submit_answers')
class SubmitAnswers(Resource):
    @quiz_ns.expect(check_answers_model)
    @quiz_ns.doc(tags=['Quiz'])
    def post(self):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            return {"message": auth_result["error"]}, auth_result["status"]
        
        user_id = auth_result['user_id']
        return submit_answers(user_id)

def start_quiz(module_id):
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    if len(formulas) < 6:
        return {"message": "Not enough formulas in the module."}, 400
    
    selected_formulas = random.sample(formulas, 6)
    
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
            "correct_formula_latex": f"\\({correct_answer}\\)"
        })
    
    session['quiz'] = {
        'module_id': module_id,
        'questions': questions,
        'correct_answers': 0,
        'incorrect_answers': 0
    }
    
    return {"questions": questions}, 200

def submit_answers(user_id):
    data = request.json
    user_answers = data.get('answers', [])
    
    quiz = session.get('quiz', {})
    if not quiz:
        return {"message": "Quiz not started."}, 400
    
    correct_answers = 0
    incorrect_answers = 0
    results = []
    
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
    
    total_questions = len(quiz['questions'])
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Получаем название модуля для использования как section и name
    module = Modul.query.get(quiz['module_id'])
    section_name = module.name if module else "Unknown"

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
    
    db.session.commit()

    return {
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "total_questions": total_questions,
        "accuracy": accuracy,
        "results": results
    }, 200