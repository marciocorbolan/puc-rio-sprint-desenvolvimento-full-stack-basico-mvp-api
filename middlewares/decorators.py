# --- Bibliotecas de Terceiros ---
from functools import wraps
from flask import request, jsonify
import jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Módulos do Projeto ---
from config import SECRET_KEY
from database import db
from models.user import User
from models.token_blacklist import TokenBlacklist


# ====================== RATE LIMITER ======================
# Configuração global do Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,      # Usa o IP do cliente
    default_limits=["1000 per day"]    # Limite padrão para todas as rotas
)

# Rate Limit específico e mais restrito para a rota de Login
# Proteção contra brute force
login_limiter = limiter.limit("5 per minute", methods=["POST"])
# ========================================================


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'message': 'Token é obrigatório!'}), 401
        
        try:
            # Dividimos o cabeçalho para validar o formato "Bearer <token>"
            partes = auth_header.split(" ")
            
            # Verifica se temos exatamente duas partes e se a primeira é "Bearer"
            if len(partes) != 2 or partes[0] != "Bearer":
                return jsonify({'message': 'Formato de token inválido. Use "Bearer <token>"'}), 401
            
            # Decodifica o token
            token = partes[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            jti = data.get('jti')
            user_id = data['user_id']
            token_type = data.get('token_type', 'access')

            # Verifica o tipo do token
            if token_type == 'refresh':
                return jsonify({'message': 'Use refresh token apenas na rota /auth/refresh'}), 401

            # jti é obrigatório
            if not jti:
                return jsonify({'message': 'Token inválido (jti ausente)'}), 401

            # Proteção contra Token Reuse + Blacklist
            blacklist_entry = TokenBlacklist.query.filter_by(jti=jti).first()
            if blacklist_entry:
                if blacklist_entry.used:
                    return jsonify({'message': 'Token já foi utilizado (replay attack detectado)'}), 401
                
                blacklist_entry.used = True
                db.session.commit()

            # Carrega o usuário do banco
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({'message': 'Usuário não encontrado!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        except Exception:
            return jsonify({'message': 'Erro ao processar token'}), 401
            
        # Passa o usuário atual para a rota
        return f(current_user, *args, **kwargs)

    return decorated


#########################################################################

def refresh_token_required(f):
    """Decorator específico para rotas de refresh token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'message': 'Refresh token é obrigatório!'}), 401
        
        try:
            # Dividimos o cabeçalho para validar o formato "Bearer <token>"
            partes = auth_header.split(" ")

            # Verifica se temos exatamente duas partes e se a primeira é "Bearer"
            if len(partes) != 2 or partes[0] != "Bearer":
                return jsonify({'message': 'Formato de refresh token inválido. Use "Bearer <token>"'}), 401

            # Decodifica o token
            token = partes[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            jti = data.get('jti')
            user_id = data['user_id']
            token_type = data.get('token_type')

            # Verifica o tipo do token
            if token_type != 'refresh':
                return jsonify({'message': 'Token não é um refresh token válido'}), 401

            # jti é obrigatório
            if not jti:
                return jsonify({'message': 'Refresh token inválido (jti ausente)'}), 401

            # Proteção contra Token Reuse + Blacklist
            blacklist_entry = TokenBlacklist.query.filter_by(jti=jti).first()
            if blacklist_entry:
                if blacklist_entry.used:
                    return jsonify({'message': 'Refresh token já foi utilizado'}), 401
                blacklist_entry.used = True
                db.session.commit()

            # Carrega o usuário do banco
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({'message': 'Usuário não encontrado!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Refresh token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Refresh token inválido!'}), 401
        except Exception:
            return jsonify({'message': 'Erro ao processar refresh token'}), 401
            
        # Passa o usuário atual para a rota
        return f(current_user, *args, **kwargs)

    return decorated