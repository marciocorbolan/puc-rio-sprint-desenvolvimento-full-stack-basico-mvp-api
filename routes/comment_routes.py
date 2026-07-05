# --- Bibliotecas de Terceiros ---
from flask import Blueprint, request, jsonify
import jwt
import datetime

# --- Módulos do Projeto ---
from config import SECRET_KEY
from database import db
from models.comment import Comment
from models.post import Post
from middlewares.decorators import token_required
from utils.file_manager import get_image_as_base64, save_image_from_base64
from utils.text_utils import slugify
from utils.validation import validate_base64_image

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/', methods=['GET'])
def list_comments():
    """
    Lista comments com filtros dinâmicos
    ---
    tags:
      - Comment
    parameters:
      - name: user_id
        in: query
        type: integer
      - name: post_id
        in: query
        type: integer
      - name: data_cadastro_inicio
        in: query
        type: string
        description: Formato YYYY-MM-DD HH:MM:SS
      - name: data_cadastro_fim
        in: query
        type: string
        description: Formato YYYY-MM-DD HH:MM:SS
    responses:
      200:
        description: Lista processada com sucesso
      400:
        description: Erro de validação
    """
    query = Comment.query
    
    # Parâmetros de filtro
    user_id = request.args.get('user_id')
    post_id = request.args.get('post_id')
    data_cadastro_inicio = request.args.get('data_cadastro_inicio')
    data_cadastro_fim = request.args.get('data_cadastro_fim')

    # 1. Filtros simples
    if user_id:
        query = query.filter(Comment.user_id == user_id)
    if post_id:
        query = query.filter(Comment.post_id == post_id)

    # 2. Lógica de Range para data_cadastro
    if data_cadastro_inicio and data_cadastro_fim:
        if data_cadastro_inicio > data_cadastro_fim:
            return jsonify({"message": "data_cadastro_inicio deve ser menor que data_cadastro_fim"}), 400
        query = query.filter(Comment.data_cadastro.between(data_cadastro_inicio, data_cadastro_fim))
    elif data_cadastro_inicio:
        query = query.filter(Comment.data_cadastro == data_cadastro_inicio)
    elif data_cadastro_fim:
        query = query.filter(Comment.data_cadastro == data_cadastro_fim)

    comments = query.all()
    
    return jsonify([{
        "id": c.id,
        "user_id": c.user_id,
        "post_id": c.post_id,
        "texto": c.texto,
        "data_cadastro": c.data_cadastro
    } for c in comments]), 200

#########################################################################

@comment_bp.route('/', methods=['POST'])
@token_required
def create_comment():
    """
    Cria um novo comment para o usuário logado
    ---
    tags:
      - Comment
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - post_id
            - texto
          properties:
            post_id:
              type: integer
              description: ID do post (obrigatório)
            texto:
              type: string
              description: Texto (obrigatório)
            imagem:
              type: string
              description: Imagem em Base64 (opcional)
    responses:
      201:
        description: Cadastro criado com sucesso
      400:
        description: Erro de validação
      401:
        description: Credenciais inválidas
      404:
        description: Cadastro não encontrado
    """
    token = request.headers.get('Authorization').split(" ")[1]
    data_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    data = request.get_json()

    if not data.get('post_id'):
        return jsonify({"message": "post_id é obrigatório"}), 400
    
    # Verifica se o blog existe e pertence ao usuário
    post = Post.query.get(data['post_id'])
    if not post:
        return jsonify({"message": "Post não encontrado"}), 404

    if not data.get('texto'):
        return jsonify({"message": "Texto é obrigatório"}), 400
    texto = data.get('texto')

    agora_utc = datetime.datetime.now(datetime.timezone.utc)
    data_cadastro_atualizacao_formatada = agora_utc.strftime('%Y-%m-%d %H:%M:%S')

    comment = Comment(
        user_id=data_token['user_id'],
        post_id=post.id,
        texto=texto,
        data_cadastro=data_cadastro_atualizacao_formatada,
    )
    
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Cadastro realizado com sucesso", "id": comment.id}), 201