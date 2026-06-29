from database import db

class Blog(db.Model):
    __tablename__ = 'blog'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nome = db.Column(db.String(256), nullable=False)
    imagem = db.Column(db.String(256))
    data_cadastro = db.Column(db.String(19))
    data_atualizacao = db.Column(db.String(19))

    # Definir o modelo como string evita erro de importação circular

    # Relacionamento Many-to-One: Muitos blogs pertencem a um usuário
    user = db.relationship('User', back_populates='blogs')

    # Relacionamento One-to-Many: Um blog possui muitos posts
    posts = db.relationship('Post', back_populates='blog', lazy=True)