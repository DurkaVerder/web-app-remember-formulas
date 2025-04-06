from flask import Flask
from flask_restx import Api
from config import Config
from models import db
from module import module_ns
from admin_routes import modul_np, formula_np
from quiz import quiz_ns
from user import user_ns
from video import video_ns
from flask_cors import CORS
from logger import log_info, log_error, log_debug 

app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
application = app
app.config.from_object(Config)
db.init_app(app)

log_info("Starting Flask application initialization")

with app.app_context():
    try:
        db.create_all()
        log_info("Database tables created successfully")
    except Exception as e:
        log_error(f"Error creating database tables: {str(e)}")
    
    try:
        from migration import migrate_database
        migrate_database()
        log_info("Database migration completed successfully")
    except Exception as e:
        log_error(f"Error during database migration: {str(e)}")

api.add_namespace(module_ns)
api.add_namespace(modul_np)
api.add_namespace(formula_np)
api.add_namespace(quiz_ns)
api.add_namespace(user_ns)
api.add_namespace(video_ns)

if __name__ == '__main__':
    try:
        log_info("Starting Flask development server")
        app.run(debug=True)
    except Exception as e:
        log_error(f"Failed to start Flask server: {str(e)}")