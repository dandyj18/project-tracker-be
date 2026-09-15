import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-project-tracker-secret-key-2026')
    
    # DB configuration supporting DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, DB_DIALECT, DB_PORT
    DB_DIALECT = os.environ.get('DB_DIALECT', os.environ.get('POSTGRES_DIALECT', 'postgresql'))
    # Normalize dialect string for SQLAlchemy
    if DB_DIALECT == 'postgres':
        DB_DIALECT = 'postgresql'

    DB_USERNAME = os.environ.get('DB_USERNAME', os.environ.get('POSTGRES_USER', 'postgres'))
    DB_PASSWORD = os.environ.get('DB_PASSWORD', os.environ.get('POSTGRES_PASSWORD', '123456'))
    DB_HOST = os.environ.get('DB_HOST', os.environ.get('POSTGRES_HOST', '127.0.0.1'))
    DB_PORT = os.environ.get('DB_PORT', os.environ.get('POSTGRES_PORT', '5432'))
    DB_NAME = os.environ.get('DB_NAME', os.environ.get('POSTGRES_DB', 'project_tracker'))
    
    DEFAULT_DB_URL = f'{DB_DIALECT}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    DATABASE_URI = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)
    
    # Fallback SQLite path if PostgreSQL server is down
    SQLITE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'project_tracker.db')}"
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
