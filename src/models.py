from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Modul(db.Model):
    __tablename__ = 'moduls'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(255))
    status = db.Column(db.String(50))
    avatar = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "login": self.login,
            "nickname": self.nickname,
            "status": self.status,
            "avatar": self.avatar
        }

class Formula(db.Model):
    __tablename__ = 'formulas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    formula = db.Column(db.Text, nullable=False)
    idmodul = db.Column(db.Integer, db.ForeignKey('moduls.id'), nullable=False)

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

class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    success_rate = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "date": self.date.strftime('%d.%m.%Y'),
            "success_rate": self.success_rate,
            "section": self.section
        }

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    tests_passed = db.Column(db.Integer, nullable=False)
    success_rate = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "name": self.name,
            "tests_passed": self.tests_passed,
            "success_rate": self.success_rate
        }