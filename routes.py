# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Modul, Formula, User, UsersFormulas, UsersModuls
import random

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/modules')
def list_modules():
    modules = Modul.query.all()
    return render_template('modules.html', modules=modules)

@main.route('/module/<int:module_id>')
def list_formulas(module_id):
    module = Modul.query.get_or_404(module_id)
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    return render_template('formulas.html', module=module, formulas=formulas)

@main.route('/add_formula', methods=['GET', 'POST'])
def add_formula():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        formula = request.form['formula']
        module_id = request.form['module_id']

        new_formula = Formula(name=name, description=description, formula=formula, idmodul=module_id)
        db.session.add(new_formula)
        db.session.commit()

        return redirect(url_for('main.list_formulas', module_id=module_id))

    modules = Modul.query.all()
    return render_template('add_formula.html', modules=modules)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        nickname = request.form['nickname']
        status = request.form['status']

        new_user = User(login=login, password=password, nickname=nickname, status=status)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.home'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login']
        password_input = request.form['password']
        
        user = User.query.filter_by(login=login_input, password=password_input).first()
        
        if user:
            session['user_id'] = user.id
            session['nickname'] = user.nickname
            return redirect(url_for('main.home'))
        else:
            return render_template('login.html', error="Неправильный логин или пароль.")

    return render_template('login.html')



@main.route('/assign_formula_to_user/<int:user_id>/<int:formula_id>')
def assign_formula_to_user(user_id, formula_id):
    user_formula = UsersFormulas(iduser=user_id, idformula=formula_id)
    db.session.add(user_formula)
    db.session.commit()
    return f"Формула {formula_id} назначена пользователю {user_id}"

@main.route('/assign_module_to_user/<int:user_id>/<int:module_id>')
def assign_module_to_user(user_id, module_id):
    user_module = UsersModuls(iduser=user_id, idmodul=module_id)
    db.session.add(user_module)
    db.session.commit()
    return f"Модуль {module_id} назначен пользователю {user_id}"


@main.route('/quiz/<int:module_id>', methods=['GET'])
def start_quiz(module_id):
    session['current_module'] = module_id
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    
    # Перемешиваем формулы
    random.shuffle(formulas)

    # Сохраняем перемешанные формулы в сессии
    session['shuffled_formulas'] = [formula.to_dict() for formula in formulas]
    session['quiz_index'] = 0
    session['correct_answers'] = 0

    return redirect(url_for('main.take_quiz'))


@main.route('/take_quiz', methods=['GET', 'POST'])
def take_quiz():
    if request.method == 'POST':
        answer = request.form['answer']
        correct = request.form['correct']

        # Проверка правильности ответа
        if answer.strip() == correct.strip():
            session['correct_answers'] += 1

        session['quiz_index'] += 1

    quiz_index = session.get('quiz_index', 0)
    shuffled_formulas = session.get('shuffled_formulas', [])

    if quiz_index >= len(shuffled_formulas):
        return redirect(url_for('main.quiz_complete'))

    formula_data = shuffled_formulas[quiz_index]
    formula = Formula(id=formula_data['id'], name=formula_data['name'], description=formula_data['description'], formula=formula_data['formula'])

    return render_template('quiz.html', formula=formula)


@main.route('/quiz_complete')
def quiz_complete():
    correct_answers = session.get('correct_answers', 0)
    total_questions = len(session.get('shuffled_formulas', []))

    return render_template('quiz_complete.html', correct_answers=correct_answers, total_questions=total_questions)
