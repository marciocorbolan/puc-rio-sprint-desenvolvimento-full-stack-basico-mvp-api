from functools import wraps
from flask import request, jsonify
import jwt
from config import SECRET_KEY

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
            
            token = partes[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
            
        return f(*args, **kwargs)
    return decorated