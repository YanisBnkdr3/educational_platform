import face_recognition
import base64
import numpy as np
import io

def verify_face(student_id, captured_image):
    try:
        stored_encoding = np.load(f"encodings/{student_id}.npy")
    except FileNotFoundError:
        return False

    # Processus de vérification faciale
    image_data = np.array(bytearray(captured_image.read()), dtype=np.uint8)
    img = face_recognition.load_image_file(io.BytesIO(image_data))
    face_locations = face_recognition.face_locations(img)
    
    if face_locations:
        captured_encoding = face_recognition.face_encodings(img, face_locations)[0]
        return face_recognition.compare_faces([stored_encoding], captured_encoding)[0]
    else:
        return False
