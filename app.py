# --- 1. Bibliotecas de terceiros ---
from flask import Flask
from flasgger import Swagger

# --- 2. Módulos do seu projeto ---
import config
from database import db, inicializar_banco
from error_handlers import register_error_handlers
from routes.auth_routes import auth_bp
from routes.basic_routes import basic_bp
from routes.user_routes import user_bp
from routes.blog_routes import blog_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # Inicializa o banco de dados
    db.init_app(app)
    
    # O Flasgger vai escanear todos os blueprints registrados automaticamente
    # e montar a documentação com base nas docstrings que você escrever
    Swagger(app)

    # Registro centralizado de erros
    register_error_handlers(app)

    # Registro do blueprint de rotas básicas
    app.register_blueprint(basic_bp)

    # Registro do blueprint de autenticação
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Registro do blueprint de usuário
    app.register_blueprint(user_bp, url_prefix='/user')

    # Registro do blueprint de blogs
    app.register_blueprint(blog_bp, url_prefix='/blogs')

    # Inicializa a criação das tabelas se o arquivo .db não existir
    with app.app_context():
        inicializar_banco(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)