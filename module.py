from flask import Blueprint, jsonify, request, session
from models import db, Modul, Formula, User, UsersFormulas, UsersModuls


module = Blueprint('module', __name__)

# Получение всех модулей
@module.route('/api/modules', methods=['GET'])
def api_list_modules():
    return list_modules()

# Получение всех формул по ID модуля
@module.route('/api/module/<int:module_id>/formulas', methods=['GET'])
def api_list_formulas(module_id):
    return list_formulas(module_id)



# Назначить формулу пользователю
@module.route('/api/assign_formula_to_user/<int:user_id>/<int:formula_id>', methods=['POST'])
def assign_formula_to_user(user_id, formula_id):
    user_formula = UsersFormulas(iduser=user_id, idformula=formula_id)
    db.session.add(user_formula)
    db.session.commit()
    return jsonify({"message": f"Formula {formula_id} assigned to user {user_id}"}), 200

# Назначить модуль пользователю
@module.route('/api/assign_module_to_user/<int:user_id>/<int:module_id>', methods=['POST'])
def assign_module_to_user(user_id, module_id):
    user_module = UsersModuls(iduser=user_id, idmodul=module_id)
    db.session.add(user_module)
    db.session.commit()
    return jsonify({"message": f"Module {module_id} assigned to user {user_id}"}), 200



def list_modules():
    modules = Modul.query.all()
    return jsonify([module.to_dict() for module in modules])


def list_formulas(module_id):
    module = Modul.query.get_or_404(module_id)
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    return jsonify([formula.to_dict() for formula in formulas])