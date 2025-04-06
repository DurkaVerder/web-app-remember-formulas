from flask import request
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

@modul_np.route('/modules/<int:module_id>')
class ModuleResource(Resource):
    @modul_np.doc('update_module', responses={200: 'Module updated successfully', 404: 'Module not found', 500: 'Database error'})
    @modul_np.expect(modul_model, validate=True)
    def put(self, module_id):
        try:
            module = Modul.query.get(module_id)
            if not module:
                log_error(f"Module with id {module_id} not found for update")
                return {'message': 'Module not found'}, 404

            data = request.json
            module.name = data.get('name', module.name)
            module.description = data.get('description', module.description)

            db.session.commit()
            log_info(f"Module with id {module_id} updated successfully")
            return module.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to update module with id {module_id}: {str(e)}")
            return {'message': 'Database error'}, 500

    @modul_np.doc('delete_module', responses={200: 'Module deleted successfully', 404: 'Module not found', 500: 'Database error'})
    def delete(self, module_id):
        try:
            module = Modul.query.get(module_id)
            if not module:
                log_error(f"Module with id {module_id} not found for deletion")
                return {'message': 'Module not found'}, 404

            db.session.delete(module)
            db.session.commit()
            log_info(f"Module with id {module_id} deleted successfully")
            return {'message': 'Module deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to delete module with id {module_id}: {str(e)}")
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

@formula_np.route('/formulas/<int:formula_id>')
class FormulaResource(Resource):
    @formula_np.doc('update_formula', responses={200: 'Formula updated successfully', 404: 'Formula not found', 500: 'Database error'})
    @formula_np.expect(formula_model, validate=True)
    def put(self, formula_id):
        try:
            formula = Formula.query.get(formula_id)
            if not formula:
                log_error(f"Formula with id {formula_id} not found for update")
                return {'message': 'Formula not found'}, 404

            data = request.json
            formula.name = data.get('name', formula.name)
            formula.description = data.get('description', formula.description)
            formula.formula = data.get('formula', formula.formula)
            formula.idmodul = data.get('idmodul', formula.idmodul)

            # Проверка существования нового модуля, если idmodul изменен
            if 'idmodul' in data:
                module = Modul.query.get(data['idmodul'])
                if not module:
                    log_error(f"Module with id {data['idmodul']} not found")
                    return {'message': f'Module with id {data["idmodul"]} does not exist'}, 404

            db.session.commit()
            log_info(f"Formula with id {formula_id} updated successfully")
            return formula.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to update formula with id {formula_id}: {str(e)}")
            return {'message': 'Database error'}, 500

    @formula_np.doc('delete_formula', responses={200: 'Formula deleted successfully', 404: 'Formula not found', 500: 'Database error'})
    def delete(self, formula_id):
        try:
            formula = Formula.query.get(formula_id)
            if not formula:
                log_error(f"Formula with id {formula_id} not found for deletion")
                return {'message': 'Formula not found'}, 404

            db.session.delete(formula)
            db.session.commit()
            log_info(f"Formula with id {formula_id} deleted successfully")
            return {'message': 'Formula deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to delete formula with id {formula_id}: {str(e)}")
            return {'message': 'Database error'}, 500