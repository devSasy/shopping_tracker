from flask import Flask, redirect, url_for
from config import Config
from auth import auth_bp, login_required
from spese import spese_bp
import os

def create_app():
    """Crea e configura l'applicazione Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    Config.init_app()
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(spese_bp, url_prefix='/spese')
    
    # Filtro custom per la formattazione dell'importo in valuta 
    @app.template_filter('currency')
    def currency_filter(value):
        if value is None:
            return "€ 0,00"
        return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Route principale: reindirizza alla pagina delle spese
    @app.route('/')
    def index():
        return redirect(url_for('spese.index'))
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)