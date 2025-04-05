from flask import Blueprint, jsonify, request, session
import random
from models import db, Formula, Test, Topic, Modul, Achievement
from flask_restx import Resource, fields, Namespace
from jwt_utils import IsAuthorized
from datetime import datetime
from logger import log_info, log_error, log_debug

quiz_ns = Namespace('quiz', description='Operations related to quizzes')

# Модели данных для документации
check_answers_model = quiz_ns.model('CheckAnswers', {
    'answers': fields.List(fields.String, required=True, description='Массив ответов пользователя')
})

symbol_quiz_model = quiz_ns.model('SymbolQuizAnswers', {
    'answers': fields.List(fields.List(fields.String), required=True, description='Массив ответов пользователя (массив символов для каждой формулы)')
})

# Маршрут для старта обычного квиза
@quiz_ns.route('/start/<int:module_id>')
class StartQuiz(Resource):
    @quiz_ns.doc(tags=['Quiz'], description="Старт квиза для указанного модуля с отправкой всех вопросов.")
    def get(self, module_id):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            log_error(f"Quiz start failed for module {module_id}: {auth_result['error']}")
            return {"message": auth_result["error"]}, auth_result["status"]
        
        log_info(f"Starting quiz for module {module_id} by user {auth_result['user_id']}")
        return start_quiz(module_id)

# Маршрут для проверки ответов обычного квиза
@quiz_ns.route('/submit_answers')
class SubmitAnswers(Resource):
    @quiz_ns.expect(check_answers_model)
    @quiz_ns.doc(tags=['Quiz'], description="Отправить ответы на все вопросы и получить результаты квиза.")
    def post(self):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            log_error(f"Quiz submission failed: {auth_result['error']}")
            return {"message": auth_result["error"]}, auth_result["status"]
        
        user_id = auth_result['user_id']
        log_info(f"User {user_id} submitting answers for quiz")
        return submit_answers(user_id)

# Маршрут для старта квиза с символами
@quiz_ns.route('/start_symbol_quiz/<int:module_id>')
class StartSymbolQuiz(Resource):
    @quiz_ns.doc(tags=['Quiz'], description="Старт квиза с разбиением формул на символы для указанного модуля.")
    def get(self, module_id):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            log_error(f"Symbol quiz start failed for module {module_id}: {auth_result['error']}")
            return {"message": auth_result["error"]}, auth_result["status"]
        
        log_info(f"Starting symbol quiz for module {module_id} by user {auth_result['user_id']}")
        return start_symbol_quiz(module_id)

# Маршрут для проверки ответов квиза с символами
@quiz_ns.route('/submit_symbol_answers')
class SubmitSymbolAnswers(Resource):
    @quiz_ns.expect(symbol_quiz_model)
    @quiz_ns.doc(tags=['Quiz'], description="Отправить ответы для квиза с символами и получить результаты.")
    def post(self):
        auth_result = IsAuthorized()
        if "error" in auth_result:
            log_error(f"Symbol quiz submission failed: {auth_result['error']}")
            return {"message": auth_result["error"]}, auth_result["status"]
        
        user_id = auth_result['user_id']
        log_info(f"User {user_id} submitting answers for symbol quiz")
        return submit_symbol_answers(user_id)

# Функция для старта обычного квиза
def start_quiz(module_id):
    try:
        module = Modul.query.get(module_id)
        if not module:
            log_error(f"Module {module_id} not found for quiz start")
            return {"message": "Module not found."}, 404

        formulas = Formula.query.filter_by(idmodul=module_id).all()
        if len(formulas) < 6:
            log_error(f"Not enough formulas ({len(formulas)}) in module {module_id} for quiz")
            return {"message": "Not enough formulas in the module."}, 400

        selected_formulas = random.sample(formulas, 6)
        questions = []
        for formula in selected_formulas:
            correct_name = formula.name
            all_formulas = Formula.query.filter(Formula.id != formula.id).all()
            wrong_names = random.sample([f.name for f in all_formulas], 3)
            options = wrong_names + [correct_name]
            random.shuffle(options)

            questions.append({
                "id": formula.id,
                "question": formula.formula,
                "options": options,
                "correct_name": correct_name
            })
        
        session['quiz'] = {
            'module_id': module_id,
            'questions': questions,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'start_time': datetime.now().isoformat()
        }
        log_info(f"Quiz started for module {module_id} with {len(questions)} questions")
        return {"questions": questions}, 200
    except Exception as e:
        log_error(f"Error starting quiz for module {module_id}: {str(e)}")
        return {"message": "Internal server error"}, 500

