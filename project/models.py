from project.app import db
from werkzeug.security import generate_password_hash, check_password_hash


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)

    def __init__(self, title, text, image_filename=None, **kwargs):
        self.title = title
        self.text = text
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