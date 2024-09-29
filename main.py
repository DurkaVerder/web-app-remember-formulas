from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:durka@localhost/web-site-for-remember-formulas'  # Измените на ваши данные
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "secret_key"

db = SQLAlchemy(app)


# Модели
class Modul(db.Model):
    __tablename__ = 'moduls'  # Имя таблицы в базе данных

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Используйте строку для хранения паролей
    nickname = db.Column(db.String(255))
    status = db.Column(db.String(50))


class Formula(db.Model):
    __tablename__ = 'formulas'  # Имя таблицы в базе данных

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)  # Уникальное значение
    description = db.Column(db.Text, nullable=False)  # Уникальное значение убрано, чтобы можно было использовать одинаковые описания
    formula = db.Column(db.Text, nullable=False)  # Уникальное значение убрано, чтобы можно было использовать одинаковые формулы
    idmodul = db.Column(db.Integer, db.ForeignKey('moduls.id'), nullable=False)  # Используйте то же имя в нижнем регистре

    modul = db.relationship('Modul', backref='formulas')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'formula': self.formula,
            'idmodul': self.idmodul
        }


class UsersFormulas(db.Model):
    __tablename__ = 'usersformulas'
    iduser = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    idformula = db.Column(db.Integer, db.ForeignKey('formulas.id'), primary_key=True)


class UsersModuls(db.Model):
    __tablename__ = 'usersmoduls'
    iduser = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    idmodul = db.Column(db.Integer, db.ForeignKey('moduls.id'), primary_key=True)


# Создание таблиц
with app.app_context():
    db.create_all()

# Статистика пользователей
user_stats = {}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/modules')
def list_modules():
    modules = Modul.query.all()
    return render_template('modules.html', modules=modules)


@app.route('/module/<int:module_id>')
def list_formulas(module_id):
    module = Modul.query.get_or_404(module_id)
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    return render_template('formulas.html', module=module, formulas=formulas)


@app.route('/add_formula', methods=['GET', 'POST'])
def add_formula():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        formula = request.form['formula']
        module_id = request.form['module_id']

        new_formula = Formula(name=name, description=description, formula=formula, idmodul=module_id)
        db.session.add(new_formula)
        db.session.commit()

        return redirect(url_for('list_formulas', module_id=module_id))

    modules = Modul.query.all()
    return render_template('add_formula.html', modules=modules)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        nickname = request.form['nickname']
        status = request.form['status']

        new_user = User(login=login, password=password, nickname=nickname, status=status)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/assign_formula_to_user/<int:user_id>/<int:formula_id>')
def assign_formula_to_user(user_id, formula_id):
    user_formula = UsersFormulas(iduser=user_id, idformula=formula_id)
    db.session.add(user_formula)
    db.session.commit()
    return f"Формула {formula_id} назначена пользователю {user_id}"


@app.route('/assign_module_to_user/<int:user_id>/<int:module_id>')
def assign_module_to_user(user_id, module_id):
    user_module = UsersModuls(iduser=user_id, idmodul=module_id)
    db.session.add(user_module)
    db.session.commit()
    return f"Модуль {module_id} назначен пользователю {user_id}"


@app.route('/quiz/<int:topic>', methods=['GET'])
def quiz(topic):
    session['current_topic'] = topic
    formulas = Formula.query.filter_by(idmodul=topic).all()
    random.shuffle(formulas)

    # Сохраняем только идентификаторы формул или словари
    session['shuffled_formulas'] = [formula.to_dict() for formula in formulas]
    session['quiz_index'] = 0
    session['correct_answers'] = 0

    return redirect(url_for('take_quiz'))



@app.route('/take_quiz', methods=['GET', 'POST'])
def take_quiz():
    if request.method == 'POST':
        answer = request.form['answer']
        correct = request.form['correct']

        if answer == correct:
            session['correct_answers'] += 1

        session['quiz_index'] += 1

    quiz_index = session.get('quiz_index', 0)
    shuffled_formulas = session.get('shuffled_formulas', [])

    if quiz_index >= len(shuffled_formulas):
        return redirect(url_for('quiz_complete'))

    formula_data = shuffled_formulas[quiz_index]

    # Создайте объект Formula из данных
    formula = Formula(id=formula_data['id'], name=formula_data['name'], description=formula_data['description'], formula=formula_data['formula'])

    return render_template('quiz.html', formula=formula)



@app.route('/quiz_complete')
def quiz_complete():
    correct_answers = session.get('correct_answers', 0)
    total_questions = len(session.get('shuffled_formulas', []))

    return render_template('quiz_complete.html', correct_answers=correct_answers, total_questions=total_questions)


if __name__ == '__main__':
    app.run(debug=True)
