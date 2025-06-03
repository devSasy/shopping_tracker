import os
import csv
from datetime import datetime
from decimal import Decimal
import bcrypt
from config import Config
from db import execute_query

class User:
    """Modello utente per l'autenticazione"""
    
    def __init__(self, id=None, username=None, password_hash=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
    
    @classmethod
    def from_dict(cls, data):
        """Crea un'istanza User da un dizionario"""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            password_hash=data.get('password_hash')
        )
    
    def to_dict(self):
        """Converte User in dizionario"""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash
        }
    
    @staticmethod
    def hash_password(password):
        """Crea l'hash di una password usando bcrypt (algoritmo robusto contro attacchi di forza bruta)"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password):
        """Verifica una password rispetto all'hash memorizzato"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @classmethod
    def get_by_id(cls, user_id):
        """Recupera un utente tramite ID"""
        query = "SELECT * FROM users WHERE id = %s"
        result = execute_query(query, (user_id,), fetch=True)
        
        if result and len(result) > 0:
            return cls.from_dict(result[0])
        return None
    
    @classmethod
    def get_by_username(cls, username):
        """Recupera un utente tramite username"""
        query = "SELECT * FROM users WHERE username = %s"
        result = execute_query(query, (username,), fetch=True)
        
        if result and len(result) > 0:
            return cls.from_dict(result[0])
        return None
    
    def save(self):
        """Salva l'utente nel database (crea o aggiorna)"""
        if self.id:
            query = """
            UPDATE users 
            SET username = %s, password_hash = %s
            WHERE id = %s
            """
            execute_query(query, (self.username, self.password_hash, self.id), commit=True)
            return self.id
        else:
            query = """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            """
            self.id = execute_query(query, (self.username, self.password_hash), commit=True)
            return self.id


