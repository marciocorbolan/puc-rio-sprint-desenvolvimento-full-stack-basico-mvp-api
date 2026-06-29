# --- Bibliotecas de Terceiros ---
from flask import Blueprint, request, jsonify
import jwt
import datetime
from werkzeug.security import check_password_hash, generate_password_hash

# --- Módulos do Projeto ---
from config import SECRET_KEY
from database import db
from models.user import User
from middlewares.decorators import token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """
    Exibe os dados do usuário logado
    ---
    tags:
      - Usuário
    security:
      - Bearer: []
    """
    token = request.headers.get('Authorization').split(" ")[1]
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    user = User.query.get(data['user_id'])
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
def update_profile():
    """
    Altera os dados do usuário logado
    ---
    tags:
      - Usuário
    security:
      - Bearer: []
    """
    token = request.headers.get('Authorization').split(" ")[1]
    data_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    user = User.query.get(data_token['user_id'])
    if not user:
        return jsonify({"message": "Cadastro não encontrado"}), 404
        
    data = request.get_json()

    if data.get('nome'):
      user.nome = data['nome']

    if data.get('email'):
      user.email = data['email']
    
    db.session.commit()
    
    return jsonify({"message": "Cadastro atualizado com sucesso!"}), 200