import numpy as np

encoding = np.load('encodings/102.npy')
print("Encodage facial chargé depuis le fichier .npy :", encoding)
def get_student_id(email):
    conn = create_snowflake_connection()
    try:
        cur = conn.cursor()
        # Requête pour récupérer l'ID de l'étudiant en fonction de l'email
        query = "SELECT ETUDIANT_ID FROM EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.ETUDIANT WHERE COURRIEL = %s"
        cur.execute(query, (email,))
        result = cur.fetchone()
        if result:
            return result[0]  # Renvoie l'ID numérique de l'étudiant
        else:
            print(f"Aucun ID trouvé pour l'email : {email}")
            return None
    finally:
        conn.close()