class Spesa:
    """Modello Spesa"""
    
    def __init__(self, id=None, user_id=None, data=None, categoria=None, descrizione=None, importo=None):
        self.id = id
        self.user_id = user_id
        
        # Conversione della data
        if isinstance(data, str):
            try:
                self.data = datetime.strptime(data, "%Y-%m-%d").date()
            except ValueError:
                self.data = None
        else:
            self.data = data
            
        self.categoria = categoria
        self.descrizione = descrizione
        
        # Conversione decimale
        if isinstance(importo, str):
            try:
                self.importo = Decimal(importo.replace(',', '.'))
            except:
                self.importo = Decimal('0')
        else:
            self.importo = Decimal(str(importo)) if importo is not None else None
    
    @classmethod
    def from_dict(cls, data):
        """Crea una Spesa da un dizionario"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            data=data.get('data'),
            categoria=data.get('categoria'),
            descrizione=data.get('descrizione'),
            importo=data.get('importo')
        )
    
    def to_dict(self):
        """Converte Spesa in dizionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'data': self.data.strftime("%Y-%m-%d") if self.data else None,
            'categoria': self.categoria,
            'descrizione': self.descrizione,
            'importo': float(self.importo) if self.importo else None
        }
    
    def to_csv_dict(self):
        """Converte Spesa in formato dizionario per CSV"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'data': self.data.strftime("%Y-%m-%d") if self.data else None,
            'categoria': self.categoria,
            'descrizione': self.descrizione,
            'importo': str(self.importo) if self.importo else None
        }
    
    @classmethod
    def from_csv_dict(cls, row, user_id=None):
        """Crea una Spesa da una riga CSV"""
        return cls(
            id=int(row.get('id')) if row.get('id') else None,
            user_id=int(row.get('user_id')) if row.get('user_id') else user_id,
            data=row.get('data'),
            categoria=row.get('categoria'),
            descrizione=row.get('descrizione'),
            importo=row.get('importo')
        )
    
    @staticmethod
    def get_csv_path(user_id):
        """Restituisce il percorso del file CSV per uno specifico utente"""
        return os.path.join(Config.CSV_DIR, f"spese_{user_id}.csv")
    
    @classmethod
    def load_from_csv(cls, user_id):
        """Carica le spese da file CSV per uno specifico utente"""
        csv_path = cls.get_csv_path(user_id)
        spese = []
        
        try:
            if os.path.exists(csv_path):
                with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        spese.append(cls.from_csv_dict(row, user_id))
        except Exception as e:
            print(f"Errore caricamento CSV: {e}")
        
        return spese
    
    @classmethod
    def save_to_csv(cls, user_id, spese_list):
        """Salva le spese su file CSV per uno specifico utente"""
        csv_path = cls.get_csv_path(user_id)
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'user_id', 'data', 'categoria', 'descrizione', 'importo']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for spesa in spese_list:
                    writer.writerow(spesa.to_csv_dict())
            return True
        except Exception as e:
            print(f"Errore salvataggio CSV: {e}")
            return False
    
    @classmethod
    def get_by_id(cls, spesa_id, user_id=None):
        """Recupera una spesa tramite ID, opzionalmente filtrando per utente"""
        query = "SELECT * FROM spese WHERE id = %s"
        params = [spesa_id]
        
        if user_id is not None:
            query += " AND user_id = %s"
            params.append(user_id)
        
        result = execute_query(query, tuple(params), fetch=True)
        
        if result and len(result) > 0:
            return cls.from_dict(result[0])
        return None
    
    @classmethod
    def get_all(cls, user_id=None, filters=None):
        """
        Restituisce tutte le spese, opzionalmente filtrate per utente e altri filtri
        Argomenti:
            user_id (int, opzionale): ID utente
            filters (dict, opzionale): Filtri aggiuntivi (categoria, mese)
        """
        query = "SELECT * FROM spese WHERE 1=1"
        params = []
        
        if user_id is not None:
            query += " AND user_id = %s"
            params.append(user_id)
        
        if filters:
            if filters.get('categoria'):
                query += " AND categoria = %s"
                params.append(filters['categoria'])
            
            if filters.get('mese'):
                query += " AND DATE_FORMAT(data, '%Y-%m') = %s"
                params.append(filters['mese'])
        
        query += " ORDER BY data DESC"
        
        result = execute_query(query, tuple(params) if params else None, fetch=True)
        
        return [cls.from_dict(row) for row in result] if result else []
    
    @classmethod
    def get_categorie(cls, user_id=None):
        """Restituisce tutte le categorie distinte, opzionalmente filtrate per utente"""
        query = "SELECT DISTINCT categoria FROM spese"
        params = []
        
        if user_id is not None:
            query += " WHERE user_id = %s"
            params.append(user_id)
        
        query += " ORDER BY categoria"
        
        result = execute_query(query, tuple(params) if params else None, fetch=True)
        
        return [row['categoria'] for row in result if row['categoria']] if result else []
    
    @classmethod
    def get_mesi(cls, user_id=None):
        """Restituisce tutti i mesi distinti in formato YYYY-MM, opzionalmente filtrati per utente"""
        query = "SELECT DISTINCT DATE_FORMAT(data, '%Y-%m') as mese FROM spese"
        params = []
        
        if user_id is not None:
            query += " WHERE user_id = %s"
            params.append(user_id)
        
        query += " ORDER BY mese DESC"
        
        result = execute_query(query, tuple(params) if params else None, fetch=True)
        
        return [row['mese'] for row in result if row['mese']] if result else []
    
    def save(self):
        """Salva la spesa nel database (crea o aggiorna) e sincronizza il CSV"""
        if self.id:
            query = """
            UPDATE spese 
            SET user_id = %s, data = %s, categoria = %s, descrizione = %s, importo = %s
            WHERE id = %s
            """
            execute_query(
                query, 
                (self.user_id, self.data, self.categoria, self.descrizione, float(self.importo), self.id), 
                commit=True
            )
        else:
            query = """
            INSERT INTO spese (user_id, data, categoria, descrizione, importo)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.id = execute_query(
                query, 
                (self.user_id, self.data, self.categoria, self.descrizione, float(self.importo)), 
                commit=True
            )

        spese = self.get_all(user_id=self.user_id)
        self.save_to_csv(self.user_id, spese)
        
        return self.id
    
    def delete(self):
        """Elimina la spesa dal database e aggiorna il CSV"""
        if not self.id:
            return False
        
        query = "DELETE FROM spese WHERE id = %s"
        execute_query(query, (self.id,), commit=True)
        
        spese = self.get_all(user_id=self.user_id)
        self.save_to_csv(self.user_id, spese)
        
        return True