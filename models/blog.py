from database import db

class Blog(db.Model):
    __tablename__ = 'blog'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nome = db.Column(db.String(256), nullable=False)
    imagem = db.Column(db.String(256))
    data_cadastro = db.Column(db.String(19))
    data_atualizacao = db.Column(db.String(19))

    # Relacionamento One-to-Many: Um status para muitos usuários
    # 'User' como string evita erro de importação circular
    user = db.relationship('User', backref='blogs')

    # Relacionamento Many-to-One: Muitos usuários para um status
    # 'Post' como string evita erro de importação circular
    posts = db.relationship('Post', backref='blog', lazy=True)