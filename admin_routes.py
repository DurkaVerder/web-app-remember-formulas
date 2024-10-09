from flask import Blueprint, jsonify, request, session
from models import db, Modul, Formula, User, UsersFormulas, UsersModuls

admin = Blueprint('admin', __name__)

# Добавление новой формулы
@admin.route('/api/add_formula', methods=['POST'])
def api_add_formula():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    formula = data.get('formula')
    module_id = data.get('module_id')

    new_formula = Formula(name=name, description=description, formula=formula, idmodul=module_id)
    db.session.add(new_formula)
    db.session.commit()

    return jsonify({"message": "Formula added successfully!"}), 201