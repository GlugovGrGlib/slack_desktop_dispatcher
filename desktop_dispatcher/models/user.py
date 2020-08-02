from models import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.Unicode, unique=True, nullable=False)
    name = db.Column(db.Unicode, nullable=False)
