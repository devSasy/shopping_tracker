CREATE DATABASE IF NOT EXISTS shopping_tracker;

USE shopping_tracker;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella spese: ogni riga rappresenta una spesa registrata da un utente.
--    - La chiave esterna su user_id garantisce che ogni spesa sia sempre associata a un utente esistente.
CREATE TABLE IF NOT EXISTS spese (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  data DATE NOT NULL,
  categoria VARCHAR(100) NOT NULL,
  descrizione VARCHAR(255) NOT NULL,
  importo DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indici: vengono creati per velocizzare le ricerche più frequenti (per utente, data e categoria).
CREATE INDEX idx_spese_user_id ON spese(user_id);
CREATE INDEX idx_spese_data ON spese(data);
CREATE INDEX idx_spese_categoria ON spese(categoria);