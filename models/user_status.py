from database import db

class UserStatus(db.Model):
    __tablename__ = 'user_status'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(256), nullable=False)

    # Definir o modelo como string evita erro de importação circular

    # Relacionamento One-to-Many: Um status user possui muitos users
    users = db.relationship('User', back_populates='status', lazy=True)