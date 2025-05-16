from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from datetime import datetime
# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    # Setting password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Check if password matches the other password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Game model
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rawg_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(250))
    platform = db.Column(db.String(100))
    release_date = db.Column(db.String(20))
    reviews = db.relationship('Review', backref='game', lazy=True)

    def __repr__(self):
        return f'<Game {self.title}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    
    user = db.relationship('User', backref='reviews')

# User loader for login manager
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
