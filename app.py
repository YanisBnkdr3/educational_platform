import streamlit as st
import snowflake.connector
from signup import signup_form, verify_face, verify_voice  # Ajouter `verify_voice` pour la vérification vocale
from professor_module import professor_interface
from student_module import student_interface
from connect import create_snowflake_connection

# Fonction pour récupérer l'ID étudiant en fonction de l'email
def get_student_id(email):
    conn = create_snowflake_connection()
    try:
        cur = conn.cursor()
        query = "SELECT ETUDIANT_ID FROM EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.ETUDIANT WHERE COURRIEL = %s"
        cur.execute(query, (email,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            print(f"Aucun ID trouvé pour l'email : {email}")
            return None
    finally:
        conn.close()

# Fonction pour vérifier les identifiants de connexion
def verify_login(email, nip, role):
    conn = create_snowflake_connection()
    cur = conn.cursor()
    try:
        print(f"Tentative de connexion avec l'email : {email}, le NIP : {nip} et le rôle : {role}")
        
        if role == "Étudiant":
            query = """
            SELECT courriel, nip FROM EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.ETUDIANT
            WHERE courriel = %s AND nip = %s
            """
        elif role == "Professeur":
            query = """
            SELECT courriel, nip FROM EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.PROFESSEUR
            WHERE courriel = %s AND nip = %s
            """
        else:
            print("Rôle invalide.")
            return False

        cur.execute(query, (email, nip))
        result = cur.fetchone()

        if result:
            print("Connexion réussie.")
            return True
        else:
            print("Échec de la connexion : Courriel ou NIP invalide.")
            return False
    finally:
        conn.close()

# Fonction pour obtenir le nom d'utilisateur basé sur le rôle
def get_user_name(email, role):
    conn = create_snowflake_connection()
    try:
        cur = conn.cursor()
        if role == "Professeur":
            query = "SELECT nom, prenom FROM EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.PROFESSEUR WHERE courriel = %s"
        elif role == "Étudiant":
            query = "SELECT nom, prenom FROM EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.ETUDIANT WHERE courriel = %s"
        cur.execute(query, (email,))
        return cur.fetchone()  # Retourne (nom, prenom)
    finally:
        conn.close()

# Titre de la page
st.title("Étudier à L'INTELEV")

# Initialiser les états de session pour la connexion
if "is_professor_logged_in" not in st.session_state:
    st.session_state.is_professor_logged_in = False
if "is_student_logged_in" not in st.session_state:
    st.session_state.is_student_logged_in = False
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None
if "captured_voice" not in st.session_state:
    st.session_state.captured_voice = None

# Définir une fonction de déconnexion
def logout():
    st.session_state.is_professor_logged_in = False
    st.session_state.is_student_logged_in = False
    st.session_state.professor_name = None
    st.session_state.student_name = None
    st.session_state.captured_image = None
    st.session_state.captured_voice = None
    st.experimental_set_query_params(rerun="1")

# Vérifier si un professeur ou un étudiant est connecté
if st.session_state.is_professor_logged_in:
    st.success(f"Bienvenue Professeur à l'INTELEV, {st.session_state.professor_name}.")
    professor_interface(st.session_state.professor_id)
    if st.button("Déconnexion"):
        logout()

elif st.session_state.is_student_logged_in:
    st.success(f"Bienvenue Étudiant à l'INTELEV, {st.session_state.student_name}!")
    student_interface(st.session_state.student_id)
    if st.button("Déconnexion"):
        logout()

else:
    # Afficher l'interface de connexion/inscription
    option = st.radio("Choisissez une option", ("Se connecter", "S'inscrire"), index=0)

    if option == "Se connecter":
        col1, col2 = st.columns(2)

        # Section Professeur
        with col1:
            st.header("Professeur à l'INTELEV.")
            email = st.text_input("Courriel Personnel *", key="prof_email")
            password = st.text_input("Mot de passe *", type='password', key="prof_password")
            
            if st.button("Se connecter", key="login_prof"):
                result = verify_login(email, password, "Professeur")
                if result:
                    st.session_state.is_professor_logged_in = True
                    professor_name = get_user_name(email, "Professeur")
                    st.session_state.professor_name = f"{professor_name[0]} {professor_name[1]}"
                    st.session_state.professor_id = email
                    st.experimental_set_query_params(rerun="1")
                else:
                    st.error("Courriel ou mot de passe invalide pour les professeurs.")

        # Section Étudiant avec choix de reconnaissance
        with col2:
            st.header("Étudiant de l'INTELEV.")
            email_student = st.text_input("Courriel Personnel *", key="student_email")
            nip = st.text_input("NIP *", type='password', key="student_password")

            # Choix du type de reconnaissance
            recognition_type = st.radio("Choisissez le type de reconnaissance :", ("Faciale", "Vocale"))

            # Gestion de la capture en fonction du type de reconnaissance
            if recognition_type == "Faciale":
                picture_webcam = st.camera_input("Capturez votre visage pour la vérification")
                if picture_webcam:
                    st.session_state.captured_image = picture_webcam
                    st.write("Image capturée avec succès.")
                    st.image(st.session_state.captured_image)
            else:
                captured_voice_file = st.file_uploader("Téléchargez un enregistrement vocal pour la vérification", type=["wav", "mp3"])
                if captured_voice_file:
                    st.session_state.captured_voice = captured_voice_file
                    st.write("Enregistrement vocal chargé avec succès.")

            # Vérifiez l'authentification et lancez la reconnaissance choisie
            if st.button("Se connecter", key="login_student"):
                if email_student and nip:
                    result = verify_login(email_student, nip, "Étudiant")
                    if result:
                        st.write("Connexion réussie pour l'étudiant.")
                        
                        # Récupérer l'ID numérique de l'étudiant pour `student_id`
                        student_id = get_student_id(email_student)
                        
                        if student_id:
                            st.session_state.student_id = student_id
                            student_name = get_user_name(email_student, "Étudiant")
                            st.session_state.student_name = f"{student_name[0]} {student_name[1]}"

                            if recognition_type == "Faciale" and st.session_state.captured_image:
                                verification_result = verify_face(st.session_state.student_id, st.session_state.captured_image)
                                st.write(f"Résultat de la vérification faciale : {verification_result}")

                                if verification_result:
                                    st.session_state.is_student_logged_in = True
                                    st.write("Reconnaissance faciale réussie. Connexion à l'interface étudiant.")
                                    st.experimental_set_query_params(rerun="1")
                                else:
                                    st.error("Échec de la reconnaissance faciale.")

                            elif recognition_type == "Vocale" and st.session_state.captured_voice:
                                verification_result = verify_voice(st.session_state.student_id, st.session_state.captured_voice)
                                st.write(f"Résultat de la vérification vocale : {verification_result}")

                                if verification_result:
                                    st.session_state.is_student_logged_in = True
                                    st.write("Reconnaissance vocale réussie. Connexion à l'interface étudiant.")
                                    st.experimental_set_query_params(rerun="1")
                                else:
                                    st.error("Échec de la reconnaissance vocale.")
                            else:
                                st.error("Veuillez fournir une image ou un enregistrement vocal pour la vérification.")
                        else:
                            st.error("Impossible de récupérer l'ID de l'étudiant.")
                    else:
                        st.error("Courriel ou NIP invalide.")
                else:
                    st.error("Veuillez remplir tous les champs.")

    elif option == "S'inscrire":
        signup_form()
