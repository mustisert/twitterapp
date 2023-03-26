from app import db
from datetime import datetime
from flask_login import UserMixin
from flask import current_app
from app import login_manager
from werkzeug.security import generate_password_hash, check_password_hash


# Define the followers association table
class Follows(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    tweets = db.relationship('Tweet', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    about_me = db.Column(db.String(140))

    followed = db.relationship('Follows', foreign_keys=[Follows.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follows', foreign_keys=[Follows.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')


    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def followed_tweets(self):
        followed = Tweet.query.join(Follows, Follows.followed_id == Tweet.user_id).filter(Follows.follower_id == self.id)
        own = Tweet.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Tweet.timestamp.desc())
    
    def like_tweet(self, tweet):
        if not self.has_liked_tweet(tweet):
            like = Like(user_id=self.id, tweet_id=tweet.id)
            db.session.add(like)

    def unlike_tweet(self, tweet):
        like = Like.query.filter_by(user_id=self.id, tweet_id=tweet.id).first()
        if like:
            db.session.delete(like)

    def has_liked_tweet(self, tweet):
        return Like.query.filter(Like.user_id == self.id, Like.tweet_id == tweet.id).count() > 0
    
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    
    def follow(self, user):
        if not self.is_following(user):
            f = Follows(follower_id=self.id, followed_id=user.id)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)


    
    

# Define the Tweet model
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('Like', backref='tweet', lazy='dynamic')

    def __repr__(self):
        return '<Tweet {}>'.format(self.body)
    
    def is_liked_by(self, user):
        return Like.query.filter_by(user_id=user.id, tweet_id=self.id).first() is not None
    
    @property
    def num_likes(self):
        return self.likes.count()
    
    def is_owned_by(self, user):
        return self.user_id == user.id


# Define the Like model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'))

    def __repr__(self):
        return '<Like {}>'.format(self.id)



# Define the UserLoader callback
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
