import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db
from routes.projects import projects_bp
from routes.tasks import tasks_bp

migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    app.config.from_object(Config)

    CORS(app)

    # Database Initialization with PostgreSQL -> SQLite Fallback
    try:
        db.init_app(app)
        with app.app_context():
            # Test DB connection
            db.engine.connect()
            db.create_all()
            print("Successfully connected to primary database.")
    except Exception as e:
        print(f"Primary DB connection failed: {e}. Falling back to SQLite...")
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLITE_URI
        db.init_app(app)
        with app.app_context():
            db.create_all()
            print("Successfully initialized SQLite fallback database.")

    # Initialize Flask-Migrate CLI commands (flask db)
    migrate.init_app(app, db)

    # CLI Command: flask db-seed
    @app.cli.command("db-seed")
    def seed_db():
        """Run database seeders."""
        from seeders import DatabaseSeeder
        DatabaseSeeder.run()


    # Register Blueprints
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'service': 'Project Tracker API'})

    # Serve React SPA in production
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        elif os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return jsonify({'message': 'Project Tracker API is running. Frontend build pending.'})

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
