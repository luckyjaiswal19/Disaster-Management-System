"""
Extension instances for Flask components.
Centralized extension initialization to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Database instance
db = SQLAlchemy()

# Login manager for user sessions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Database migrations
migrate = Migrate()

# CSRF protection
csrf = CSRFProtect()