# --- Bibliotecas de Terceiros ---
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def inicializar_banco(app):
    """Registra todos os modelos ANTES de criar as tabelas"""
    
    with app.app_context():
        # IMPORTAÇÕES PRIMEIRO (para registrar os modelos no SQLAlchemy)
        from models.user_status import UserStatus
        from models.user import User
        from models.blog import Blog
        from models.post import Post
        from models.comment import Comment
        from models.token_blacklist import TokenBlacklist

        # Pega o caminho do banco diretamente da configuração do app
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

        if not os.path.exists(db_path):
            print(f"Banco não encontrado. Criando em: {db_path}...")
            db.create_all()
        else:
            # O db.create_all() ira criar novas tabelas, mas nuca irá atualizalas
            # Se precisar atualizar o banco, você pode deletar o arquivo .db e reiniciar a aplicação

            db.create_all()
            print(f"Banco de dados encontrado: {db_path}")


    print("Banco criado/atualizado com sucesso!")