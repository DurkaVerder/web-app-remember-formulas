from flask import Blueprint, request
from flask_restx import Api, Resource, fields, Namespace
from models import db, Formula

admin = Blueprint('admin', __name__)
admin_ns = Namespace('admin', description='Operations related to admin')

# Определение модели для валидации входящих данных
formula_model = admin_ns.model('Formula', {
    'name': fields.String(required=True, description='Имя формулы'),
    'description': fields.String(required=True, description='Описание формулы'),
    'formula': fields.String(required=True, description='Текст формулы'),
    'module_id': fields.Integer(required=True, description='ID модуля')
})

@admin_ns.route('/api/add_formula')
class AddFormula(Resource):
    @admin_ns.expect(formula_model)
    def post(self):
        data = request.json
        name = data.get('name')
        description = data.get('description')
        formula = data.get('formula')
        module_id = data.get('module_id')

        new_formula = Formula(name=name, description=description, formula=formula, idmodul=module_id)
        db.session.add(new_formula)
        db.session.commit()

        return {"message": "Formula added successfully!"}, 201

