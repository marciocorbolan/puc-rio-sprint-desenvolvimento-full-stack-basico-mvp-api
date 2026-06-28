import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def inicializar_banco(app):
    # Pega o caminho do banco diretamente da configuração do app
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    if not os.path.exists(db_path):
        print(f"Banco não encontrado. Criando em: {db_path}...")
    else:
        print(f"Banco de dados encontrado: {db_path}")

    # Importação local para evitar importação circular
    from models.user import User
    from models.user_status import UserStatus
    from models.blog import Blog
    from models.post import Post
    from models.comment import Comment

    # O correto é utilizar migrations para atualizar o banco de dados, mas para fins de simplicidade, vamos apenas criar as tabelas se não existirem.
    with app.app_context():
        db.create_all()

    print("Banco criado/atualizado com sucesso!")