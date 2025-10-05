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

## Déploiement

### GitHub Pages (Interface Statique)

L'interface web est déployée automatiquement sur GitHub Pages via GitHub Actions.

1. Le workflow `.github/workflows/pages.yml` déploie automatiquement le contenu du dossier `docs/` à chaque push sur la branche `main`.
2. L'interface est accessible via : `https://flyrix68.github.io/portail_academique/`

**Note :** L'interface statique ne peut pas exécuter les requêtes API (connexions aux bases de données) car elle nécessite un serveur backend. Pour une démonstration complète, exécutez l'application localement.

### Déploiement Complet (avec Backend)

Pour déployer l'application complète avec le backend Flask :

1. Utilisez Heroku ou un autre service de déploiement Python
2. Le `Procfile` est configuré pour Heroku
3. Assurez-vous que les DSN ODBC sont configurés sur le serveur de déploiement

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