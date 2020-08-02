from models import db


class Desktop(db.Model):
    __tablename__ = 'desktop'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(None, db.ForeignKey('users.id'))
    name = db.Column(db.String, unique=True)
    occupied = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, server_default='now()')
