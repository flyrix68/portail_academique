# Démonstration ODBC - Middleware Universitaire

Ce projet démontre l'utilisation d'ODBC comme middleware pour accéder de manière unifiée à trois bases de données différentes : Oracle, MySQL et PostgreSQL.

## Prérequis

- Python 3.8+
- ODBC drivers pour Oracle, MySQL et PostgreSQL
- Configuration des DSN ODBC

## Installation

1. Installer Python depuis https://python.org

2. Créer un environnement virtuel :
```bash
python -m venv venv
```

3. Activer l'environnement virtuel :
```bash
venv\Scripts\activate  # Windows
```

4. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration ODBC

Configurer les DSN suivants dans l'Administrateur de sources de données ODBC :

- OracleDSN : pour Oracle
- MySQLDSN : pour MySQL
- PostgreSQLDSN : pour PostgreSQL

## Lancement

```bash
python app.py
```

Accéder à http://localhost:5000


## Architecture

- `app.py` : Application Flask principale
- `sql_adapter.py` : Couche d'abstraction pour les différences SQL
- `config.py` : Configuration des bases de données
- `templates/index.html` : Interface web
- `static/` : CSS et JavaScript

## Fonctionnalités

- Test des connexions ODBC
- Exécution de requêtes adaptées aux dialectes SQL
- Comparaison avant/après ODBC
- Démonstration des avantages et limites d'ODBC