from config import db

class Channel(db.Model):
    __tablename__ = 'channels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    emotes = db.relationship('Emote', backref='channel', lazy=True, cascade='all, delete-orphan')

class Emote(db.Model):
    __tablename__ = 'emotes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    count = db.Column(db.Integer, default=0)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
