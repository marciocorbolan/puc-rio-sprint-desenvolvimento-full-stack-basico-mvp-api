# --- Bibliotecas de Terceiros ---
from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Módulos do Projeto ---
import config
from database import db, inicializar_banco
from error_handlers import register_error_handlers
from routes.auth_routes import auth_bp
from routes.basic_routes import basic_bp
from routes.user_routes import user_bp
from routes.blog_routes import blog_bp
from routes.post_routes import post_bp
from routes.comment_routes import comment_bp
from middlewares.decorators import limiter


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # Permite que um index.html local acesse a API em qualquer porta
    CORS(app)

    # Inicializa o banco de dados
    db.init_app(app)

    # Controlar o número de requisições por IP e evitar ataques de brute force (principalmente no login)
    limiter.init_app(app)
    
    # O Flasgger vai escanear todos os blueprints registrados automaticamente
    swagger_template = {
        "swagger": "2.0",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Insira o token JWT no formato: Bearer <seu_token>"
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }
    Swagger(app, template=swagger_template)

    # Registro centralizado de erros
    register_error_handlers(app)

    # Registro dos Blueprints
    app.register_blueprint(basic_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(blog_bp, url_prefix='/blogs')
    app.register_blueprint(post_bp, url_prefix='/posts')
    app.register_blueprint(comment_bp, url_prefix='/comments')

    # Inicializa a criação das tabelas, se o arquivo .db não existir
    with app.app_context():
        inicializar_banco(app)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)