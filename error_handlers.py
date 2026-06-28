from flask import jsonify

def register_error_handlers(app):
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "erro": "Recurso não encontrado",
            "codigo": 404
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "erro": "Erro interno no servidor",
            "codigo": 500
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "erro": "Requisição inválida",
            "codigo": 400
        }), 400