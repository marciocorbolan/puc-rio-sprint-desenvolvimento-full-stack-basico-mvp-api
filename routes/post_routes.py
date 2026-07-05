# --- Bibliotecas de Terceiros ---
import os
from flask import Blueprint, request, jsonify
import jwt
import datetime

# --- Módulos do Projeto ---
from config import SECRET_KEY
from database import db
from models.blog import Blog
from models.post import Post
from models.user import User
from models.comment import Comment
from middlewares.decorators import token_required
from utils.file_manager import get_image_as_base64, save_image_from_base64
from utils.text_utils import slugify
from utils.validation import validate_base64_image

post_bp = Blueprint('post', __name__)

@post_bp.route('/', methods=['GET'])
def list_posts():
    """
    Lista posts com filtros dinâmicos
    ---
    tags:
      - Post
    parameters:
      - name: user_id
        in: query
        type: integer
      - name: blog_id
        in: query
        type: integer
      - name: titulo
        in: query
        type: string
      - name: data_cadastro_inicio
        in: query
        type: string
        description: Formato YYYY-MM-DD HH:MM:SS
      - name: data_cadastro_fim
        in: query
        type: string
        description: Formato YYYY-MM-DD HH:MM:SS
      - name: com_comentarios
        in: query
        type: boolean
    responses:
      200:
        description: Lista processada com sucesso
      400:
        description: Erro de validação
    """

    query = Post.query
    
    # Parâmetros de filtro
    user_id = request.args.get('user_id')
    blog_id = request.args.get('blog_id')
    titulo = request.args.get('titulo')
    data_cadastro_inicio = request.args.get('data_cadastro_inicio')
    data_cadastro_fim = request.args.get('data_cadastro_fim')
    com_comentarios = request.args.get('com_comentarios', 'false').lower() == 'true'

    # Filtros simples
    if user_id:
        query = query.join(Post.user).filter(User.id == user_id)
    if blog_id:
        query = query.filter(Post.blog_id == blog_id)
    if titulo:
        query = query.filter(Post.titulo.ilike(f'%{titulo}%'))

    # Lógica de Range para data_cadastro
    if data_cadastro_inicio and data_cadastro_fim:
        if data_cadastro_inicio > data_cadastro_fim:
            return jsonify({"message": "data_cadastro_data_cadastro_inicio deve ser menor que data_cadastro_fim"}), 400
        query = query.filter(Post.data_cadastro.between(data_cadastro_inicio, data_cadastro_fim))
    elif data_cadastro_inicio:
        query = query.filter(Post.data_cadastro == data_cadastro_inicio)
    elif data_cadastro_fim:
        query = query.filter(Post.data_cadastro == data_cadastro_fim)

    # Filtro de blogs com comentarios
    if com_comentarios:
        query = query.join(Comment).distinct()

    posts = query.all()
    
    return jsonify([{
        "id": p.id,
        "user_id": p.user.id,
        "blog_id": p.blog_id,
        "titulo": p.titulo,
        "conteudo": p.conteudo,
        "slug": slugify(p.titulo),
        "image": get_image_as_base64(p.imagem),
        "data_cadastro": p.data_cadastro,
        "data_atualizacao": p.data_atualizacao
    } for p in posts]), 200

#########################################################################

@post_bp.route('/<int:id>/', methods=['GET'])
@post_bp.route('/<int:id>/<slug>', methods=['GET'])
def get_post(id, slug=None):
    """
    Exibe os detalhes de um post específico por ID
    ---
    tags:
      - Post
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: slug
        in: path
        type: string
        required: false
    responses:
      200:
        description: Cadastro encontrado
      400:
        description: Erro de validação
      404:
        description: Cadastro não encontrado
    """

    if not id:
        return jsonify({"message": "ID não informado"}), 400

    post = Post.query.get(id)
    if not post:
        return jsonify({"message": "Cadastro não encontrado"}), 404

    # Poderia validar o slug aqui, mas para simplificação, vamos apenas retornar os dados do post
        
    return jsonify({
        "id": post.id,
        "user_id": post.user.id,
        "blog_id": post.blog_id,
        "titulo": post.titulo,
        "conteudo": post.conteudo,
        "slug": slugify(post.titulo),
        "image": get_image_as_base64(post.imagem),
        "data_cadastro": post.data_cadastro,
        "data_atualizacao": post.data_atualizacao
    }), 200

#########################################################################

