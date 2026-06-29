from database import db

class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data_cadastro = db.Column(db.String(19))

    # Definir o modelo como string evita erro de importação circular

    # Relacionamento Many-to-One: Muitos comentários pertencem a um usuário
    user = db.relationship('User', back_populates='comments')

    # Relacionamento Many-to-One: Muitos comentários pertencem a um post
    post = db.relationship('Post', back_populates='comments')