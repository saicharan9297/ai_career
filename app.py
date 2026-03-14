from flask import Flask, redirect, url_for, flash
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os

# Load .env file first
load_dotenv()

app = Flask(__name__)

# Secret key – MUST be set (production lo .env lo strong random key use cheyyi)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or 'super-secret-key-change-this-2026-random-very-long-string'

# Load config if exists (optional)
try:
    from config import Config
    app.config.from_object(Config)
except ImportError:
    pass

# Import models & routes after app creation
from models.user import db, User
from routes.auth import auth_bp
from routes.roadmap import roadmap_bp
from routes.practice import practice_bp
from routes.main import main_bp
from routes.quiz import quiz_bp  # ← Add this import

# Initialize DB
db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

# Register all blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(roadmap_bp, url_prefix='/roadmap')
app.register_blueprint(practice_bp, url_prefix='/practice')
app.register_blueprint(quiz_bp, url_prefix='/quiz')  # ← Add this line

# Create DB tables (dev only – production lo Flask-Migrate use cheyyi)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)