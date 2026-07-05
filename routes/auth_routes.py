# --- Bibliotecas de Terceiros ---
from flask import Blueprint, request, jsonify
import jwt
import datetime
from werkzeug.security import check_password_hash, generate_password_hash

# --- Módulos do Projeto ---
import config
from database import db
from models.user import User
from middlewares.decorators import token_required, login_limiter


auth_bp = Blueprint('auth', __name__)


#########################################################################


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Cadastra um novo usuário
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - cpfcnpj
            - nome
            - email
            - senha
          properties:
            cpfcnpj:
              type: string
              description: CPF ou CNPJ (obrigatório)
            nome:
              type: string
              description: Nome (obrigatório)
            email:
              type: string
              description: Email (obrigatório)
            senha:
              type: string
              description: Senha (obrigatório)
    responses:
      201:
        description: Cadastro criado com sucesso
      400:
        description: Erro de validação
    """

    data = request.get_json()
    
    # Validação simples
    cpfcnpj = data.get('cpfcnpj')
    senha = data.get('senha')
    nome = data.get('nome')
    email = data.get('email')

    # Verifica se o CPF/CNPJ foi informado
    if not cpfcnpj:
        return jsonify({"message": "CPF/CNPJ não informados"}), 400
    # Verifica se o CPF/CNPJ está em uso
    user = User.query.filter_by(cpfcnpj=cpfcnpj).first()
    if user:
        return jsonify({"message": "CPF/CNPJ em uso"}), 400
    
    # Verifica se a senha foi informada
    if not senha:
        return jsonify({"message": "Senha não informada"}), 400
    
    # Verifica se o nome foi informado
    if not nome:
        return jsonify({"message": "Nome não informado"}), 400
    
    # Verifica se o email foi informado
    if not email:
        return jsonify({"message": "Email não informado"}), 400
    # Verifica se o email está em uso
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "Email em uso"}), 400

    # Criar o objeto usuário
    novo_usuario = User(
        cpfcnpj=cpfcnpj,
        nome=nome,
        email=email,
        senha=generate_password_hash(senha),
        status_id=1
    )
    
    db.session.add(novo_usuario)
    db.session.commit()
    
    return jsonify({"message": "Cadastro criado com sucesso"}), 201


#########################################################################

@auth_bp.route('/login', methods=['POST'])
@login_limiter
def login():
    """
    Realiza o login e retorna um token JWT
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - cpfcnpj
            - senha
          properties:
            cpfcnpj:
              type: string
              description: CPF ou CNPJ (obrigatório)
            senha:
              type: string
              description: Senha (obrigatório)
    responses:
      200:
        description: Token JWT retornado
      400:
        description: Erro de validação
      401:
        description: Credenciais inválidas
    """

    data = request.get_json()
    cpfcnpj = data.get('cpfcnpj')
    senha = data.get('senha')

    # Validação básica dos campos
    if not cpfcnpj:
        return jsonify({"message": "CPF/CNPJ não informados"}), 400
    if not senha:
        return jsonify({"message": "Senha não informada"}), 400

    #  Verifica se o usuário existe e se a senha está correta
    user = User.query.filter_by(cpfcnpj=cpfcnpj).first()
    if not user or not check_password_hash(user.senha, senha):
        return jsonify({"message": "CPF/CNPJ ou senha inválidos"}), 401
    
    # Tempo de expiração configurável
    expiration = datetime.datetime.now(datetime.timezone.utc) + \
                 datetime.timedelta(hours=config.JWT_EXPIRATION_HOURS)

    # Criação do token
    token = jwt.encode({
        'user_id': user.id,
        'cpfcnpj': user.cpfcnpj,
        'email': user.email,
        'nome': user.nome,
        'exp': expiration
    }, config.SECRET_KEY, algorithm="HS256")

    return jsonify({
        'token': token,
        'user_id': user.id,
        'expires_in': f"{config.JWT_EXPIRATION_HOURS} horas"
    })


#########################################################################

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Realiza o logout (invalidação real do token)
    ---
    tags:
      - Autenticação
    security:
      - Bearer: []
    responses:
      200:
        description: Logout realizado com sucesso
      401:
        description: Credenciais inválidas
    """

    # Se importar TokenBlacklist no topo, um loop pode ser gerado.
    #
    # "auth_routes.py" importa "token_required" de "decorators.py"
    # "decorators.py" importa "TokenBlacklist"
    # "TokenBlacklist" importa "db" de "database.py"
    from models.token_blacklist import TokenBlacklist

    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(" ")[1]
        
        # Decodifica apenas para pegar o jti
        data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        jti = data.get('jti')

        if jti:
            blacklist_entry = TokenBlacklist(
                jti=jti,
                user_id=current_user.id
            )
            db.session.add(blacklist_entry)
            db.session.commit()

        return jsonify({"message": "Logout realizado com sucesso!"}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"message": "Erro ao realizar logout"}), 500