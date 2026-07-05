from flask import Blueprint, jsonify

basic_bp = Blueprint('basic', __name__)

@basic_bp.route('/', methods=['GET'])
@basic_bp.route('/status', methods=['GET'])
def get_info():
    """
    Retorna o status da API
    ---
    tags:
      - Geral
    responses:
      200:
        description: API está online
        schema:
          type: object
          properties:
            status:
              type: string
              description: Status da API
            mensagem:
              type: string
              description: Mensagem de status
    """

    return jsonify({
        "status": "1",
        "mensagem": "API do Pl@g - MVP PUC-Rio"
    }), 200