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


base_dir = os.getcwd()  # oppure os.path.dirname(__file__) se sei in uno script
style_path = os.path.abspath(os.path.join(base_dir, "TouchDesigner", "bicicletta.JPG"))
content_path = os.path.abspath(os.path.join(base_dir, "TouchDesigner", "TDMovieOut.0.png"))

content_img = load_image_from_path(content_path)
style_img = load_image_from_path(style_path)

# Esegui lo style transfer
stylized_img = perform_style_transfer(content_img, style_img, output_image_size=384)

# Rimuovi la dimensione del batch prima di ridimensionare
stylized_img_no_batch = tf.squeeze(stylized_img, axis=0)

# Ridimensiona l'immagine stilizzata per avere lo stesso formato della content_img
stylized_img_resized = tf.image.resize(stylized_img_no_batch, tf.shape(content_img)[0:2])

# Ripristina la dimensione del batch
stylized_img_resized = tf.expand_dims(stylized_img_resized, axis=0)

# Visualizza l'immagine stilizzata (ricorda che la funzione restituisce un batch, perciò prendi il primo elemento)
plt.imshow(stylized_img_resized[0])
plt.axis('off')
plt.title("Immagine Stilizzata")
plt.show()

# Salva l'immagine stilizzata
# output_path = r"C:\Users\alice\Downloads\stylized_image.jpg"
# tf.keras.preprocessing.image.save_img(output_path, stylized_img_resized[0])

# print(f"Immagine stilizzata salvata in: {output_path}")