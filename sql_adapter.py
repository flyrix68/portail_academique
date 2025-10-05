class SQLAdapter:
    def get_limit_clause(self, sgbd_type, limit):
        if sgbd_type.upper() == 'ORACLE':
            return f"WHERE ROWNUM <= {limit}"
        elif sgbd_type.upper() in ['MYSQL', 'POSTGRESQL']:
            return f"LIMIT {limit}"

    def get_isnull_function(self, sgbd_type, column, default):
        if sgbd_type.upper() == 'ORACLE':
            return f"NVL({column}, {default})"
        elif sgbd_type.upper() == 'MYSQL':
            return f"IFNULL({column}, {default})"
        elif sgbd_type.upper() == 'POSTGRESQL':
            return f"COALESCE({column}, {default})"

    def get_student_enrollment_query(self, sgbd_type, student_id):
        """Check if student is enrolled"""
        limit_clause = self.get_limit_clause(sgbd_type, 1)
        return f"SELECT id_etudiant, nom, prenom, statut FROM etudiants WHERE id_etudiant = {student_id} {limit_clause}"

    def get_student_details_query(self, sgbd_type, student_id):
        """Get complete student details"""
        return f"SELECT * FROM etudiants WHERE id_etudiant = {student_id}"

    def get_student_grades_query(self, sgbd_type, student_id):
        """Get student grades (assuming grades table exists)"""
        return f"SELECT matiere, note, date_evaluation FROM notes WHERE id_etudiant = {student_id}"

    def get_students_by_name_query(self, sgbd_type, name):
        """Search students by name"""
        limit_clause = self.get_limit_clause(sgbd_type, 10)
        return f"SELECT id_etudiant, nom, prenom FROM etudiants WHERE UPPER(nom) LIKE UPPER('%{name}%') {limit_clause}"

    def get_enrollment_count_query(self, sgbd_type):
        """Get total number of enrolled students"""
        if sgbd_type.upper() == 'ORACLE':
            return "SELECT COUNT(*) as total FROM etudiants WHERE statut = 'INSCRIT'"
        elif sgbd_type.upper() in ['MYSQL', 'POSTGRESQL']:
            return "SELECT COUNT(*) as total FROM etudiants WHERE statut = 'INSCRIT'"

    def get_student_profile_query(self, sgbd_type, student_id):
        """Get student personal information (Oracle)"""
        return f"SELECT id_etudiant, nom, prenom, email, telephone, adresse FROM etudiants WHERE id_etudiant = {student_id}"

    def get_student_gpa_query(self, sgbd_type, student_id):
        """Get student GPA from grades (MySQL)"""
        if sgbd_type.upper() == 'MYSQL':
            return f"SELECT AVG(note) as moyenne_generale FROM notes WHERE id_etudiant = {student_id}"
        else:
            # For other databases, return a compatible query (though ideally this would be MySQL specific)
            return f"SELECT AVG(note) as moyenne_generale FROM notes WHERE id_etudiant = {student_id}"

    def get_borrowed_books_count_query(self, sgbd_type, student_id):
        """Get count of currently borrowed books (PostgreSQL)"""
        return f"SELECT COUNT(*) as livres_empruntes FROM emprunts WHERE id_etudiant = {student_id} AND date_retour IS NULL"

    def get_tuition_payment_query(self, sgbd_type, student_id):
        """Check if student has paid tuition fees (Oracle)"""
        return f"SELECT COUNT(*) as frais_payes FROM paiements WHERE id_etudiant = {student_id} AND type_paiement = 'SCOLARITE' AND statut = 'PAYE'"

    def get_credits_validation_query(self, sgbd_type, student_id):
        """Check if student has enough credits (MySQL)"""
        if sgbd_type.upper() == 'MYSQL':
            return f"SELECT SUM(credits) as total_credits FROM notes n JOIN matieres m ON n.id_matiere = m.id_matiere WHERE n.id_etudiant = {student_id} AND n.note >= 10"
        else:
            return f"SELECT SUM(credits) as total_credits FROM notes n JOIN matieres m ON n.id_matiere = m.id_matiere WHERE n.id_etudiant = {student_id} AND n.note >= 10"

    def get_overdue_books_query(self, sgbd_type, student_id):
        """Check for overdue books (PostgreSQL)"""
        return f"SELECT COUNT(*) as livres_en_retard FROM emprunts WHERE id_etudiant = {student_id} AND date_retour IS NULL AND date_retour_prevue < CURRENT_DATE"

    def get_available_books_query(self, sgbd_type):
        """Get list of available books (PostgreSQL)"""
        return "SELECT id_livre, titre, auteur, categorie FROM livres WHERE disponible = true ORDER BY titre"

    def borrow_book_query(self, sgbd_type, student_id, book_id):
        """Borrow a book - insert into loans table (PostgreSQL)"""
        return f"INSERT INTO emprunts (id_etudiant, id_livre, date_emprunt, date_retour_prevue) VALUES ({student_id}, {book_id}, CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days')"

    def update_book_availability_query(self, sgbd_type, book_id, available):
        """Update book availability (PostgreSQL)"""
        return f"UPDATE livres SET disponible = {available} WHERE id_livre = {book_id}"

    def get_student_current_loans_query(self, sgbd_type, student_id):
        """Get student's current book loans (PostgreSQL)"""
        return f"SELECT e.id_emprunt, l.titre, l.auteur, e.date_emprunt, e.date_retour_prevue FROM emprunts e JOIN livres l ON e.id_livre = l.id_livre WHERE e.id_etudiant = {student_id} AND e.date_retour IS NULL ORDER BY e.date_emprunt DESC"

    def return_book_query(self, sgbd_type, loan_id):
        """Return a book - update loan with return date (PostgreSQL)"""
        return f"UPDATE emprunts SET date_retour = CURRENT_DATE WHERE id_emprunt = {loan_id}"