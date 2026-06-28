from database import db

class UserStatus(db.Model):
    __tablename__ = 'user_status'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(256), nullable=False)
    
    # Relacionamento One-to-Many: Um status para muitos usuários
    users = db.relationship('User', backref='status', lazy=True)