# --- Bibliotecas de Terceiros ---
from flask import Blueprint, request, jsonify
import jwt
import datetime
import uuid
from werkzeug.security import check_password_hash, generate_password_hash

# --- Módulos do Projeto ---
import config
from database import db
from models.user import User
from models.token_blacklist import TokenBlacklist
from middlewares.decorators import login_limiter, token_required, refresh_token_required


auth_bp = Blueprint('auth', __name__)


#########################################################################

def generate_access_token(user):
    """Gera token de acesso (curto prazo)"""
    expiration = datetime.datetime.now(datetime.timezone.utc) + \
                 datetime.timedelta(hours=config.JWT_EXPIRATION_HOURS)
    jti = str(uuid.uuid4())
    
    token = jwt.encode({
        'user_id': user.id,
        'cpfcnpj': user.cpfcnpj,
        'email': user.email,
        'nome': user.nome,
        'jti': jti,
        'token_type': 'access',
        'exp': expiration
    }, config.SECRET_KEY, algorithm="HS256")

    return token, jti, expiration


#########################################################################

def generate_refresh_token(user):
    """Gera token de refresh (longo prazo)"""
    expiration = datetime.datetime.now(datetime.timezone.utc) + \
                 datetime.timedelta(days=config.JWT_REFRESH_EXPIRATION_DAYS)
    
    jti = str(uuid.uuid4())
    
    token = jwt.encode({
        'user_id': user.id,
        'jti': jti,
        'token_type': 'refresh',
        'exp': expiration
    }, config.SECRET_KEY, algorithm="HS256")
    
    return token, jti, expiration


#########################################################################


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Cadastra um novo usuário no sistema
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
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
              description: CPF ou CNPJ (obrigatório e único)
            nome:
              type: string
              description: Nome completo do usuário
            email:
              type: string
              description: Endereço de email válido (único)
            senha:
              type: string
              description: Senha para acesso (mín. 6 caracteres)
    responses:
      201:
        description: Cadastro realizado com sucesso
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
    
    agora_utc = datetime.datetime.now(datetime.timezone.utc)
    data_cadastro_atualizacao_formatada = agora_utc.strftime('%Y-%m-%d %H:%M:%S')

    # Criar o objeto usuário
    novo_usuario = User(
        cpfcnpj=cpfcnpj,
        nome=nome,
        email=email,
        senha=generate_password_hash(senha),
        status_id=1,
        data_cadastro=data_cadastro_atualizacao_formatada,
        data_atualizacao=data_cadastro_atualizacao_formatada
    )
    
    db.session.add(novo_usuario)
    db.session.commit()
    
    return jsonify({"message": "Cadastro realizado com sucesso"}), 201


#########################################################################

@auth_bp.route('/login', methods=['POST'])
@login_limiter
def login():
    """
    Realiza login e retorna tokens JWT (Access + Refresh)
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - cpfcnpj
            - senha
          properties:
            cpfcnpj:
              type: string
              description: CPF ou CNPJ cadastrado
            senha:
              type: string
              description: Senha do usuário
    responses:
      200:
        description: Login realizado com sucesso
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: Token de acesso (válido por 24h)
            refresh_token:
              type: string
              description: Token para renovar acesso (válido por 7 dias)
            user_id:
              type: integer
            access_expires_in:
              type: string
            refresh_expires_in:
              type: string
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
    
    # Gera tokens
    access_token, access_jti, access_exp = generate_access_token(user)
    refresh_token, refresh_jti, refresh_exp = generate_refresh_token(user)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': user.id,
        'access_expires_in': f"{config.JWT_EXPIRATION_HOURS} horas",
        'refresh_expires_in': f"{config.JWT_REFRESH_EXPIRATION_DAYS} dias"
    })


#########################################################################

@auth_bp.route('/refresh', methods=['POST'])
@refresh_token_required
def refresh(current_user):
    """
    Renova o Access Token usando Refresh Token (com rotação de token)
    ---
    tags:
      - Autenticação
    security:
      - Bearer: []
    responses:
      200:
        description: Novos tokens gerados com sucesso
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            user_id:
              type: integer
            expires_in:
              type: string
      401:
        description: Credenciais inválidas (refresh token inválido, expirado ou já utilizado)
      500:
        description: Erro interno no servidor (ex.: gerar token)
    """

    try:
        # Gera novo access token
        access_token, access_jti, _ = generate_access_token(current_user)
        
        # Token Rotation: Gera novo refresh token (melhor prática de segurança)
        new_refresh_token, new_refresh_jti, _ = generate_refresh_token(current_user)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'user_id': current_user.id,
            'expires_in': f"{config.JWT_EXPIRATION_HOURS} horas"
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"message": "Erro ao gerar novo token"}), 500


#########################################################################

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Realiza logout invalidando o token atual
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
      500:
        description: Erro interno no servidor (ex.: logout)
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
                user_id=current_user.id,
                used=True # Marca como usado
            )
            db.session.add(blacklist_entry)
            db.session.commit()

        return jsonify({"message": "Logout realizado com sucesso!"}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"message": "Erro ao realizar logout"}), 500