from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models import User

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Accesso richiesto. Effettua il login per continuare.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route per la registrazione di un nuovo utente.
    Gestisce sia la visualizzazione del form che la logica di validazione e salvataggio dei dati.
    La password viene sempre salvata in modo sicuro (hashata) e non in chiaro.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        error = None
        if not username:
            error = 'Username è obbligatorio.'
        elif not password:
            error = 'Password è obbligatoria.'
        elif password != confirm_password:
            error = 'Le password non corrispondono.'
        elif User.get_by_username(username):
            error = f'Username {username} è già registrato.'
        
        if error is None:
            # Creazione e salvataggio del nuovo utente.
            # La password viene cifrata tramite hash per motivi di sicurezza.
            user = User(
                username=username,
                password_hash=User.hash_password(password)
            )
            user.save()
            
            flash('Registrazione completata con successo! Ora puoi effettuare il login.', 'success')
            return redirect(url_for('auth.login'))
        
        flash(error, 'danger')
    
    # il template login.html viene riutilizzato anche per la registrazione, variando solo la logica lato server.
    return render_template('login.html', register=True)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route per il login utente.
    Gestisce la verifica delle credenziali e l'impostazione della sessione Flask.
    Se il login ha successo, l'utente viene reindirizzato alla pagina desiderata o alla dashboard principale.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        error = None
        if not username:
            error = 'Username è obbligatorio.'
        elif not password:
            error = 'Password è obbligatoria.'
        
        if error is None:
            user = User.get_by_username(username)
            
            if user and user.verify_password(password):
                session.clear()
                session['user_id'] = user.id
                session['username'] = user.username
                
                # Se l'utente aveva richiesto una pagina protetta, viene reindirizzato lì dopo il login.
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('spese.index'))
            
            error = 'Username o password non validi.'
        
        flash(error, 'danger')
    
    return render_template('login.html', register=False)

@auth_bp.route('/logout')
def logout():
    """
    Route per il logout dell'utente.
    Cancella la sessione e mostra un messaggio di conferma.
    """
    session.clear()
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.before_app_request
def load_logged_in_user():
    """
    Funzione eseguita prima di ogni richiesta.
    Serve a caricare i dati dell'utente loggato (se presente) e a renderli disponibili durante la richiesta.
    Questo pattern è utile per accedere facilmente alle informazioni dell'utente corrente in tutto il ciclo di vita della richiesta.
    """
    user_id = session.get('user_id')
    
    if user_id is None:
        request.current_user = None
    else:
        request.current_user = User.get_by_id(user_id)