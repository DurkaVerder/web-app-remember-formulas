from flask import Blueprint, jsonify, request
from models import db, Modul, Formula, User, UsersFormulas, UsersModuls
from flask_restx import Api, Resource, fields, Namespace

module = Blueprint('module', __name__)
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
        return list_modules()


# Получение всех формул по ID модуля
@module_ns.route('/api/module/<int:module_id>/formulas', methods=['GET'])
class FormulaList(Resource):
    @module_ns.doc('list_formulas')
    def get(self, module_id):
        """Получение всех формул по ID модуля."""
        return list_formulas(module_id)


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
        user_id = data['user_id']
        formula_id = data['formula_id']

        user_formula = UsersFormulas(iduser=user_id, idformula=formula_id)
        db.session.add(user_formula)
        db.session.commit()

        return {"message": f"Formula {formula_id} assigned to user {user_id}"}, 200


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
        user_id = data['user_id']
        module_id = data['module_id']

        user_module = UsersModuls(iduser=user_id, idmodul=module_id)
        db.session.add(user_module)
        db.session.commit()

        return {"message": f"Module {module_id} assigned to user {user_id}"}, 200


def list_modules():
    modules = Modul.query.all()
    return [module.to_dict() for module in modules]


def list_formulas(module_id):
    module = Modul.query.get_or_404(module_id)
    formulas = Formula.query.filter_by(idmodul=module_id).all()
    return [formula.to_dict() for formula in formulas]
