from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import sequence

#TODO all id's have a fixed length, don't just put random lengths

class Artist(db.Model):
    artist_id = db.Column(db.String(100), primary_key=True)
    artist = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.spotify_user_id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    spotify_user_id = db.Column(db.String(10000),unique=True)
    artist = db.relationship('Artist')
    Albums = db.relationship('Albums')


class Albums(db.Model):
    album_id = db.Column(db.String(100),primary_key=True)
    album = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    artist_id = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    album_cover_link = db.Column(db.String(50))
    album_rating = db.Column(db.Integer)
    spotify_user_id = db.Column(db.String(10000), db.ForeignKey('user.spotify_user_id'),primary_key=True)
    popularity = db.Column(db.Integer)