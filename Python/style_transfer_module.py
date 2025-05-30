import tensorflow as tf
import tensorflow_hub as hub  # type: ignore

# Carica il modello da TF Hub una sola volta in fase di importazione.
HUB_HANDLE = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
hub_module = hub.load(HUB_HANDLE)
print("Modello di style transfer caricato da TF Hub.")

def load_image_from_path(image_path):
    img_raw = tf.io.read_file(image_path)
    img = tf.io.decode_image(img_raw, channels=3, dtype=tf.float32)
    return img


def perform_style_transfer(content_image_path, style_image_path, output_path, output_image_size=384):
    """
    Esegue lo style transfer a partire da un'immagine di contenuto e una di stile.

    Parametri:
      content_image_path (str): Percorso dell'immagine di contenuto.
      style_image_path (str): Percorso dell'immagine di stile.
      output_path (str): Percorso dove salvare l'immagine stilizzata.
      output_image_size (int): Dimensione (altezza e larghezza) per il ridimensionamento finale.

    Restituisce:
      None: salva direttamente l'immagine su disco.
    """
    # Carica le immagini di contenuto e stile
    content_img = load_image_from_path(content_image_path)
    style_img = load_image_from_path(style_image_path)

    # Salva dimensioni originali di content per il resize finale
    orig_shape = tf.shape(content_img)[0:2]

    # Aggiungi batch dimension se mancante
    content = tf.expand_dims(content_img, axis=0) if len(content_img.shape) == 3 else content_img
    style = tf.expand_dims(style_img, axis=0) if len(style_img.shape) == 3 else style_img

    # Ridimensiona per il modello
    content = tf.image.resize(content, (output_image_size, output_image_size))
    style = tf.image.resize(style, (256, 256))

    # Applica un pooling medio sullo stile
    style = tf.nn.avg_pool(style, ksize=[1, 3, 3, 1], strides=[1, 1, 1, 1], padding='SAME')

    # Esegue il trasferimento di stile
    stylized_outputs = hub_module(tf.constant(content), tf.constant(style))
    stylized = stylized_outputs[0]

    # Rimuove la dimensione del batch
    stylized = tf.squeeze(stylized, axis=0)

    # Ridimensiona allo shape originale di content_img
    stylized = tf.image.resize(stylized, orig_shape)

    # Salva su disco
    tf.keras.preprocessing.image.save_img(output_path, stylized)

# Esempio di utilizzo:
# perform_style_transfer('content.jpg', 'style.jpg', 'stylized.jpg', output_image_size=384)
