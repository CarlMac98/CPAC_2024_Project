import sys
import os

# Add the directory containing style_transfer_module.py to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from style_transfer_module import perform_style_transfer
import tensorflow as tf
import matplotlib.pyplot as plt

# Carica o crea le tue immagini (qui un esempio di caricamento da file)
def load_image_from_path(image_path):
    img_raw = tf.io.read_file(image_path)
    img = tf.io.decode_image(img_raw, channels=3, dtype=tf.float32)
    return img

# Carica l'immagine di contenuto e l'immagine di stile
content_img = load_image_from_path(r"C:\Users\alice\Desktop\MAE\secondo anno\HACKATON\CPAC_2024_Project\style_transfer\golden_retriever.jpg")
style_img = load_image_from_path(r"C:\Users\alice\Desktop\MAE\secondo anno\HACKATON\CPAC_2024_Project\style_transfer\pablo_picasso012m.jpg")

# Esegui lo style transfer
stylized_img = perform_style_transfer(content_img, style_img, output_image_size=384)

# Visualizza l'immagine stilizzata (ricorda che la funzione restituisce un batch, perciò prendi il primo elemento)
plt.imshow(stylized_img[0])
plt.axis('off')
plt.title("Immagine Stilizzata")
plt.show()