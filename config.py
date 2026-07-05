import os

# ====================== CONFIGURAÇÕES GERAIS ======================
# Define o caminho base do projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Nome do arquivo
DB_NAME = 'puc-rio-sdfsb-mvp.db'

# Configuração do Banco de Dados SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, DB_NAME)

# Configuração necessária para evitar avisos (Flask-SQLAlchemy)
SQLALCHEMY_TRACK_MODIFICATIONS = False
# ==================================================================

# ======================= CONFIGURAÇÕES JWT =======================
# Chave secreta para JWT
SECRET_KEY = 'uma-chave-bem-longa-e-aleatoria-como-exemplo-123456789-!@#$'

# Tempo de expiração do token (em horas)
JWT_EXPIRATION_HOURS = 24
# =================================================================