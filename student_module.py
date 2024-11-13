import streamlit as st
from connect import create_snowflake_connection  

# Function to fetch available classes from the database
def get_available_classes(student_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    classes = []

    try:
        cursor.execute(
            '''
            SELECT c.classe_id, c.nom
            FROM Classe c
            LEFT JOIN ClasseEtudiant ce ON c.classe_id = ce.classe_id AND ce.etudiant_id = %s
            WHERE ce.etudiant_id IS NULL  -- Fetch only classes not yet enrolled
            ''',
            (student_id,)
        )
        classes = cursor.fetchall()  # Fetch available classes
    finally:
        cursor.close()
        conn.close()

    return classes

# Function to enroll a student in a selected class
def enroll_student_in_class(student_id, class_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO ClasseEtudiant (etudiant_id, classe_id) VALUES (%s, %s)',
            (student_id, class_id)
        )
        conn.commit()  # Commit the transaction
        return True  # Enrollment success
    except Exception as e:
        st.error(f"Error during enrollment: {e}")  # Handle potential errors
        return False
    finally:
        cursor.close()
        conn.close()

# Function to manage the student interface
def student_interface(student_id):
    # Display a welcome message with the student's name
    student_name = st.session_state.student_name  # Retrieve the student's name
    st.title(f"Tableau de Bord Étudiant - Bienvenue, {student_name}!")

    st.success(f"Bienvenue, {student_name} à l'INTELEV!")  # Personalized welcome message

    # Sidebar options for the student module
    st.sidebar.title("Options Étudiant")
    option = st.sidebar.radio(
        "Sélectionnez une option",
        ("Passage d'examen en ligne", "Soumission du questionnaire", "Visualisation des résultats", "S'inscrire à une classe")
    )

    # Display the appropriate interface based on the selection
    if option == "Passage d'examen en ligne":
        st.header("Passage d'Examen en Ligne")
        st.write("Instructions pour l'examen :")
        st.write("1. Assurez-vous de ne pas ouvrir d'autres fenêtres ou navigateurs.")
        st.write("2. Minimiser les fenêtres est interdit.")
        st.write("3. Votre session est surveillée.")

        # Add example exam questions
        st.subheader("Questions :")
        question_1 = st.text_area("1. Décrivez l'importance de l'intelligence artificielle dans le monde moderne.")
        question_2 = st.text_area("2. Quelles sont les principales étapes d'une méthode agile ?")
        
        if st.button("Soumettre les réponses"):
            st.success("Réponses soumises avec succès !")
            # Add functionality to save responses

    elif option == "Soumission du questionnaire":
        st.header("Soumission du Questionnaire")
        st.write("Veuillez soumettre votre questionnaire rempli ci-dessous :")
        uploaded_file = st.file_uploader("Téléverser le fichier", type=["pdf", "docx", "txt"])
        
        if uploaded_file is not None:
            st.success("Questionnaire soumis avec succès !")
            # Add functionality to save the uploaded file

    elif option == "Visualisation des résultats":
        st.header("Résultats de vos examens")
        st.write("Vous pouvez visualiser vos résultats ici :")
        
        # Example results (to be dynamically fetched based on student data)
        st.subheader("Résultat pour l'examen d'Intelligence Artificielle :")
        st.write("Note obtenue : 18/20")
        st.write("Commentaires : Très bon travail, continuez ainsi !")

        st.subheader("Résultat pour l'examen de Méthodes Agiles :")
        st.write("Note obtenue : 15/20")
        st.write("Commentaires : Bonne compréhension, mais des améliorations sont possibles.")

    elif option == "S'inscrire à une classe":
        st.header("S'inscrire à une Classe")
        available_classes = get_available_classes(student_id)

        if available_classes:
            st.write("Classes disponibles :")
            for class_id, class_name in available_classes:
                if st.button(f"S'inscrire à {class_name}"):
                    if enroll_student_in_class(student_id, class_id):
                        st.success(f"Inscription réussie à la classe {class_name}!")
                    else:
                        st.error(f"Échec de l'inscription à la classe {class_name}.")
        else:
            st.write("Aucune classe disponible pour l'inscription.")
