import face_recognition
import io

from signup import verify_face  # Assurez-vous que le module est correctement importé
from PIL import Image
import io

# Charger une image d'exemple pour simuler la vérification faciale
with open("WIN_20241111_16_26_51_Pro.jpg", "rb") as image_file:  # Remplacez par le chemin de l'image de test
    captured_image = io.BytesIO(image_file.read())

# Remplacez 'student_id' par l'ID de l'étudiant pour qui l'encodage est sauvegardé
student_id = '203'  # Exemple d'ID

# Exécuter la vérification faciale
verification_result = verify_face(student_id, captured_image, tolerance=0.6)
print("Résultat de la vérification faciale :", verification_result)
