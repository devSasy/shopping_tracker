import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    
    # Connessione database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASS = os.environ.get('DB_PASS', '')
    DB_NAME = os.environ.get('DB_NAME', 'shopping_tracker')
    
    # Directory dove vengono salvati eventuali file CSV esportati o di backup.
    CSV_DIR = os.environ.get('CSV_DIR', 'data')
    
    @classmethod
    def init_app(cls):
        # Pattern utile in fase di scrittura/lettura file per assicurarsi che la dir per i CSV esista.
        if not os.path.exists(cls.CSV_DIR):
            os.makedirs(cls.CSV_DIR)