@post_bp.route('/', methods=['POST'])
@token_required
def create_post():
    """
    Cria um novo post vinculado a um blog do usuário logado
    ---
    tags:
      - Post
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - blog_id
            - titulo
          properties:
            blog_id:
              type: integer
              description: ID do blog (obrigatório)
            titulo:
              type: string
              description: título (obrigatório)
            conteudo:
              type: string
              description: Conteúdo do post (obrigatório)
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
      403:
        description: Acesso negado
      500:
        description: Erro interno no servidor
    """

    token = request.headers.get('Authorization').split(" ")[1]
    data_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    data = request.get_json()

    if not data.get('blog_id'):
        return jsonify({"message": "blog_id é obrigatório"}), 400
    
    blog = Blog.query.get(data['blog_id'])
    if not blog or blog.user_id != data_token['user_id']:
        return jsonify({"message": "Acesso negado ou blog inexistente"}), 403

    if not data.get('titulo'):
        return jsonify({"message": "Título é obrigatório"}), 400
    titulo = data.get('titulo')

    if not data.get('conteudo'):
        return jsonify({"message": "Conteúdo é obrigatório"}), 400
    conteudo = data.get('conteudo')
    
    agora_utc = datetime.datetime.now(datetime.timezone.utc)
    data_cadastro_atualizacao_formatada = agora_utc.strftime('%Y-%m-%d %H:%M:%S')

    post = Post(
        blog_id=blog.id,
        titulo=titulo,
        conteudo=conteudo,
        data_cadastro=data_cadastro_atualizacao_formatada,
        data_atualizacao=data_cadastro_atualizacao_formatada
    )
    
    if data.get('imagem'):
        valido, erro, img_bytes = validate_base64_image(data['imagem'])
        if not valido:
            return jsonify({"message": erro}), 400
        
        # O ID só existe após o commit, então criamos o post antes
        db.session.add(post)
        db.session.commit() # Agora teremo o ID
        
        # Salva o arquivo e atualiza o caminho no banco
        caminho_imagem = save_image_from_base64(img_bytes, 'post', post.id)
        if not caminho_imagem:
            # Removemos o post criado se a imagem falhar (transação manual)
            db.session.delete(post)
            db.session.commit()

            return jsonify({"message": "Erro ao salvar imagem no servidor"}), 500
        else:
            post.imagem = caminho_imagem
            db.session.commit()
    else:
        db.session.add(post)
        db.session.commit()

    return jsonify({"message": "Cadastro realizado com sucesso", "id": post.id}), 201

#########################################################################

@post_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_post(id):
    """
    Edita um post existente (Apenas se for o dono)
    ---
    tags:
      - Post
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do cadastro a ser editado
      - in: body
        name: body
        schema:
          type: object
          properties:
            titulo:
              type: string
              description: título (opcional)
            conteudo:
              type: string
              description: Conteúdo do post (opcional)
            imagem:
              type: string
              description: Imagem em Base64 (opcional)
    responses:
      200:
        description: Cadastro atualizado com sucesso
      400:
        description: Erro de validação
      401:
        description: Credenciais inválidas
      403:
        description: Acesso negado
      404:
        description: Cadastro não encontrado
      500:
        description: Erro interno no servidor
    """

    token = request.headers.get('Authorization').split(" ")[1]
    data_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    if not id:
        return jsonify({"message": "ID não informado"}), 400
    
    post = Post.query.get(id)
    if not post:
        return jsonify({"message": "Cadastro não encontrado"}), 404

    if post.blog.user_id != data_token['user_id']:
        return jsonify({"message": "Acesso negado: Você não é o dono deste post"}), 403
    
    agora_utc = datetime.datetime.now(datetime.timezone.utc)
    data_atualizacao_formatada = agora_utc.strftime('%Y-%m-%d %H:%M:%S')

    data = request.get_json()

    if data.get('titulo'):
        post.titulo = data['titulo']

    if data.get('conteudo'):
        post.conteudo = data['conteudo']

    if data.get('imagem'):
        valido, erro, img_bytes = validate_base64_image(data['imagem'])
        if not valido:
            return jsonify({"message": erro}), 400
        
        caminho_imagem = save_image_from_base64(img_bytes, 'post', post.id)
        if not caminho_imagem:
            return jsonify({"message": "Erro ao salvar imagem no servidor"}), 500
        else:
            post.imagem = caminho_imagem

    post.data_atualizacao = data_atualizacao_formatada

    db.session.commit()

    return jsonify({"message": "Cadastro atualizado com sucesso"}), 200

#########################################################################

@post_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_post(id):
    """
    Remove um post existente (Apenas se for o dono)
    ---
    tags:
      - Post
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do post a ser deletado
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

    token = request.headers.get('Authorization').split(" ")[1]
    data_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    if not id:
        return jsonify({"message": "ID não informado"}), 400

    post = Post.query.get(id)
    if not post:
        return jsonify({"message": "Cadastro não encontrado"}), 404

    if post.blog.user_id != data_token['user_id']:
        return jsonify({"message": "Acesso negado: Você não tem permissão para deletar este post"}), 403

    if post.imagem and os.path.exists(post.imagem):
        try:
            os.remove(post.imagem)
        except OSError as e:
            print(f"Erro ao deletar arquivo de imagem: {e}")

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Cadastro removido com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao remover o cadastro", "error": str(e)}), 500