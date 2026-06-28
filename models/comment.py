from database import db

class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    data_cadastro = db.Column(db.String(19))

    # Relacionamento One-to-Many: Um status para muitos usuários
    # 'User' como string evita erro de importação circular
    user = db.relationship('User', backref='comments')