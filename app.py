from flask import Flask, render_template, request, jsonify
import pyodbc
from sql_adapter import SQLAdapter
from config import DATABASES

# Direct drivers for comparison
try:
    import cx_Oracle as oracle_driver
    import pymysql as mysql_driver
    import psycopg2 as postgres_driver
    DIRECT_DRIVERS_AVAILABLE = True
except ImportError:
    DIRECT_DRIVERS_AVAILABLE = False
    print("Direct drivers not available - install cx-Oracle, pymysql, psycopg2")

app = Flask(__name__)
adapter = SQLAdapter()

def get_connection(db_name):
    db_config = DATABASES[db_name]
    conn_str = f'DSN={db_config["dsn"]}'
    return pyodbc.connect(conn_str), db_config['type']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect/<db_name>')
def connect_db(db_name):
    try:
        conn, db_type = get_connection(db_name)
        conn.close()
        return jsonify({'status': 'success', 'message': f'Connected to {db_name.upper()}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/query/<db_name>')
def query_db(db_name):
    try:
        conn, db_type = get_connection(db_name)
        cursor = conn.cursor()

        # Example query: Get first 10 students
        base_query = "SELECT * FROM etudiants"
        limit_clause = adapter.get_limit_clause(db_type, 10)
        query = f"{base_query} {limit_clause}"

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return jsonify({'status': 'success', 'data': results, 'query': query})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/student/enrollment/<db_name>')
def check_student_enrollment(db_name):
    import time
    start_time = time.time()

    student_id = request.args.get('id')
    if not student_id:
        return jsonify({'status': 'error', 'message': 'Student ID required'})

    try:
        conn, db_type = get_connection(db_name)
        cursor = conn.cursor()

        query = adapter.get_student_enrollment_query(db_type, student_id)
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        execution_time = round((time.time() - start_time) * 1000, 2)  # ms

        enrolled = len(results) > 0
        return jsonify({
            'status': 'success',
            'method': 'odbc',
            'enrolled': enrolled,
            'data': results[0] if results else None,
            'query': query,
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'error',
            'method': 'odbc',
            'message': str(e),
            'execution_time': execution_time
        })

@app.route('/direct/enrollment/<int:student_id>')
def check_enrollment_direct_demo(student_id):
    """Simulated direct driver approach for demonstration"""
    import time
    start_time = time.time()

    # Simulate the complexity of direct drivers
    # In a real implementation, this would use cx_Oracle, pymysql, psycopg2
    time.sleep(0.15)  # Simulate connection overhead

    # Simulate query execution with different syntax handling
    time.sleep(0.08)  # Simulate query execution

    execution_time = round((time.time() - start_time) * 1000, 2)

    # Mock result for demonstration
    mock_result = {
        'id_etudiant': student_id,
        'nom': 'Dupont',
        'prenom': 'Jean',
        'statut': 'INSCRIT'
    }

    return jsonify({
        'status': 'success',
        'method': 'direct',
        'enrolled': True,
        'data': mock_result,
        'execution_time': execution_time,
        'note': 'Simulation - Drivers directs non installés'
    })

@app.route('/student/details/<db_name>')
def get_student_details(db_name):
    student_id = request.args.get('id')
    if not student_id:
        return jsonify({'status': 'error', 'message': 'Student ID required'})

    try:
        conn, db_type = get_connection(db_name)
        cursor = conn.cursor()

        query = adapter.get_student_details_query(db_type, student_id)
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return jsonify({
            'status': 'success',
            'data': results[0] if results else None,
            'query': query
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/student/grades/<db_name>')
def get_student_grades(db_name):
    student_id = request.args.get('id')
    if not student_id:
        return jsonify({'status': 'error', 'message': 'Student ID required'})

    try:
        conn, db_type = get_connection(db_name)
        cursor = conn.cursor()

        query = adapter.get_student_grades_query(db_type, student_id)
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return jsonify({
            'status': 'success',
            'data': results,
            'query': query
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/student/search/<db_name>')
def search_students(db_name):
    name = request.args.get('name')
    if not name:
        return jsonify({'status': 'error', 'message': 'Name required'})

    try:
        conn, db_type = get_connection(db_name)
        cursor = conn.cursor()

        query = adapter.get_students_by_name_query(db_type, name)
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return jsonify({
            'status': 'success',
            'data': results,
            'query': query
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/books/borrow', methods=['POST'])
def borrow_book():
    """Borrow a book - requires student_id and book_id"""
    data = request.get_json()
    student_id = data.get('student_id')
    book_id = data.get('book_id')

    if not student_id or not book_id:
        return jsonify({'status': 'error', 'message': 'Student ID and Book ID required'})

    try:
        conn_pg, pg_type = get_connection('postgresql')
        cursor_pg = conn_pg.cursor()

        # Check if book is available
        cursor_pg.execute(f"SELECT disponible FROM livres WHERE id_livre = {book_id}")
        book_status = cursor_pg.fetchone()

        if not book_status or not book_status[0]:
            conn_pg.close()
            return jsonify({'status': 'error', 'message': 'Book is not available'})

        # Borrow the book
        borrow_query = adapter.borrow_book_query(pg_type, student_id, book_id)
        cursor_pg.execute(borrow_query)

        # Update book availability
        availability_query = adapter.update_book_availability_query(pg_type, book_id, 'false')
        cursor_pg.execute(availability_query)

        conn_pg.commit()
        conn_pg.close()

        return jsonify({
            'status': 'success',
            'message': 'Book borrowed successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Data insertion endpoints for populating databases
@app.route('/admin/insert/student', methods=['POST'])
def insert_student():
    """Insert a new student into Oracle database"""
    import time
    start_time = time.time()

    data = request.get_json()
    if not data or not all(k in data for k in ['id_etudiant', 'nom', 'prenom', 'email']):
        return jsonify({'status': 'error', 'message': 'Missing required fields'})

    try:
        conn, db_type = get_connection('oracle')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO etudiants (id_etudiant, nom, prenom, email, telephone, adresse, statut)
            VALUES (:id, :nom, :prenom, :email, :tel, :adresse, 'INSCRIT')
        """, {
            'id': data['id_etudiant'],
            'nom': data['nom'],
            'prenom': data['prenom'],
            'email': data['email'],
            'tel': data.get('telephone', ''),
            'adresse': data.get('adresse', '')
        })

        conn.commit()
        conn.close()

        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'success',
            'method': 'odbc',
            'message': f'Étudiant {data["nom"]} {data["prenom"]} ajouté avec succès',
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'error',
            'method': 'odbc',
            'message': str(e),
            'execution_time': execution_time
        })

@app.route('/admin/insert/grade', methods=['POST'])
def insert_grade():
    """Insert a grade into MySQL database"""
    import time
    start_time = time.time()

    data = request.get_json()
    if not data or not all(k in data for k in ['id_etudiant', 'id_matiere', 'note', 'date_evaluation']):
        return jsonify({'status': 'error', 'message': 'Missing required fields'})

    try:
        conn, db_type = get_connection('mysql')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO notes (id_etudiant, id_matiere, note, date_evaluation)
            VALUES (%s, %s, %s, %s)
        """, (
            data['id_etudiant'],
            data['id_matiere'],
            data['note'],
            data['date_evaluation']
        ))

        conn.commit()
        conn.close()

        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'success',
            'method': 'odbc',
            'message': f'Note {data["note"]}/20 ajoutée pour l\'étudiant {data["id_etudiant"]}',
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'error',
            'method': 'odbc',
            'message': str(e),
            'execution_time': execution_time
        })

@app.route('/admin/insert/book', methods=['POST'])
def insert_book():
    """Insert a book into PostgreSQL database"""
    import time
    start_time = time.time()

    data = request.get_json()
    if not data or not all(k in data for k in ['id_livre', 'titre', 'auteur']):
        return jsonify({'status': 'error', 'message': 'Missing required fields'})

    try:
        conn, db_type = get_connection('postgresql')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO livres (id_livre, titre, auteur, categorie, disponible)
            VALUES (%s, %s, %s, %s, true)
        """, (
            data['id_livre'],
            data['titre'],
            data['auteur'],
            data.get('categorie', 'Général'),
        ))

        conn.commit()
        conn.close()

        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'success',
            'method': 'odbc',
            'message': f'Livre "{data["titre"]}" ajouté avec succès',
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'error',
            'method': 'odbc',
            'message': str(e),
            'execution_time': execution_time
        })

@app.route('/admin/create/loan', methods=['POST'])
def create_loan():
    """Create a book loan in PostgreSQL database"""
    import time
    start_time = time.time()

    data = request.get_json()
    if not data or not all(k in data for k in ['id_etudiant', 'id_livre']):
        return jsonify({'status': 'error', 'message': 'Missing required fields'})

    try:
        conn, db_type = get_connection('postgresql')
        cursor = conn.cursor()

        # Check if book is available
        cursor.execute("SELECT disponible FROM livres WHERE id_livre = %s", (data['id_livre'],))
        book = cursor.fetchone()

        if not book or not book[0]:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Livre non disponible'})

        # Create loan
        from datetime import datetime, timedelta
        date_emprunt = datetime.now()
        date_retour_prevue = date_emprunt + timedelta(days=30)

        cursor.execute("""
            INSERT INTO emprunts (id_etudiant, id_livre, date_emprunt, date_retour_prevue)
            VALUES (%s, %s, %s, %s)
        """, (
            data['id_etudiant'],
            data['id_livre'],
            date_emprunt,
            date_retour_prevue
        ))

        # Mark book as unavailable
        cursor.execute("UPDATE livres SET disponible = false WHERE id_livre = %s", (data['id_livre'],))

        conn.commit()
        conn.close()

        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'success',
            'method': 'odbc',
            'message': f'Emprunt créé pour l\'étudiant {data["id_etudiant"]} - livre {data["id_livre"]}',
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'error',
            'method': 'odbc',
            'message': str(e),
            'execution_time': execution_time
        })

@app.route('/admin/populate/sample', methods=['POST'])
def populate_sample_data():
    """Populate all databases with sample data"""
    import time
    start_time = time.time()

    results = {'oracle': None, 'mysql': None, 'postgresql': None}

    # Sample students for Oracle
    students = [
        {'id': 1, 'nom': 'Dupont', 'prenom': 'Jean', 'email': 'jean.dupont@univ.fr', 'tel': '0102030405', 'adresse': '123 Rue A'},
        {'id': 2, 'nom': 'Martin', 'prenom': 'Marie', 'email': 'marie.martin@univ.fr', 'tel': '0102030406', 'adresse': '456 Rue B'},
        {'id': 3, 'nom': 'Dubois', 'prenom': 'Pierre', 'email': 'pierre.dubois@univ.fr', 'tel': '0102030407', 'adresse': '789 Rue C'}
    ]

    # Sample grades for MySQL
    grades = [
        {'id_etudiant': 1, 'id_matiere': 1, 'note': 15.5, 'date': '2024-01-15'},
        {'id_etudiant': 1, 'id_matiere': 2, 'note': 14.0, 'date': '2024-01-20'},
        {'id_etudiant': 2, 'id_matiere': 1, 'note': 16.5, 'date': '2024-01-15'},
        {'id_etudiant': 3, 'id_matiere': 2, 'note': 13.5, 'date': '2024-01-20'}
    ]

    # Sample books for PostgreSQL
    books = [
        {'id': 1, 'titre': 'Introduction à l\'Informatique', 'auteur': 'Alice Dupont', 'categorie': 'Informatique'},
        {'id': 2, 'titre': 'Mathématiques Discrètes', 'auteur': 'Bob Martin', 'categorie': 'Mathématiques'},
        {'id': 3, 'titre': 'Bases de Données', 'auteur': 'Claire Dubois', 'categorie': 'Informatique'}
    ]

    # Insert students (Oracle)
    try:
        conn, _ = get_connection('oracle')
        cursor = conn.cursor()
        for student in students:
            cursor.execute("""
                INSERT INTO etudiants (id_etudiant, nom, prenom, email, telephone, adresse, statut)
                VALUES (:id, :nom, :prenom, :email, :tel, :adresse, 'INSCRIT')
            """, {
                'id': student['id'], 'nom': student['nom'], 'prenom': student['prenom'],
                'email': student['email'], 'tel': student['tel'], 'adresse': student['adresse']
            })
        conn.commit()
        conn.close()
        results['oracle'] = {'status': 'success', 'count': len(students)}
    except Exception as e:
        results['oracle'] = {'status': 'error', 'message': str(e)}

    # Insert grades (MySQL)
    try:
        conn, _ = get_connection('mysql')
        cursor = conn.cursor()
        for grade in grades:
            cursor.execute("""
                INSERT INTO notes (id_etudiant, id_matiere, note, date_evaluation)
                VALUES (%s, %s, %s, %s)
            """, (grade['id_etudiant'], grade['id_matiere'], grade['note'], grade['date']))
        conn.commit()
        conn.close()
        results['mysql'] = {'status': 'success', 'count': len(grades)}
    except Exception as e:
        results['mysql'] = {'status': 'error', 'message': str(e)}

    # Insert books (PostgreSQL)
    try:
        conn, _ = get_connection('postgresql')
        cursor = conn.cursor()
        for book in books:
            cursor.execute("""
                INSERT INTO livres (id_livre, titre, auteur, categorie, disponible)
                VALUES (%s, %s, %s, %s, true)
            """, (book['id'], book['titre'], book['auteur'], book['categorie']))
        conn.commit()
        conn.close()
        results['postgresql'] = {'status': 'success', 'count': len(books)}
    except Exception as e:
        results['postgresql'] = {'status': 'error', 'message': str(e)}

    execution_time = round((time.time() - start_time) * 1000, 2)
    return jsonify({
        'status': 'completed',
        'execution_time': execution_time,
        'results': results
    })

# Library management endpoints
@app.route('/books/available')
def get_available_books():
    """Get all available books from PostgreSQL"""
    import time
    start_time = time.time()

    try:
        conn, db_type = get_connection('postgresql')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_livre, titre, auteur, categorie
            FROM livres
            WHERE disponible = true
            ORDER BY titre
        """)

        books = []
        for row in cursor.fetchall():
            books.append({
                'id_livre': row[0],
                'titre': row[1],
                'auteur': row[2],
                'categorie': row[3]
            })

        conn.close()

        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'success',
            'method': 'odbc',
            'books': books,
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'error',
            'method': 'odbc',
            'message': str(e),
            'execution_time': execution_time
        })

@app.route('/books/my-loans/<int:student_id>')
def get_my_loans(student_id):
    """Get student's current loans from PostgreSQL"""
    import time
    start_time = time.time()

    try:
        conn, db_type = get_connection('postgresql')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.id_emprunt, l.titre, l.auteur, e.date_emprunt, e.date_retour_prevue
            FROM emprunts e
            JOIN livres l ON e.id_livre = l.id_livre
            WHERE e.id_etudiant = %s AND e.date_retour IS NULL
            ORDER BY e.date_emprunt DESC
        """, (student_id,))

        loans = []
        for row in cursor.fetchall():
            loans.append({
                'id_emprunt': row[0],
                'titre': row[1],
                'auteur': row[2],
                'date_emprunt': row[3].strftime('%d/%m/%Y') if row[3] else None,
                'date_retour_prevue': row[4].strftime('%d/%m/%Y') if row[4] else None
            })

        conn.close()

        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'success',
            'method': 'odbc',
            'loans': loans,
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'status': 'error',
            'method': 'odbc',
            'message': str(e),
            'execution_time': execution_time
        })


# Direct driver functions (without ODBC middleware)
def get_oracle_connection_direct():
    """Direct Oracle connection using cx_Oracle"""
    try:
        # Using a simplified connection string - in real scenario would use actual credentials
        dsn = cx_Oracle.makedsn("localhost", 1521, service_name="XE")
        connection = cx_Oracle.connect(user="system", password="password", dsn=dsn)
        return connection
    except Exception as e:
        raise Exception(f"Oracle direct connection failed: {str(e)}")

def get_mysql_connection_direct():
    """Direct MySQL connection using pymysql"""
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="password",
            database="university",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        raise Exception(f"MySQL direct connection failed: {str(e)}")

def get_postgres_connection_direct():
    """Direct PostgreSQL connection using psycopg2"""
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="university",
            user="postgres",
            password="password"
        )
        return connection
    except Exception as e:
        raise Exception(f"PostgreSQL direct connection failed: {str(e)}")

@app.route('/direct/enrollment/<int:student_id>')
def check_enrollment_direct(student_id):
    """Check student enrollment using direct Oracle driver"""
    if not DIRECT_DRIVERS_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'Direct drivers not available'})

    try:
        conn = get_oracle_connection_direct()
        cursor = conn.cursor()

        # Oracle-specific SQL syntax
        cursor.execute("""
            SELECT id_etudiant, nom, prenom, statut
            FROM etudiants
            WHERE id_etudiant = :student_id AND statut = 'INSCRIT'
        """, {'student_id': student_id})

        result = cursor.fetchone()
        conn.close()

        if result:
            return jsonify({
                'status': 'success',
                'method': 'direct_oracle',
                'enrolled': True,
                'data': {
                    'id_etudiant': result[0],
                    'nom': result[1],
                    'prenom': result[2],
                    'statut': result[3]
                }
            })
        else:
            return jsonify({
                'status': 'success',
                'method': 'direct_oracle',
                'enrolled': False
            })

    except Exception as e:
        return jsonify({'status': 'error', 'method': 'direct_oracle', 'message': str(e)})

@app.route('/direct/grades/<int:student_id>')
def get_grades_direct(student_id):
    """Get student grades using direct MySQL driver"""
    if not DIRECT_DRIVERS_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'Direct drivers not available'})

    try:
        conn = get_mysql_connection_direct()
        cursor = conn.cursor()

        # MySQL-specific SQL syntax
        cursor.execute("""
            SELECT n.id_etudiant, n.note, n.date_evaluation,
                   m.nom_matiere, m.coefficient
            FROM notes n
            JOIN matieres m ON n.id_matiere = m.id_matiere
            WHERE n.id_etudiant = %s
            ORDER BY n.date_evaluation DESC
        """, (student_id,))

        results = cursor.fetchall()
        conn.close()

        return jsonify({
            'status': 'success',
            'method': 'direct_mysql',
            'grades': results
        })

    except Exception as e:
        return jsonify({'status': 'error', 'method': 'direct_mysql', 'message': str(e)})

@app.route('/direct/books/<int:student_id>')
def get_books_direct(student_id):
    """Get student borrowed books using direct PostgreSQL driver"""
    if not DIRECT_DRIVERS_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'Direct drivers not available'})

    try:
        conn = get_postgres_connection_direct()
        cursor = conn.cursor()

        # PostgreSQL-specific SQL syntax
        cursor.execute("""
            SELECT l.titre, l.auteur, e.date_emprunt, e.date_retour_prevue,
                   CASE WHEN e.date_retour IS NULL THEN 'En cours' ELSE 'Retourné' END as statut
            FROM emprunts e
            JOIN livres l ON e.id_livre = l.id_livre
            WHERE e.id_etudiant = %s
            ORDER BY e.date_emprunt DESC
        """, (student_id,))

        results = cursor.fetchall()
        conn.close()

        return jsonify({
            'status': 'success',
            'method': 'direct_postgresql',
            'books': results
        })

    except Exception as e:
        return jsonify({'status': 'error', 'method': 'direct_postgresql', 'message': str(e)})

@app.route('/compare/methods/<int:student_id>')
def compare_methods(student_id):
    """Compare direct drivers vs ODBC for the same operation"""
    results = {
        'student_id': student_id,
        'methods': {}
    }

    # Test ODBC method
    try:
        start_time = time.time()
        response = get_student_dashboard(student_id)
        odbc_time = time.time() - start_time
        results['methods']['odbc'] = {
            'time': round(odbc_time * 1000, 2),  # ms
            'status': 'success' if response.status_code == 200 else 'error'
        }
    except:
        results['methods']['odbc'] = {'status': 'error'}

    # Test direct drivers method
    if DIRECT_DRIVERS_AVAILABLE:
        try:
            start_time = time.time()

            # Direct Oracle call
            oracle_result = check_enrollment_direct(student_id)

            # Direct MySQL call
            mysql_result = get_grades_direct(student_id)

            # Direct PostgreSQL call
            postgres_result = get_books_direct(student_id)

            direct_time = time.time() - start_time
            results['methods']['direct'] = {
                'time': round(direct_time * 1000, 2),  # ms
                'status': 'success',
                'oracle': oracle_result.get_json(),
                'mysql': mysql_result.get_json(),
                'postgresql': postgres_result.get_json()
            }
        except:
            results['methods']['direct'] = {'status': 'error'}
    else:
        results['methods']['direct'] = {'status': 'unavailable', 'message': 'Direct drivers not installed'}

    return jsonify(results)

@app.route('/books/my-loans/<int:student_id>')
def get_student_loans(student_id):
    """Get student's current book loans"""
    try:
        conn_pg, pg_type = get_connection('postgresql')
        cursor_pg = conn_pg.cursor()

        query = adapter.get_student_current_loans_query(pg_type, student_id)
        cursor_pg.execute(query)
        columns = [column[0] for column in cursor_pg.description]
        results = [dict(zip(columns, row)) for row in cursor_pg.fetchall()]

        conn_pg.close()
        return jsonify({
            'status': 'success',
            'loans': results
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/books/return', methods=['POST'])
def return_book():
    """Return a book - requires loan_id"""
    data = request.get_json()
    loan_id = data.get('loan_id')

    if not loan_id:
        return jsonify({'status': 'error', 'message': 'Loan ID required'})

    try:
        conn_pg, pg_type = get_connection('postgresql')
        cursor_pg = conn_pg.cursor()

        # Get book_id from loan
        cursor_pg.execute(f"SELECT id_livre FROM emprunts WHERE id_emprunt = {loan_id}")
        loan_info = cursor_pg.fetchone()

        if not loan_info:
            conn_pg.close()
            return jsonify({'status': 'error', 'message': 'Loan not found'})

        book_id = loan_info[0]

        # Return the book
        return_query = adapter.return_book_query(pg_type, loan_id)
        cursor_pg.execute(return_query)

        # Update book availability
        availability_query = adapter.update_book_availability_query(pg_type, book_id, 'true')
        cursor_pg.execute(availability_query)

        conn_pg.commit()
        conn_pg.close()

        return jsonify({
            'status': 'success',
            'message': 'Book returned successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stats/enrollment/<db_name>')
def get_enrollment_stats(db_name):
    try:
        conn, db_type = get_connection(db_name)
        cursor = conn.cursor()

        query = adapter.get_enrollment_count_query(db_type)
        cursor.execute(query)
        result = cursor.fetchone()

        conn.close()
        return jsonify({
            'status': 'success',
            'total_enrolled': result[0] if result else 0,
            'query': query
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/admin/all-books')
def get_all_books_admin():
    """Get all books with their status for admin view"""
    try:
        conn, db_type = get_connection('postgresql')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_livre, titre, auteur, categorie, disponible
            FROM livres
            ORDER BY id_livre
        """)

        books = []
        for row in cursor.fetchall():
            books.append({
                'id_livre': row[0],
                'titre': row[1],
                'auteur': row[2],
                'categorie': row[3],
                'disponible': row[4]
            })

        conn.close()
        return jsonify({
            'status': 'success',
            'books': books
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/admin/all-loans')
def get_all_loans_admin():
    """Get all loans with complete information for admin view"""
    try:
        conn, db_type = get_connection('postgresql')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.id_emprunt, e.id_etudiant, e.id_livre, l.titre, l.auteur,
                   e.date_emprunt, e.date_retour_prevue, e.date_retour
            FROM emprunts e
            LEFT JOIN livres l ON e.id_livre = l.id_livre
            ORDER BY e.date_emprunt DESC
        """)

        loans = []
        for row in cursor.fetchall():
            loans.append({
                'id_emprunt': row[0],
                'id_etudiant': row[1],
                'id_livre': row[2],
                'titre': row[3],
                'auteur': row[4],
                'date_emprunt': row[5].isoformat() if row[5] else None,
                'date_retour_prevue': row[6].isoformat() if row[6] else None,
                'date_retour': row[7].isoformat() if row[7] else None
            })

        conn.close()
        return jsonify({
            'status': 'success',
            'loans': loans
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/dashboard/<int:student_id>')
def get_student_dashboard(student_id):
    """Get complete student dashboard from all three databases"""
    try:
        dashboard_data = {}

        # Get student profile from Oracle
        try:
            conn_oracle, oracle_type = get_connection('oracle')
            cursor_oracle = conn_oracle.cursor()
            query_profile = adapter.get_student_profile_query(oracle_type, student_id)
            cursor_oracle.execute(query_profile)
            profile_result = cursor_oracle.fetchone()
            if profile_result:
                dashboard_data['profile'] = {
                    'id_etudiant': profile_result[0],
                    'nom': profile_result[1],
                    'prenom': profile_result[2],
                    'email': profile_result[3],
                    'telephone': profile_result[4],
                    'adresse': profile_result[5]
                }
            conn_oracle.close()
        except Exception as e:
            dashboard_data['profile_error'] = f"Erreur Oracle: {str(e)}"

        # Get GPA from MySQL
        try:
            conn_mysql, mysql_type = get_connection('mysql')
            cursor_mysql = conn_mysql.cursor()
            query_gpa = adapter.get_student_gpa_query(mysql_type, student_id)
            cursor_mysql.execute(query_gpa)
            gpa_result = cursor_mysql.fetchone()
            dashboard_data['gpa'] = float(gpa_result[0]) if gpa_result and gpa_result[0] else None
            conn_mysql.close()
        except Exception as e:
            dashboard_data['gpa_error'] = f"Erreur MySQL: {str(e)}"

        # Get borrowed books count from PostgreSQL
        try:
            conn_pg, pg_type = get_connection('postgresql')
            cursor_pg = conn_pg.cursor()
            query_books = adapter.get_borrowed_books_count_query(pg_type, student_id)
            cursor_pg.execute(query_books)
            books_result = cursor_pg.fetchone()
            dashboard_data['borrowed_books'] = books_result[0] if books_result else 0
            conn_pg.close()
        except Exception as e:
            dashboard_data['books_error'] = f"Erreur PostgreSQL: {str(e)}"

        return jsonify({
            'status': 'success',
            'student_id': student_id,
            'data': dashboard_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/graduation/<int:student_id>')
def check_graduation_eligibility(student_id):
    """Check graduation eligibility across all three databases"""
    try:
        graduation_checks = {}

        # Check tuition payment from Oracle
        try:
            conn_oracle, oracle_type = get_connection('oracle')
            cursor_oracle = conn_oracle.cursor()
            query_tuition = adapter.get_tuition_payment_query(oracle_type, student_id)
            cursor_oracle.execute(query_tuition)
            tuition_result = cursor_oracle.fetchone()
            graduation_checks['tuition_paid'] = tuition_result[0] > 0 if tuition_result else False
            conn_oracle.close()
        except Exception as e:
            graduation_checks['tuition_error'] = f"Erreur Oracle: {str(e)}"
            graduation_checks['tuition_paid'] = False

        # Check credits validation from MySQL
        try:
            conn_mysql, mysql_type = get_connection('mysql')
            cursor_mysql = conn_mysql.cursor()
            query_credits = adapter.get_credits_validation_query(mysql_type, student_id)
            cursor_mysql.execute(query_credits)
            credits_result = cursor_mysql.fetchone()
            total_credits = credits_result[0] if credits_result and credits_result[0] else 0
            graduation_checks['credits_validated'] = total_credits >= 180  # Assuming 180 credits required
            graduation_checks['total_credits'] = total_credits
            conn_mysql.close()
        except Exception as e:
            graduation_checks['credits_error'] = f"Erreur MySQL: {str(e)}"
            graduation_checks['credits_validated'] = False
            graduation_checks['total_credits'] = 0

        # Check overdue books from PostgreSQL
        try:
            conn_pg, pg_type = get_connection('postgresql')
            cursor_pg = conn_pg.cursor()
            query_overdue = adapter.get_overdue_books_query(pg_type, student_id)
            cursor_pg.execute(query_overdue)
            overdue_result = cursor_pg.fetchone()
            graduation_checks['no_overdue_books'] = overdue_result[0] == 0 if overdue_result else True
            graduation_checks['overdue_books_count'] = overdue_result[0] if overdue_result else 0
            conn_pg.close()
        except Exception as e:
            graduation_checks['overdue_error'] = f"Erreur PostgreSQL: {str(e)}"
            graduation_checks['no_overdue_books'] = False
            graduation_checks['overdue_books_count'] = 0

        # Overall eligibility
        graduation_checks['eligible_for_graduation'] = (
            graduation_checks.get('tuition_paid', False) and
            graduation_checks.get('credits_validated', False) and
            graduation_checks.get('no_overdue_books', False)
        )

        return jsonify({
            'status': 'success',
            'student_id': student_id,
            'checks': graduation_checks
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True)