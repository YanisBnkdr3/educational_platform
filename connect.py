import snowflake.connector
from datetime import datetime

# Snowflake database connection
def create_snowflake_connection():
    conn = snowflake.connector.connect(
        user='YANISBNKDR06',
        password='Yanismob06',
        account='iurfcex-xy75467',
        warehouse='COMPUTE_WH',
        database='EXAM_SYSTEM',
        schema='ONLINE_EXAM_SCHEMA'
    )
    return conn

def save_exam(title, description, total_points, professor_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    
    # Insert the exam with the current timestamp
    current_timestamp = datetime.now()
    cursor.execute("""
        INSERT INTO EXAMEN (TITRE, DESCRIPTION, TOTAL_POINTS, PROFESSEUR_ID, DATE_CREATION)
        VALUES (%s, %s, %s, %s, %s)
    """, (title, description, total_points, professor_id, current_timestamp))
    
    # Fetch the last inserted EXAMEN_ID based on the timestamp
    cursor.execute("""
        SELECT EXAMEN_ID FROM EXAMEN 
        WHERE DATE_CREATION = %s
        AND TITRE = %s
        AND PROFESSEUR_ID = %s
    """, (current_timestamp, title, professor_id))
    
    exam_id = cursor.fetchone()[0]  # Fetch the EXAMEN_ID
    conn.commit()
    conn.close()
    
    return exam_id



# Save questions for an exam
def save_question(exam_id, question_text, question_type, correct_answer, choices, points):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO QUESTION (INTITULE, TYPE_QUESTION, REPONSE_CORRECTE, CHOIX, EXAMEN_ID, POINTS)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (question_text, question_type, correct_answer, choices, exam_id, points))
    conn.commit()
    conn.close()

# Get exams created by a professor (for "Gérer les examens")
def get_professor_exams(professor_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT EXAMEN_ID, TITRE FROM EXAMEN WHERE PROFESSEUR_ID = %s", (professor_id,))
    exams = cursor.fetchall()
    conn.close()
    return exams

# Get exam details
def get_exam_details(exam_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    
    # Correct way to execute a parameterized query in Snowflake
    query = "SELECT * FROM EXAMEN WHERE EXAMEN_ID = :1"  # Use :1 for the first parameter
    cursor.execute(query, (exam_id,))  # Passing the parameter as a tuple
    
    exam_details = cursor.fetchone()
    conn.close()
    
    return exam_details



# Assign an exam to a class with start and end times (for "Gérer les examens")
def assign_exam_to_class(exam_id, class_id, start_datetime, end_datetime):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE EXAMEN SET CLASSE_ID = %s, DATE_DEBUT = %s, DATE_FIN = %s
        WHERE EXAMEN_ID = %s
    """, (class_id, start_datetime, end_datetime, exam_id))
    conn.commit()
    conn.close()

# Create a class
def create_class(professor_id, class_name, description):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO CLASSE (NOM, DESCRIPTION, PROFESSEUR_ID)
        VALUES (%s, %s, %s)
    """, (class_name, description, professor_id))
    conn.commit()
    conn.close()

# Get classes managed by a professor
def get_professor_classes(professor_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CLASSE_ID, NOM FROM CLASSE WHERE PROFESSEUR_ID = %s", (professor_id,))
    classes = cursor.fetchall()
    conn.close()
    return classes

# Get all students (for "Gérer les classes")
def get_all_students():
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ETUDIANT_ID, NOM, PRENOM FROM ETUDIANT")
    students = cursor.fetchall()
    conn.close()
    return students

def get_students_in_class(class_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()

    # Update the query to include schema references
    cursor.execute("""
        SELECT ETUDIANT.ETUDIANT_ID, ETUDIANT.NOM, ETUDIANT.PRENOM
        FROM EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.CLASSEETUDIANT AS CLASSEETUDIANT
        JOIN EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.ETUDIANT AS ETUDIANT 
        ON CLASSEETUDIANT.ETUDIANT_ID = ETUDIANT.ETUDIANT_ID
        WHERE CLASSEETUDIANT.CLASSE_ID = %s
    """, (class_id,))
    
    students = cursor.fetchall()
    conn.close()
    return students



# Add a student to a class
def add_student_to_class(student_id, class_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO CLASSEETUDIANT (ETUDIANT_ID, CLASSE_ID)
        VALUES (%s, %s)
    """, (student_id, class_id))
    conn.commit()
    conn.close()

# Remove a student from a class
def remove_student_from_class(student_id, class_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM CLASSEETUDIANT
        WHERE ETUDIANT_ID = %s AND CLASSE_ID = %s
    """, (student_id, class_id))
    conn.commit()
    conn.close()

# Get available classes for a professor (for exam management)
def get_classes(professor_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CLASSE_ID, NOM FROM CLASSE WHERE PROFESSEUR_ID = %s", (professor_id,))
    classes = cursor.fetchall()
    conn.close()
    return classes
