import streamlit as st
import base64
import numpy as np
from connect import create_snowflake_connection
import face_recognition
import io
import os
from PIL import Image
import librosa
from pydub import AudioSegment


def save_voice_encoding(student_id, voice_file):
    # Convertir l'enregistrement en un format compatible
    audio = AudioSegment.from_file(voice_file, format="wav")
    audio.export(f"temp_audio.wav", format="wav")  # Sauvegarde temporaire pour traitement

    # Charger et extraire les caractéristiques vocales avec librosa
    y, sr = librosa.load("temp_audio.wav", sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc.T, axis=0)

    # Sauvegarder les caractéristiques vocales dans un fichier .npy avec le format ID_vocal.npy
    np.save(f"encodings/{student_id}_vocal.npy", mfcc_mean)
    print(f"Encodage vocal sauvegardé pour l'étudiant {student_id}.")
def verify_voice(student_id, captured_voice_file, tolerance=0.6):
    # Extraire les caractéristiques de l'enregistrement capturé
    y, sr = librosa.load(captured_voice_file, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean_captured = np.mean(mfcc.T, axis=0)

    # Charger les caractéristiques vocales enregistrées
    try:
        stored_encoding = np.load(f'encodings/{student_id}_vocal.npy')
    except FileNotFoundError:
        print(f"Fichier d'encodage vocal introuvable pour l'ID étudiant {student_id}.")
        return False

    # Calculer la distance entre les encodages capturés et enregistrés
    distance = np.linalg.norm(stored_encoding - mfcc_mean_captured)
    return distance < tolerance

# Sauvegarde de l'encodage facial
def save_face_encoding(student_id, image):
    image_data = image.getvalue()  # Récupérer le contenu binaire de l'image
    img = Image.open(io.BytesIO(image_data)).convert("RGB")  # Charger l'image en RGB
    img_array = np.array(img)

    face_encodings = face_recognition.face_encodings(img_array)
    if face_encodings:
        face_encoding = face_encodings[0]
        np.save(f"encodings/{student_id}_face.npy", face_encoding)
        print(f"Encodage facial sauvegardé pour l'étudiant {student_id}.")
    else:
        print("Aucun visage détecté dans l'image. Encodage non sauvegardé.")

# Vérification de la reconnaissance faciale
def verify_face(student_id, captured_image, tolerance=0.6):
    captured_image_bytes = io.BytesIO(captured_image.getvalue()).read()
    captured_image_array = face_recognition.load_image_file(io.BytesIO(captured_image_bytes))
    captured_encoding = face_recognition.face_encodings(captured_image_array)

    if not captured_encoding:
        print("Aucun encodage facial trouvé dans l'image capturée.")
        return False

    # Charger l'encodage facial stocké
    try:
        stored_encoding = np.load(f'encodings/{student_id}_face.npy')
    except FileNotFoundError:
        print(f"Fichier d'encodage facial introuvable pour l'ID étudiant {student_id}.")
        return False

    # Comparer les encodages avec une tolérance
    results = face_recognition.compare_faces([stored_encoding], captured_encoding[0], tolerance=tolerance)
    return results[0] if results else False

# Insertion des données d'étudiant dans la base de données
def insert_student_data(first_name, last_name, email, nip, code_permanent, photo=None, voice=None):
    conn = create_snowflake_connection()
    cur = conn.cursor()
    try:
        photo_data = base64.b64encode(photo.read()).decode('utf-8') if photo else None
        voice_data = base64.b64encode(voice.read()).decode('utf-8') if voice else None

        insert_query = """
            INSERT INTO EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.ETUDIANT (NOM, PRENOM, COURRIEL, NIP, CODE_PERMANENT, ENREGISTREMENT_VOCAL)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, (first_name, last_name, email, nip, code_permanent, voice_data))
        conn.commit()

        # Récupérer l'ID de l'étudiant basé sur l'email
        cur.execute("SELECT ETUDIANT_ID FROM EXAM_SYSTEM.ONLINE_EXAM_SCHEMA.ETUDIANT WHERE COURRIEL = %s", (email,))
        student_id = cur.fetchone()[0]
        print("Étudiant ajouté avec succès :", email)
        print("ID étudiant récupéré :", student_id)  # Débogage pour vérifier l'ID
        return student_id
    except Exception as e:
        print("Erreur lors de l'insertion :", e)
        return None
    finally:
        conn.close()

# Formulaire d'inscription avec capture d'image et enregistrement vocal
def signup_form():
    st.header("Créer un compte étudiant")
    first_name = st.text_input("Prénom")
    last_name = st.text_input("Nom")
    email = st.text_input("Courriel")
    nip = st.text_input("NIP", type="password")
    code_permanent = st.text_input("Code Permanent")

    picture_webcam = st.camera_input("Capturez une image")
    voice_file = st.file_uploader("Téléchargez un enregistrement vocal", type=["wav", "mp3"])

    if st.button("S'inscrire"):
        # Insérer les données dans la base de données et récupérer l'ID de l'étudiant
        student_id = insert_student_data(first_name, last_name, email, nip, code_permanent, picture_webcam, voice_file)
        
        if student_id:
            if picture_webcam:
                save_face_encoding(student_id, picture_webcam)
            if voice_file:
                save_voice_encoding(student_id, voice_file)
            st.success(f"Compte créé avec succès pour {first_name} {last_name}")
        else:
            st.error("Erreur lors de la création du compte.")

