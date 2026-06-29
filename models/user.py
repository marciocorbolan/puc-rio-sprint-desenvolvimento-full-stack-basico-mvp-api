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

    # Definir o modelo como string evita erro de importação circular

    # Relacionamento Many-to-One: Muitos users pertencem a um status user
    status = db.relationship('UserStatus', back_populates='users')

    # Relacionamento One-to-Many: Um usuário possui muitos blogs
    blogs = db.relationship('Blog', back_populates='user', lazy=True)

    # Relacionamento One-to-Many: Um usuário possui muitos comentários
    comments = db.relationship('Comment', back_populates='user', lazy=True)