# Функция для проверки ответов обычного квиза
def submit_answers(user_id):
    try:
        data = request.json
        user_answers = data.get('answers', [])
        
        quiz = session.get('quiz', {})
        if not quiz:
            log_error(f"User {user_id} attempted to submit answers but quiz not started")
            return {"message": "Quiz not started."}, 400
        
        start_time = datetime.fromisoformat(quiz['start_time'])
        end_time = datetime.now()
        
        correct_answers = 0
        incorrect_answers = 0
        results = []
        
        for i, user_answer in enumerate(user_answers):
            if i >= len(quiz['questions']):
                break
            question = quiz['questions'][i]
            is_correct = user_answer == question['correct_name']
            if is_correct:
                correct_answers += 1
            else:
                incorrect_answers += 1
            results.append({
                "question_id": question["id"],
                "question": question["question"],
                "selected_answer": user_answer,
                "correct_answer": question["correct_name"],
                "is_correct": is_correct
            })
        
        total_questions = len(quiz['questions'])
        accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        module = Modul.query.get(quiz['module_id'])
        if not module:
            log_error(f"Module {quiz['module_id']} not found during quiz submission for user {user_id}")
            return {"message": "Module not found"}, 404
        section_name = module.name

        new_test = Test(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            date=datetime.now().date(),
            success_rate=int(accuracy),
            section=section_name
        )
        db.session.add(new_test)

        topic = Topic.query.filter_by(user_id=user_id, name=section_name).first()
        if topic:
            topic.tests_passed += 1
            topic.success_rate = ((topic.success_rate * (topic.tests_passed - 1)) + accuracy) / topic.tests_passed
        else:
            topic = Topic(
                user_id=user_id,
                name=section_name,
                tests_passed=1,
                success_rate=accuracy
            )
            db.session.add(topic)
        
        db.session.commit()
        from achievements import check_achievements
        check_achievements(user_id)
        log_info(f"Quiz submitted for user {user_id}: {correct_answers}/{total_questions} correct, accuracy {accuracy}%")
        
        session.pop('quiz', None)
        return {
            "correct_answers": correct_answers,
            "incorrect_answers": incorrect_answers,
            "total_questions": total_questions,
            "accuracy": accuracy,
            "results": results
        }, 200
    except Exception as e:
        db.session.rollback()
        log_error(f"Error submitting quiz answers for user {user_id}: {str(e)}")
        return {"message": f"Database error: {str(e)}"}, 500

# Функция для старта квиза с символами
def start_symbol_quiz(module_id):
    try:
        module = Modul.query.get(module_id)
        if not module:
            log_error(f"Module {module_id} not found for symbol quiz start")
            return {"message": "Module not found."}, 404

        formulas = Formula.query.filter_by(idmodul=module_id).all()
        if len(formulas) < 6:
            log_error(f"Not enough formulas ({len(formulas)}) in module {module_id} for symbol quiz")
            return {"message": "Not enough formulas in the module."}, 400

        selected_formulas = random.sample(formulas, 6)
        questions = []
        
        for formula in selected_formulas:
            formula_cleaned = formula.formula.replace(" ", "")
            symbols = list(formula_cleaned)
            extra_symbols = ['+', '-', '=', '(', ')', '*', '/', '^', 'x', 'y', 'z']
            distractors = random.sample([sym for sym in extra_symbols if sym not in symbols], min(5, len(symbols)))
            
            all_symbols = symbols + distractors
            random.shuffle(all_symbols)
            
            questions.append({
                "id": formula.id,
                "name": formula.name,
                "correct_formula": formula_cleaned,
                "symbols": all_symbols,
                "length": len(symbols)
            })
        
        session['symbol_quiz'] = {
            'module_id': module_id,
            'questions': questions,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'start_time': datetime.now().isoformat()
        }
        log_info(f"Symbol quiz started for module {module_id} with {len(questions)} questions")
        return {"questions": questions}, 200
    except Exception as e:
        log_error(f"Error starting symbol quiz for module {module_id}: {str(e)}")
        return {"message": "Internal server error"}, 500

# Функция для проверки ответов квиза с символами
def submit_symbol_answers(user_id):
    try:
        data = request.json
        user_answers = data.get('answers', [])
        
        quiz = session.get('symbol_quiz', {})
        if not quiz:
            log_error(f"User {user_id} attempted to submit symbol quiz answers but quiz not started")
            return {"message": "Symbol quiz not started."}, 400
        
        start_time = datetime.fromisoformat(quiz['start_time'])
        end_time = datetime.now()
        
        correct_answers = 0
        incorrect_answers = 0
        results = []
        
        for i, user_answer in enumerate(user_answers):
            if i >= len(quiz['questions']):
                break
            question = quiz['questions'][i]
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
            log_error(f"Module {quiz['module_id']} not found during symbol quiz submission for user {user_id}")
            return {"message": "Module not found"}, 404
        section_name = module.name

        new_test = Test(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            date=datetime.now().date(),
            success_rate=int(accuracy),
            section=section_name + " (Symbol Quiz)"
        )
        db.session.add(new_test)

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
        
        db.session.commit()
        from achievements import check_achievements
        check_achievements(user_id)
        log_info(f"Symbol quiz submitted for user {user_id}: {correct_answers}/{total_questions} correct, accuracy {accuracy}%")
        
        session.pop('symbol_quiz', None)
        return {
            "correct_answers": correct_answers,
            "incorrect_answers": incorrect_answers,
            "total_questions": total_questions,
            "accuracy": accuracy,
            "results": results
        }, 200
    except Exception as e:
        db.session.rollback()
        log_error(f"Error submitting symbol quiz answers for user {user_id}: {str(e)}")
        return {"message": f"Database error: {str(e)}"}, 500