import tensorflow as tf
import tensorflow_hub as hub  # type: ignore

# Carica il modello da TF Hub una sola volta in fase di importazione.
HUB_HANDLE = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
hub_module = hub.load(HUB_HANDLE)
print("Modello di style transfer caricato da TF Hub.")

def perform_style_transfer(content_image, style_image, output_image_size=384):
    """
    Esegue lo style transfer a partire da un'immagine di contenuto e una di stile.

    Parametri:
      content_image (tf.Tensor): Immagine di contenuto. Può essere un tensore di forma [H, W, 3]
                                 oppure [1, H, W, 3]. Se non contiene il batch, verrà aggiunto.
      style_image (tf.Tensor): Immagine di stile. Deve avere forma [H, W, 3] oppure [1, H, W, 3].
      output_image_size (int): Dimensione (altezza e larghezza) a cui ridimensionare l'immagine di contenuto.
                               Default è 384.

    Restituisce:
      tf.Tensor: Immagine stilizzata di forma [1, output_image_size, output_image_size, 3].
    """
    # Se le immagini non hanno la dimensione batch, le espande aggiungendo una dimensione.
    if len(content_image.shape) == 3:
        content_image = tf.expand_dims(content_image, axis=0)
    if len(style_image.shape) == 3:
        style_image = tf.expand_dims(style_image, axis=0)

    # Ridimensiona l'immagine di contenuto alla dimensione specificata.
    content_image = tf.image.resize(content_image, (output_image_size, output_image_size))
    # Ridimensiona l'immagine di stile a 256x256 (dimensione consigliata per il modello).
    style_image = tf.image.resize(style_image, (256, 256))

    # Applica un pooling medio all'immagine di stile per lisciarla.
    style_image = tf.nn.avg_pool(style_image, ksize=[1, 3, 3, 1], strides=[1, 1, 1, 1], padding='SAME')

    # Esegue il trasferimento di stile.
    outputs = hub_module(tf.constant(content_image), tf.constant(style_image))
    stylized_image = outputs[0]

    return stylized_image
