from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'routes.login'

# Initialize models (after db but before routes)
from app import models

# Register the blueprint for routes
from app.routes import routes
app.register_blueprint(routes)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
