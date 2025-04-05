from flask import Blueprint, jsonify, request
from models import db, Modul, Formula, User, UsersFormulas, UsersModuls
from flask_restx import Api, Resource, fields, Namespace
from logger import log_info, log_error, log_debug 

module_ns = Namespace('module', description='Operations related to modules')

# Определение модели для Swagger
user_formula_model = module_ns.model('UserFormula', {
    'message': fields.String(description='Message indicating assignment success')
})

user_module_model = module_ns.model('UserModule', {
    'message': fields.String(description='Message indicating assignment success')
})

# Получение всех модулей
@module_ns.route('/api/modules', methods=['GET'])
class ModuleList(Resource):
    @module_ns.doc('list_modules')
    def get(self):
        """Получение всех модулей."""
        try:
            result = list_modules()
            log_info(f"Retrieved {len(result)} modules successfully")
            return result
        except Exception as e:
            log_error(f"Error retrieving modules: {str(e)}")
            return {"message": "Internal server error"}, 500

# Получение всех формул по ID модуля
@module_ns.route('/api/module/<int:module_id>/formulas', methods=['GET'])
class FormulaList(Resource):
    @module_ns.doc('list_formulas')
    def get(self, module_id):
        """Получение всех формул по ID модуля."""
        try:
            result = list_formulas(module_id)
            log_info(f"Retrieved {len(result)} formulas for module_id {module_id}")
            return result
        except Exception as e:
            log_error(f"Error retrieving formulas for module_id {module_id}: {str(e)}")
            return {"message": f"Module {module_id} not found or error occurred"}, 404

# Назначить формулу пользователю
@module_ns.route('/api/assign_formula_to_user', methods=['POST'])
class AssignFormula(Resource):
    @module_ns.doc('assign_formula_to_user')
    @module_ns.expect(module_ns.model('AssignFormulaPayload', {
        'user_id': fields.Integer(required=True, description='ID пользователя, которому назначается формула'),
        'formula_id': fields.Integer(required=True, description='ID формулы для назначения')
    }))
    @module_ns.marshal_with(user_formula_model)
    def post(self):
        """Назначить формулу пользователю."""
        data = request.json
        user_id = data.get('user_id')
        formula_id = data.get('formula_id')

        if not user_id or not formula_id:
            log_error("Missing user_id or formula_id in request")
            return {"message": "User ID and Formula ID are required"}, 400

        try:
            user_formula = UsersFormulas(iduser=user_id, idformula=formula_id)
            db.session.add(user_formula)
            db.session.commit()
            log_info(f"Formula {formula_id} assigned to user {user_id}")
            return {"message": f"Formula {formula_id} assigned to user {user_id}"}, 200
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to assign formula {formula_id} to user {user_id}: {str(e)}")
            return {"message": "Database error"}, 500

# Назначить модуль пользователю
@module_ns.route('/api/assign_module_to_user', methods=['POST'])
class AssignModule(Resource):
    @module_ns.doc('assign_module_to_user')
    @module_ns.expect(module_ns.model('AssignModulePayload', {
        'user_id': fields.Integer(required=True, description='ID пользователя, которому назначается модуль'),
        'module_id': fields.Integer(required=True, description='ID модуля для назначения')
    }))
    @module_ns.marshal_with(user_module_model)
    def post(self):
        """Назначить модуль пользователю."""
        data = request.json
        user_id = data.get('user_id')
        module_id = data.get('module_id')

        if not user_id or not module_id:
            log_error("Missing user_id or module_id in request")
            return {"message": "User ID and Module ID are required"}, 400

        try:
            user_module = UsersModuls(iduser=user_id, idmodul=module_id)
            db.session.add(user_module)
            db.session.commit()
            log_info(f"Module {module_id} assigned to user {user_id}")
            return {"message": f"Module {module_id} assigned to user {user_id}"}, 200
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to assign module {module_id} to user {user_id}: {str(e)}")
            return {"message": "Database error"}, 500

def list_modules():
    try:
        modules = Modul.query.all()
        return [module.to_dict() for module in modules]
    except Exception as e:
        log_error(f"Error in list_modules: {str(e)}")
        raise

def list_formulas(module_id):
    try:
        module = Modul.query.get_or_404(module_id)
        formulas = Formula.query.filter_by(idmodul=module_id).all()
        return [formula.to_dict() for formula in formulas]
    except Exception as e:
        log_error(f"Error in list_formulas for module_id {module_id}: {str(e)}")
        raise