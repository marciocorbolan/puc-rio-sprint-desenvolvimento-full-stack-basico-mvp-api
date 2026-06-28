from database import db

class Post(db.Model):
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    data_cadastro = db.Column(db.String(19))
    data_atualizacao = db.Column(db.String(19))

    # Relacionamento Many-to-One: Muitos usuários para um status
    # 'Comment' como string evita erro de importação circular
    comments = db.relationship('Comment', backref='post', lazy=True)