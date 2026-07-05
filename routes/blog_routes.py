# --- Bibliotecas de Terceiros ---
import os
from flask import Blueprint, request, jsonify
import datetime

# --- Módulos do Projeto ---
from database import db
from models.blog import Blog
from models.post import Post
from middlewares.decorators import token_required
from utils.file_manager import get_image_as_base64, save_image_from_base64
from utils.validation import validate_base64_image


blog_bp = Blueprint('blog', __name__)


#########################################################################


@blog_bp.route('/', methods=['GET'])
def list_blogs():
    """
    Lista os blogs cadastrados (Suporte a filtros)
    ---
    tags:
      - Blog
    parameters:
      - name: user_id
        in: query
        type: integer
        description: Filtrar por ID do dono
      - name: nome
        in: query
        type: string
        description: Busca por nome (parcial)
      - name: data_cadastro_inicio
        in: query
        type: string
        description: Data inicial (YYYY-MM-DD HH:MM:SS)
      - name: data_cadastro_fim
        in: query
        type: string
        description: Data final (YYYY-MM-DD HH:MM:SS)
      - name: com_posts
        in: query
        type: boolean
        description: Retornar apenas blogs que possuem posts
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
              nome:
                type: string
              image:
                type: string
              data_cadastro:
                type: string
              data_atualizacao:
                type: string
      400:
        description: Parâmetros inválidos
    """

    query = Blog.query
    
    # Parâmetros de filtro
    user_id = request.args.get('user_id')
    nome = request.args.get('nome')
    data_cadastro_inicio = request.args.get('data_cadastro_inicio')
    data_cadastro_fim = request.args.get('data_cadastro_fim')
    com_posts = request.args.get('com_posts', 'false').lower() == 'true'

    # Filtros simples
    if user_id:
        query = query.filter(Blog.user_id == user_id)
    if nome:
        query = query.filter(Blog.nome.ilike(f'%{nome}%'))

    # Lógica de Range para data_cadastro
    if data_cadastro_inicio and data_cadastro_fim:
        if data_cadastro_inicio > data_cadastro_fim:
            return jsonify({"message": "data_cadastro_inicio deve ser menor que data_cadastro_fim"}), 400
        query = query.filter(Blog.data_cadastro.between(data_cadastro_inicio, data_cadastro_fim))
    elif data_cadastro_inicio:
        query = query.filter(Blog.data_cadastro == data_cadastro_inicio)
    elif data_cadastro_fim:
        query = query.filter(Blog.data_cadastro == data_cadastro_fim)

    # Filtro de blogs com posts
    if com_posts:
        query = query.join(Post).distinct()

    blogs = query.all()
    
    return jsonify([{
        "id": b.id,
        "user_id": b.user_id,
        "nome": b.nome,
        "image": get_image_as_base64(b.imagem),
        "user_id": b.user_id,
        "data_cadastro": b.data_cadastro,
        "data_atualizacao": b.data_atualizacao
    } for b in blogs]), 200


#########################################################################

@blog_bp.route('/<int:id>', methods=['GET'])
def get_blog(id):
    """
    Retorna detalhes de um blog
    ---
    tags:
      - Blog
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do blog
    responses:
      200:
        description: Dados do cadastro
        schema:
          type: object
          properties:
            id:
              type: integer
            user_id:
              type: integer
            nome:
              type: string
            image:
              type: string
            data_cadastro:
              type: string
      400:
        description: Parâmetros inválidos
      404:
        description: Cadastro não encontrado
    """

    if not id:
        return jsonify({"message": "ID não informado"}), 400

    blog = Blog.query.get(id)
    if not blog:
        return jsonify({"message": "Cadastro não encontrado"}), 404
    
    return jsonify({
        "id": blog.id,
        "user_id": blog.user_id,
        "nome": blog.nome,
        "image": get_image_as_base64(blog.imagem),
        "data_cadastro": blog.data_cadastro,
        "data_atualizacao": blog.data_atualizacao
    }), 200


#########################################################################

