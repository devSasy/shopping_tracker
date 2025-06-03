# ShoppingTracker - Gestore Spese Personali con Flask

Un'applicazione web per monitorare le spese personali, dotata di autenticazione utente, filtri avanzati e funzionalità di esportazione in CSV.

## 🚀 Funzionalità Principali

- Registrazione e autenticazione utenti
- Aggiunta, modifica e cancellazione delle spese
- Filtraggio delle spese per categoria e mese
- Esportazione delle spese in formato CSV
- Interfaccia responsive con Bootstrap 5
- Persistenza dei dati su MariaDB e backup in CSV

## 📋 Prerequisiti

- Python 3.10 o superiore
- DBMS come HeidiSQL (o altro client MySQL, opzionale)
- se si usa HeidiSQL usare Xampp eventualmente per aprire le porte MySQL

## 🛠️ Installazione

1. **Clona il repository:**
   ```bash
   git clone https://github.com/devsasy/shopping-tracker.git
   cd shopping-tracker
   ```

2. **Crea e attiva un ambiente virtuale:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Installa le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura le variabili d'ambiente:**
   Crea un file `.env` nella directory principale del progetto con il seguente contenuto:
   ```env
   # Configurazione Flask
   SECRET_KEY=la-tua-chiave-segreta
   DEBUG=True

   # Configurazione Database
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASS=la-tua-password
   DB_NAME=shopping_tracker

   # Directory per i CSV
   CSV_DIR=data
   ```

5. **Inizializza il database:**
   ```bash
   mysql -u root -p < migration/init.sql
   ```

## ▶️ Avvio dell'Applicazione

1. **Assicurati di aver attivato l'ambiente virtuale:**
   ```bash
   venv\Scripts\activate
   ```

2. **Avvia l'app Flask:**
   ```bash
   flask run
   ```

3. Apri il browser e vai su:
   [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## ❓ FAQ

**1. Posso usare un database diverso da MariaDB?**
Sì, puoi utilizzare ad esempio MySQL. Assicurati di aggiornare le variabili d'ambiente di conseguenza.

**2. Dove vengono salvati i file CSV?**
Nella cartella specificata dalla variabile `CSV_DIR` (di default è stato impostato `data`).

**3. Come posso cambiare la porta dell'applicazione?**
Puoi avviare Flask su una porta diversa con:
```bash
flask run --port 8080
```

## 📦 Dipendenze Principali

- Flask
- Flask-Login
- python-dotenv
- mysql-connector-python
- Bootstrap 5

Per l'elenco completo, consulta `requirements.txt`.

## 📝 Licenza

Questo progetto è distribuito sotto licenza MIT.
