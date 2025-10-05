# Configuration for database connections
# DSNs must be configured in ODBC Data Source Administrator

DATABASES = {
    'oracle': {
        'dsn': 'OracleDSN',  # Replace with actual DSN name
        'type': 'ORACLE'
    },
    'mysql': {
        'dsn': 'MySQLDSN',  # Replace with actual DSN name
        'type': 'MYSQL'
    },
    'postgresql': {
        'dsn': 'PostgreSQLDSN',  # Replace with actual DSN name
        'type': 'POSTGRESQL'
    }
}