@blog_bp.route('/', methods=['POST'])
@token_required
def create_blog(current_user):
    """
    Cria um novo blog para o usuário logado
    ---
    tags:
      - Blog
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
          properties:
            nome:
              type: string
              description: Nome do blog (obrigatório)
            imagem:
              type: string
              description: Imagem no formato Base64 (opcional, tamanho máximo 8MB)
    responses:
      201:
        description: Cadastro realizado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
            id:
              type: integer
      400:
        description: Erro de validação
      403:
        description: Acesso negado
      404:
        description: Cadastro não encontrado
      500:
        description: Erro interno no servidor (imagem)
    """

    data = request.get_json()

    if not data.get('nome'):
        return jsonify({"message": "Nome é obrigatório"}), 400
    nome = data.get('nome')
    
    agora_utc = datetime.datetime.now(datetime.timezone.utc)
    data_cadastro_atualizacao_formatada = agora_utc.strftime('%Y-%m-%d %H:%M:%S')

    blog = Blog(
        user_id=current_user.id,
        nome=nome,
        data_cadastro=data_cadastro_atualizacao_formatada,
        data_atualizacao=data_cadastro_atualizacao_formatada
    )
    
    if data.get('imagem'):
        valido, erro, img_bytes = validate_base64_image(data['imagem'])
        if not valido:
            return jsonify({"message": erro}), 400
        
        # O ID só existe após o commit, então criamos o blog antes
        db.session.add(blog)
        db.session.commit() # Agora teremo o ID
        
        # Salva o arquivo e atualiza o caminho no banco
        caminho_imagem = save_image_from_base64(img_bytes, 'blog', blog.id)
        if not caminho_imagem:
            # Removemos o blog criado se a imagem falhar (transação manual)
            db.session.delete(blog)
            db.session.commit()

            return jsonify({"message": "Erro ao salvar imagem no servidor"}), 500
        else:
            blog.imagem = caminho_imagem
            db.session.commit()
    else:
        db.session.add(blog)
        db.session.commit()

    return jsonify({"message": "Cadastro realizado com sucesso", "id": blog.id}), 201


#########################################################################

@blog_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_blog(current_user, id):
    """
    Atualiza os dados de um blog (apenas o dono)
    ---
    tags:
      - Blog
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
            nome:
              type: string
              description: Nome do blog (opcional)
            imagem:
              type: string
              description: Imagem no formato Base64 (opcional, tamanho máximo 8MB)
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
        description: Erro interno no servidor (imagem)
    """

    if not id:
        return jsonify({"message": "ID não informado"}), 400
    
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({"message": "Cadastro não encontrado"}), 404

    if blog.user_id != current_user.id:
        return jsonify({"message": "Acesso negado: Você não é o dono deste blog"}), 403
    
    agora_utc = datetime.datetime.now(datetime.timezone.utc)
    data_atualizacao_formatada = agora_utc.strftime('%Y-%m-%d %H:%M:%S')

    data = request.get_json()

    if data.get('nome'):
        blog.nome = data['nome']

    if data.get('imagem'):
        valido, erro, img_bytes = validate_base64_image(data['imagem'])
        if not valido:
            return jsonify({"message": erro}), 400
        
        caminho_imagem = save_image_from_base64(img_bytes, 'blog', blog.id)
        if not caminho_imagem:
            return jsonify({"message": "Erro ao salvar imagem no servidor"}), 500
        else:
            blog.imagem = caminho_imagem

    blog.data_atualizacao = data_atualizacao_formatada

    db.session.commit()

    return jsonify({"message": "Cadastro atualizado com sucesso"}), 200


#########################################################################

@blog_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_blog(current_user, id):
    """
    Remove um blog (Apenas se for o dono)
    ---
    tags:
      - Blog
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do cadastro a ser deletado
    responses:
      200:
        description: Cadastro removido com sucesso
      401:
        description: Credenciais inválidas
      403:
        description: Acesso negado
      404:
        description: Cadastro não encontrado
      500:
        description: Erro interno no servidor (imagem)
    """

    if not id:
        return jsonify({"message": "ID não informado"}), 400

    blog = Blog.query.get(id)
    if not blog:
        return jsonify({"message": "Cadastro não encontrado"}), 404

    if blog.user_id != current_user.id:
        return jsonify({"message": "Acesso negado: Você não tem permissão para deletar este blog"}), 403

    if blog.imagem and os.path.exists(blog.imagem):
        try:
            os.remove(blog.imagem)
        except OSError as e:
            print(f"Erro ao deletar arquivo de imagem: {e}")

    try:
        db.session.delete(blog)
        db.session.commit()
        return jsonify({"message": "Cadastro removido com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao remover o cadastro", "error": str(e)}), 500