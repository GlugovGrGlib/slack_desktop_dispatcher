import gino
from settings import get_config

db = gino.Gino()
config = get_config()

drivername = config['database']['db_driver']
database = config['database']['database']
username = config['database']['user']
password = config['database']['password']
host = config['database']['host']
port = config['database']['port']


class Desktop(db.Model):
    __tablename__ = 'desktop'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, default=None)
    name = db.Column(db.String, unique=True)
    occupied = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, server_default='now()')


async def get_bind():
    await db.set_bind(f'{drivername}://{username}:{password}@{host}:{port}/{database}')
    await db.gino.create_all()
