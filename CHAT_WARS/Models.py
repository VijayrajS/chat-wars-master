from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table

db = SQLAlchemy()

# Player Table
class Castles(db.Model):
    __tablename__='castles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100))
    players = db.relationship('Player',backref='castle',lazy='dynamic')
    
    
class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state = db.Column(db.String(20), default='DEFEND')
    username = db.Column(db.String(100),unique=True, nullable=False)
    password = db.Column(db.String)
    email = db.Column(db.String(100), unique=True,
                      nullable=False)
    castle_id = db.Column(db.Integer,db.ForeignKey('castles.id'))
    exp = db.Column(db.Integer, nullable=False, default=0)
    level = db.Column(db.Integer, nullable=False, default=1)
    attack = db.Column(db.Integer, nullable=False, default=0)
    defense = db.Column(db.Integer, nullable=False, default=0)
    gold = db.Column(db.Integer, nullable=False, default=0)
    sword = db.Column(db.Integer, nullable=False, default=1)
    sheild = db.Column(db.Integer, nullable=False, default=1)
    


class Quests(db.Model):
    __tablename__ = 'quests-table'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(200), nullable=False)
    gold = db.Column(db.Integer, nullable=False, default=0)
    exp = db.Column(db.Integer, nullable=False, default=0)

