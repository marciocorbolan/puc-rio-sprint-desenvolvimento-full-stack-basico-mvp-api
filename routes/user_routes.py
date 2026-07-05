# --- Bibliotecas de Terceiros ---
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

# --- Módulos do Projeto ---
from database import db
from models.user import User
from middlewares.decorators import token_required


user_bp = Blueprint('user', __name__)


#########################################################################


@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Exibe os dados do usuário logado
    ---
    tags:
      - Usuário
    security:
      - Bearer: []
    responses:
      200:
        description: Cadastro encontrado
      401:
        description: Credenciais inválidas
      404:
        description: Cadastro não encontrado
    """

    user = User.query.get(current_user.id)
    if not user:
        return jsonify({"message": "Cadastro não encontrado"}), 404
        
    return jsonify({
        "nome": user.nome,
        "email": user.email,
        "cpfcnpj": user.cpfcnpj
    }), 200


#########################################################################

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    Altera os dados do usuário logado
    ---
    tags:
      - Usuário
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          properties:
            nome:
              type: string
              description: Nome (opcional)
            email:
              type: string
              description: Email (opcional)
            senha:
              type: string
              description: Senha (opcional)
    responses:
      200:
        description: Cadastro atualizado com sucesso
      400:
        description: Erro de validação
      401:
        description: Credenciais inválidas
      404:
        description: Cadastro não encontrado
    """

    user = User.query.get(current_user.id)
    if not user:
        return jsonify({"message": "Cadastro não encontrado"}), 404
        
    data = request.get_json()

    if data.get('nome'):
      user.nome = data['nome']

    if data.get('email'):
      user.email = data['email']

    if data.get('senha'):
      user.senha = generate_password_hash(data['senha'])
    
    db.session.commit()
    
    return jsonify({"message": "Cadastro atualizado com sucesso!"}), 200