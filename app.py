from flask import Flask
import config
from database import db, inicializar_banco

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # Inicializa o banco de dados
    db.init_app(app)

    # Inicializa a criação das tabelas se o arquivo .db não existir
    with app.app_context():
        inicializar_banco(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)