import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, date, time
from connect import create_snowflake_connection
import connect

# Function to fetch exams with actual dates
def fetch_exams(professor_id):
    conn = create_snowflake_connection()
    cursor = conn.cursor()
    try:
        # Fetch exams with their start and end dates, along with additional details for hover info
        cursor.execute("""
            SELECT TITRE AS "Exam", DESCRIPTION, TOTAL_POINTS, DATE_DEBUT AS "Start", DATE_FIN AS "End"
            FROM EXAMEN
            WHERE PROFESSEUR_ID = %s
        """, (professor_id,))
        exams = cursor.fetchall()
        exams_df = pd.DataFrame(exams, columns=["Exam", "Description", "Total Points", "Start", "End"])
        return exams_df
    finally:
        cursor.close()
        conn.close()

def validate_time(time_str):
    """Validates that the time is in HH:MM format."""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        return time_obj
    except ValueError:
        return None

def professor_interface(professor_id):
    st.title("Module Professeur")

    # Option selection in sidebar
    option = st.sidebar.selectbox("Options", ["Vue du calendrier", "Créer un examen", "Gérer les examens", "Créer une classe", "Gérer les classes"])

    if option == "Vue du calendrier":
        st.header("Vue du calendrier des examens")
        exams_data = fetch_exams(professor_id)

        if not exams_data.empty:
            exams_data['Color'] = pd.Categorical(exams_data['Exam']).codes
            fig = px.timeline(
                exams_data,
                x_start="Start",
                x_end="End",
                y="Exam",
                color="Exam",
                hover_data={
                    "Description": True,
                    "Total Points": True,
                    "Start": False,
                    "End": False,
                },
                title="Calendrier des examens"
            )
            fig.update_yaxes(categoryorder="total ascending")
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Examen",
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False
            )
            fig.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Aucun examen prévu.")

    elif option == "Créer un examen":
        st.header("Préparation de l'examen")
        exam_title = st.text_input("Titre de l'examen")
        exam_description = st.text_area("Description de l'examen")
        exam_type = st.selectbox("Choisissez le type d'examen", ["QCM", "Essay"])
        total_points = st.number_input("Total des points de l'examen", min_value=1)

        # Date picker and manual time input fields
        start_date = st.date_input("Date de début de l'examen", value=datetime.today())
        start_time_str = st.text_input("Heure de début (HH:MM)")
        end_date = st.date_input("Date de fin de l'examen", value=datetime.today())
        end_time_str = st.text_input("Heure de fin (HH:MM)")
        
        
        

        if exam_type == "QCM":
            num_questions = st.number_input("Nombre de questions", min_value=1, step=1)

            # Create dynamic input fields for the number of questions specified
            questions_data = []
            for i in range(num_questions):
                st.subheader(f"Question {i + 1}")
                question = st.text_area(f"Entrez votre question ici (Question {i + 1})")
                choices = st.text_area(f"Entrez les choix possibles (séparés par des virgules) pour la question {i + 1}")
                correct_answer = st.text_input(f"Entrez la réponse correcte pour la question {i + 1}")
                points_per_question = st.number_input(f"Points pour la question {i + 1}", min_value=0, step=1)

                questions_data.append({
                    'question': question,
                    'choices': choices.split(','),
                    'correct_answer': correct_answer,
                    'points': points_per_question
                })
                
                


        if st.button("Enregistrer l'examen"):
            if exam_title and exam_description:
                start_time = validate_time(start_time_str)
                end_time = validate_time(end_time_str)

                if start_time and end_time:
                    start_datetime = datetime.combine(start_date, start_time)
                    end_datetime = datetime.combine(end_date, end_time)
                    connect.save_exam(exam_title, exam_description, total_points, professor_id)
                    st.success("Examen enregistré avec succès!")
                else:
                    st.error("Les heures doivent être au format valide (HH:MM).")
            else:
                st.error("Veuillez entrer le titre et la description de l'examen.")

    elif option == "Gérer les examens":
        st.header("Gérer les examens")
        exams = connect.get_professor_exams(professor_id)
        exam_names = [exam[1] for exam in exams]
        exam_selection = st.selectbox("Sélectionnez un examen à gérer", exam_names)

        if exam_selection:
            selected_exam = next(exam for exam in exams if exam[1] == exam_selection)
            exam_id = selected_exam[0]

            # Fetch classes associated with the professor
            classes = connect.get_professor_classes(professor_id)
            class_names = [c[1] for c in classes]
            selected_class_name = st.selectbox("Choisissez la classe", class_names)

            if selected_class_name:
                class_id = next(c[0] for c in classes if c[1] == selected_class_name)

                # Date picker and manual time input fields for scheduling
                start_date = st.date_input("Date de début de l'examen", value=datetime.today())
                start_time_str = st.text_input("Heure de début (HH:MM)")
                end_date = st.date_input("Date de fin de l'examen", value=datetime.today())
                end_time_str = st.text_input("Heure de fin (HH:MM)")

                # Update button
                if st.button("Mettre à jour la date de l'examen"):
                    start_time = validate_time(start_time_str)
                    end_time = validate_time(end_time_str)

                    if start_time and end_time:
                        start_datetime = datetime.combine(start_date, start_time)
                        end_datetime = datetime.combine(end_date, end_time)
                        connect.assign_exam_to_class(exam_id, class_id, start_datetime, end_datetime)
                        st.success("Date de l'examen mise à jour avec succès!")
                    else:
                        st.error("Les heures doivent être au format valide (HH:MM).")

    elif option == "Créer une classe":
        st.header("Création de classe")
        class_name = st.text_input("Nom de la classe")
        class_description = st.text_area("Description de la classe")
        if st.button("Créer la classe"):
            if class_name and class_description:
                connect.create_class(professor_id, class_name, class_description)
                st.success(f"Classe '{class_name}' créée avec succès!")
            else:
                st.error("Veuillez entrer un nom et une description de classe.")

    elif option == "Gérer les classes":
        st.header("Gestion des classes")
        classes = connect.get_professor_classes(professor_id)
        
        class_names = [f"{c[1]}" for c in classes]
        selected_class = st.selectbox("Sélectionnez une classe", class_names)

        if selected_class:
            class_id = [c[0] for c in classes if c[1] == selected_class][0]
            students_in_class = connect.get_students_in_class(class_id)

            st.subheader("Étudiants dans la classe")
            for student in students_in_class:
                st.write(f"{student[1]} {student[2]} (ID: {student[0]})")
                if st.button(f"Retirer {student[1]}", key=f"remove_{student[0]}"):
                    connect.remove_student_from_class(student[0], class_id)
                    st.success(f"{student[1]} retiré de la classe.")

            all_students = connect.get_all_students()
            students_not_in_class = [s for s in all_students if s not in students_in_class]
            
            st.subheader("Ajouter des étudiants à la classe")
            if students_not_in_class:
                student_to_add = st.selectbox("Sélectionnez un étudiant à ajouter", [(s[0], f"{s[1]} {s[2]}") for s in students_not_in_class], format_func=lambda x: x[1])
                if st.button("Ajouter l'étudiant"):
                    connect.add_student_to_class(student_to_add[0], class_id)
                    st.success(f"{student_to_add[1]} ajouté à la classe.")
            else:
                st.info("Tous les étudiants sont déjà dans cette classe.")