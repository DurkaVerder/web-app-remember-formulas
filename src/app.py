from flask import Flask
from flask_restx import Api

from config import Config
from models import db
from module import module_ns
from admin_routes import admin_ns
from quiz import quiz_ns
from user import user_ns
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)
application = app
app.config.from_object(Config)
db.init_app(app)


with app.app_context():
    db.create_all()

api.add_namespace(module_ns)
api.add_namespace(admin_ns)
api.add_namespace(quiz_ns)
api.add_namespace(user_ns)

if __name__ == '__main__':
    app.run(debug=True)

