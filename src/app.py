from flask import Flask
from flask_restx import Api
from config import Config
from models import db
from module import module_ns
from admin_routes import modul_np, formula_np
from quiz import quiz_ns
from user import user_ns
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
application = app
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()
    try:
        from migration import migrate_database
        migrate_database()
        print("Database migration completed successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

api.add_namespace(module_ns)
api.add_namespace(modul_np)
api.add_namespace(formula_np)
api.add_namespace(quiz_ns)
api.add_namespace(user_ns)

if __name__ == '__main__':
    app.run(debug=True)