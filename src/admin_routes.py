from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from models import db, Modul, Formula, Video
from logger import log_info, log_error, log_debug

modul_np = Namespace('Add_moduls', description='Добавление модулей')
formula_np = Namespace('Add_formulas', description='Добавление формул')


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
            log_error("Missing module name in request")
            return {'message': 'Module name is required'}, 400

        try:
            new_module = Modul(name=name, description=description)
            db.session.add(new_module)
            db.session.commit()
            log_info(f"Module '{name}' added successfully")
            return new_module.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to add module: {str(e)}")
            return {'message': 'Database error'}, 500

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

        if not (name and description and formula_text and idmodul):
            log_error("Missing required fields in formula request")
            return {'message': 'All fields (name, description, formula, idmodul) are required'}, 400

        module = Modul.query.get(idmodul)
        if not module:
            log_error(f"Module with id {idmodul} not found")
            return {'message': f'Module with id {idmodul} does not exist'}, 404

        try:
            new_formula = Formula(name=name, description=description, formula=formula_text, idmodul=idmodul)
            db.session.add(new_formula)
            db.session.commit()
            log_info(f"Formula '{name}' added successfully to module {idmodul}")
            return new_formula.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to add formula: {str(e)}")
            return {'message': 'Database error'}, 500

