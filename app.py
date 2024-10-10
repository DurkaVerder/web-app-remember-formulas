from flask import Flask
from config import Config
from models import db
from routes import main
from admin_routes import admin
from quiz import quiz

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(main)
app.register_blueprint(admin)
app.register_blueprint(quiz)

if __name__ == '__main__':
    app.run(debug=True)
