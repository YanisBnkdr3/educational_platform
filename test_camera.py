import streamlit as st

st.title("Test de la Capture de la Caméra")

# Essayez de capturer une image avec la caméra
picture_webcam = st.camera_input("Capturez une image avec votre caméra")

# Vérifiez si l'image est capturée et affichez-la
if picture_webcam:
    st.write("Image capturée avec succès.")
    st.image(picture_webcam)
else:
    st.write("Aucune image capturée. Assurez-vous que la caméra fonctionne et est autorisée.")
