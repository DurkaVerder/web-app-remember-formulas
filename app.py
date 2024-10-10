from flask import Flask
from config import Config
from models import db
from module import module
from admin_routes import admin
from quiz import quiz
from user import user

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(module)
app.register_blueprint(admin)
app.register_blueprint(quiz)
app.register_blueprint(user)

if __name__ == '__main__':
    app.run(debug=True)
