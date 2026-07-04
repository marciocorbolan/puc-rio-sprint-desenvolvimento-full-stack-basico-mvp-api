from database import db

class Post(db.Model):
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    titulo = db.Column(db.String(256), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    data_cadastro = db.Column(db.String(19))
    data_atualizacao = db.Column(db.String(19))

    # Definir o modelo como string evita erro de importação circular

    # Relacionamento Many-to-One: Muitos posts pertencem a um blog
    blog = db.relationship('Blog', back_populates='posts')

    # Relacionamento One-to-Many: Um post possui muitos comentários
    comments = db.relationship('Comment', back_populates='post', lazy=True)

    # Relacionamento de acesso direto ao User através do Blog
    # viewonly=True garante que ele apenas leia a relação sem tentar alterar o banco
    user = db.relationship(
        'User',
        secondary='blog',
        primaryjoin='Post.blog_id == Blog.id',
        secondaryjoin='Blog.user_id == User.id',
        viewonly=True,
        uselist=False
    )