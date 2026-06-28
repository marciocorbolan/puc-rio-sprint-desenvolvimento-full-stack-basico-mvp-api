# database.py
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def inicializar_banco(app):
    # Pega o caminho do banco diretamente da configuração do app
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    if not os.path.exists(db_path):
        print(f"Banco não encontrado. Criando em: {db_path}...")
        with app.app_context():
            db.create_all()
        print("Banco criado com sucesso!")
    else:
        print("Banco de dados já existente.")