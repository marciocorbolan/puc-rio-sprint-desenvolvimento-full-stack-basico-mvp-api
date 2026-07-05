# --- Bibliotecas de Terceiros ---
from functools import wraps
from flask import request, jsonify
import jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Módulos do Projeto ---
from config import SECRET_KEY
from models.user import User


# ====================== RATE LIMITER ======================
# Configuração global do Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,      # Usa o IP do cliente
    default_limits=["100 per day"]    # Limite padrão para todas as rotas
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
            user_id = data['user_id']

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