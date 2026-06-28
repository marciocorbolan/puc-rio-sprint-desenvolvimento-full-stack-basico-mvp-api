from database import db

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cpfcnpj = db.Column(db.String(14), nullable=False)
    nome = db.Column(db.String(256), nullable=False)
    data_nasc = db.Column(db.String(10))
    email = db.Column(db.String(256), nullable=False)
    senha = db.Column(db.String(256), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('user_status.id'), nullable=False)

    # Relacionamento Many-to-One: Muitos usuários para um status
    # 'UserStatus' como string evita erro de importação circular
    status = db.relationship('UserStatus', backref='users')