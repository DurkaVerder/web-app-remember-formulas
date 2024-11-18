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

    def to_dict(self):
        return {
            "nickname": self.nickname
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
