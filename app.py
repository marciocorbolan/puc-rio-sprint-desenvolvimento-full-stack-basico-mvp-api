from flask import Flask
from flasgger import Swagger
import config
from database import db, inicializar_banco
from error_handlers import register_error_handlers
from routes.basic_routes import basic_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # Inicializa o banco de dados
    db.init_app(app)
    
    # O Flasgger vai escanear todos os blueprints registrados automaticamente
    # e montar a documentação com base nas docstrings que você escrever
    Swagger(app)

    # Registro dos Blueprints
    app.register_blueprint(basic_bp)

    # Registro centralizado de erros
    register_error_handlers(app)

    # Inicializa a criação das tabelas se o arquivo .db não existir
    with app.app_context():
        inicializar_banco(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)