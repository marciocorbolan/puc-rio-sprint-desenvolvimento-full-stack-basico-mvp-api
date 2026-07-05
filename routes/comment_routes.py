# --- Bibliotecas de Terceiros ---
from flask import Blueprint, request, jsonify
import datetime

# --- Módulos do Projeto ---
from database import db
from models.comment import Comment
from models.post import Post
from middlewares.decorators import token_required


comment_bp = Blueprint('comment', __name__)


#########################################################################


@comment_bp.route('/', methods=['GET'])
def list_comments():
    """
    Lista comentários cadastrados (Suporte a filtros)
    ---
    tags:
      - Comment
    parameters:
      - name: post_id
        in: query
        type: integer
        required: true
        description: Filtrar por ID da postagem (obrigatório)
      - name: data_cadastro_inicio
        in: query
        type: string
        description: Data inicial (YYYY-MM-DD HH:MM:SS)
      - name: data_cadastro_fim
        in: query
        type: string
        description: Data final (YYYY-MM-DD HH:MM:SS)
    responses:
      200:
        description: Lista processada com sucesso
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              user_id:
                type: integer
              user_nome:
                type: string
              blog_id:
                type: integer
              post_id:
                type: integer
              texto:
                type: string
              data_cadastro:
                type: string
      400:
        description: Parâmetros inválidos
    """

    query = Comment.query
    
    # Parâmetros de filtro
    post_id = request.args.get('post_id')
    data_cadastro_inicio = request.args.get('data_cadastro_inicio')
    data_cadastro_fim = request.args.get('data_cadastro_fim')

    if not post_id:
        return jsonify({"message": "post_id é obrigatório"}), 400

    # Filtros simples
    if post_id:
        query = query.filter(Comment.post_id == post_id)

    # Lógica de Range para data_cadastro
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
        "user_nome": c.user.nome,
        "blog_id": c.post.blog_id,
        "post_id": c.post_id,
        "texto": c.texto,
        "data_cadastro": c.data_cadastro
    } for c in comments]), 200


#########################################################################

@comment_bp.route('/', methods=['POST'])
@token_required
def create_comment(current_user):
    """
    Cria um novo comentário vinculada a uma postagem
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
              description: Texto do comentário (obrigatório)
    responses:
      201:
        description: Cadastro realizado com sucesso
      400:
        description: Erro de validação
      401:
        description: Credenciais inválidas
      404:
        description: Cadastro não encontrado
    """

    data = request.get_json()

    if not data.get('post_id'):
        return jsonify({"message": "post_id é obrigatório"}), 400
    
    post = Post.query.get(data['post_id'])
    if not post:
        return jsonify({"message": "Post não encontrado"}), 404

    if not data.get('texto'):
        return jsonify({"message": "Texto é obrigatório"}), 400
    texto = data.get('texto')

    agora_utc = datetime.datetime.now(datetime.timezone.utc)
    data_cadastro_atualizacao_formatada = agora_utc.strftime('%Y-%m-%d %H:%M:%S')

    comment = Comment(
        user_id=current_user.id,
        post_id=post.id,
        texto=texto,
        data_cadastro=data_cadastro_atualizacao_formatada,
    )
    
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Cadastro realizado com sucesso", "id": comment.id}), 201


#########################################################################

@comment_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_comment(current_user, id):
    """
    Remove um comentário (Apenas se for o dono da postagem)
    ---
    tags:
      - Comment
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do comment a ser deletado
    responses:
      200:
        description: Cadastro removido com sucesso
      401:
        description: Credenciais inválidas
      403:
        description: Acesso negado
      404:
        description: Cadastro não encontrado
    """

    if not id:
        return jsonify({"message": "ID não informado"}), 400

    comment = Comment.query.get(id)
    if not comment:
        return jsonify({"message": "Cadastro não encontrado"}), 404

    if comment.post.blog.user_id != current_user.id:
        return jsonify({"message": "Acesso negado: Somente o dono do blog/postagem pode excluir comentários."}), 403

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Cadastro removido com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao remover o cadastro", "error": str(e)}), 500