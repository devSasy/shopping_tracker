import mysql.connector
from mysql.connector import pooling
from config import Config

db_pool = None

def init_db_pool():
    """
    Inizializza il pool di connessioni MySQL solo se non è già stato creato.
    Questo pattern evita di aprire nuove connessioni ad ogni richiesta, riducendo il carico sul database e velocizzando le operazioni.
    """
    global db_pool
    
    if db_pool is None:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="shopping_tracker_pool",
            pool_size=5, 
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            database=Config.DB_NAME
        )
    
    return db_pool

def get_connection():
    """
    Restituisce una connessione dal pool.
    Se il pool non è ancora stato inizializzato, lo crea automaticamente.
    """
    if db_pool is None:
        init_db_pool()
    
    return db_pool.get_connection()

def execute_query(query, params=None, fetch=False, commit=False):
    """
    Esegue una query SQL parametrizzata in modo sicuro e gestisce automaticamente le transazioni.
    Argomenti:
        query (str): Query SQL da eseguire.
        params (tuple, opzionale): Parametri da passare alla query per evitare SQL injection.
        fetch (bool): Se True, restituisce i risultati della query (per SELECT).
        commit (bool): Se True, effettua il commit della transazione (per INSERT/UPDATE/DELETE).
    Ritorna:
        list o int: Risultati della query (lista di dizionari) o ID dell'ultima riga inserita.
    """
    conn = None
    cursor = None
    result = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
        
        if commit:
            conn.commit()
            if cursor.lastrowid:
                result = cursor.lastrowid
        
        return result
    
    except Exception as e:
        if conn and commit:
            conn.rollback()  
        raise e
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()