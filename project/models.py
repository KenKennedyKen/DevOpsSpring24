from project.app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # relationship to fetch the user who posted
    user = db.relationship('User', backref='posts')
    # new column for the timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # tags
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery',
        backref=db.backref('posts', lazy=True))

    def __init__(self, title, text, user_id, image_filename=None, **kwargs):
        self.title = title
        self.text = text
        self.user_id = user_id
        self.image_filename = image_filename
        super(Post, self).__init__(**kwargs)

    def __repr__(self):
        return f"<title {self.title}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self,name):
        self.name = name

    def __repr__(self):
        return f"<Tag {self.name}>"
    
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vote_type = db.Column(db.String(10)) # 'up' or 'down'
    # Relationships
    post = db.relationship('Post', backref='votes')
    user = db.relationship('User', backref='votes')
    