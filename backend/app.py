from flask import Flask, render_template, redirect, url_for
from config import Config
from extensions import db, login_manager, migrate, csrf
from models import User, Event, Resource, Donation, Request, AdminResponse
import os

def create_app(config_class=Config):
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, 'templates')
    static_dir = os.path.join(current_dir, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # csrf.init_app(app) # Enable if CSRF needed globally, but might need template adjustments
    
    # Register Blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp
    from routes.volunteer import volunteer_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(volunteer_bp, url_prefix='/volunteer')
    
    # Root Route
    @app.route('/')
    def index():
        return render_template('index.html')
        
    return app

def setup_database(app):
    """Setup database with sample data"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if we need to create sample data
            if not User.query.filter_by(email='admin@disaster.org').first():
                print("Creating sample data...")
                create_sample_data()
                print("✅ Sample data created successfully!")
            else:
                print("✅ Database already has sample data")
                
        except Exception as e:
            print(f"❌ Error setting up database: {e}")

def create_sample_data():
    # Create users
    admin = User(name='Admin User', email='admin@disaster.org', phone='+1234567890', is_admin=True)
    admin.set_password('password123')
    
    user1 = User(name='John Doe', email='john@example.com', phone='+1234567891')
    user1.set_password('password123')
    
    user2 = User(name='Jane Smith', email='jane@example.com', phone='+1234567892')
    user2.set_password('password123')
    
    # Create events
    event1 = Event(
        name='Hurricane Relief - Florida',
        description='Major hurricane causing widespread damage and flooding.',
        latitude=27.6648, longitude=-81.5158, severity='High'
    )
    
    event2 = Event(
        name='Earthquake Response - California',
        description='7.2 magnitude earthquake affecting urban areas.',
        latitude=36.7783, longitude=-119.4179, severity='Critical'
    )
    
    # Create resources
    resources = [
        Resource(name='Bottled Water', category='Food', description='Clean drinking water', total_quantity=1000, available_quantity=850, unit='bottles'),
        Resource(name='Emergency Blankets', category='Shelter', description='Thermal blankets', total_quantity=500, available_quantity=500, unit='units'),
        Resource(name='First Aid Kits', category='Medical', description='Basic medical supplies', total_quantity=200, available_quantity=180, unit='kits'),
        Resource(name='Canned Food', category='Food', description='Non-perishable food', total_quantity=800, available_quantity=750, unit='cans'),
        Resource(name='Tents', category='Shelter', description='Emergency shelters', total_quantity=100, available_quantity=95, unit='units'),
    ]
    
    db.session.add_all([admin, user1, user2, event1, event2] + resources)
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    setup_database(app)
    print("🚀 Server starting on http://localhost:5001")
    print("📧 Demo accounts: admin@disaster.org (password123), john@example.com (password123)")
    app.run(debug=True, host='0.0.0.0', port=5001)