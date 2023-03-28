from flask import jsonify, request
from app.models import User, Tweet, Like
from app import db
from sqlalchemy import func
from . import api

# Gibt eine Liste aller Benutzernamen zurück
@api.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.username for user in users])
    

# Gibt die Gesamtzahl der Benutzer und Tweets zurück
@api.route('/stats', methods=['GET'])
def get_stats():
    total_users = db.session.query(User).count()
    total_tweets = db.session.query(Tweet).count()
    return jsonify({'total_users': total_users, 'total_tweets': total_tweets}), 200


