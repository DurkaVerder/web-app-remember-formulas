from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from models import db, Modul, Formula

# Создаем Namespace для модулей и формул
modul_np = Namespace('Add_moduls', description='Добавление модулей')
formula_np = Namespace('Add_formulas', description='Добавление формул')

# Модели для документации
modul_model = modul_np.model('Modul', {
    'name': fields.String(required=True, description='Название модуля'),
    'description': fields.String(description='Описание модуля')
})

formula_model = formula_np.model('Formula', {
    'name': fields.String(required=True, description='Название формулы'),
    'description': fields.String(required=True, description='Описание формулы'),
    'formula': fields.String(required=True, description='Текст формулы'),
    'idmodul': fields.Integer(required=True, description='ID модуля, к которому принадлежит формула')
})

# Маршрут для добавления модуля
@modul_np.route('/add_module')
class AddModule(Resource):
    @modul_np.expect(modul_model)
    @modul_np.response(201, 'Module added successfully')
    @modul_np.response(400, 'Missing required fields')
    def post(self):
        data = request.json
        name = data.get('name')
        description = data.get('description', '')

        if not name:
            return {'message': 'Module name is required'}, 400

        # Создаем и добавляем новый модуль
        new_module = Modul(name=name, description=description)
        db.session.add(new_module)
        db.session.commit()

        return jsonify(new_module.to_dict()), 201  # Возвращаем корректный JSON-ответ

# Маршрут для добавления формулы
@formula_np.route('/add_formula')
class AddFormula(Resource):
    @formula_np.expect(formula_model)
    @formula_np.response(201, 'Formula added successfully')
    @formula_np.response(400, 'Missing required fields')
    @formula_np.response(404, 'Module not found')
    def post(self):
        data = request.json
        name = data.get('name')
        description = data.get('description')
        formula_text = data.get('formula')
        idmodul = data.get('idmodul')

        # Проверка обязательных полей
        if not (name and description and formula_text and idmodul):
            return {'message': 'All fields (name, description, formula, idmodul) are required'}, 400

        # Проверка существования модуля
        module = Modul.query.get(idmodul)
        if not module:
            return {'message': f'Module with id {idmodul} does not exist'}, 404

        # Создаем и добавляем новую формулу
        new_formula = Formula(name=name, description=description, formula=formula_text, idmodul=idmodul)
        db.session.add(new_formula)
        db.session.commit()

        return jsonify(new_formula.to_dict()), 201  # Возвращаем корректный JSON-ответ
