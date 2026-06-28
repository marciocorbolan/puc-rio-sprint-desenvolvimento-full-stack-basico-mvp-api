import os

# Define o caminho base do projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Nome do arquivo
DB_NAME = 'blog.db'

# Configuração do Banco de Dados SQLite
# O arquivo será criado na raiz do projeto
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, DB_NAME)

# Configuração necessária para evitar avisos do Flask-SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Chave secreta para JWT
SECRET_KEY = 'uma-chave-bem-longa-e-aleatoria-como-exemplo-123456789-!@#$'