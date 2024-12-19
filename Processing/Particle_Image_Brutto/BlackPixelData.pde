class BlackPixelData {
  int[] pixelArray; // Array per salvare i valori dei pixel in scala di grigi
  ArrayList<Integer> blackPxIdx; // Lista per salvare gli indici dei pixel neri
  int width, height;
  
  BlackPixelData(int width, int height) {
    this.width = width;
    this.height = height;
    pixelArray = new int[width * height]; // Inizializza l'array con le dimensioni dello schermo
    blackPxIdx = new ArrayList<Integer>(); // Inizializza la lista per gli indici dei pixel neri
  }
  
  void calculateBlackPixels() {
    background(255);
    loadPixels(); // Carica i pixel dell'immagine
    for (int i = 0; i < width; i++) {
      for (int j = 0; j < height; j++) {
        int index = i + j * width;
        if (chladni(i, j) > -0.05 && chladni(i, j) < 0.05) {
          pixels[index] = color(0); // Imposta il colore del pixel a nero
        } else {
          pixels[index] = color(255); // Imposta il colore del pixel a bianco
        }
      }
    }
    updatePixels(); // Aggiorna i pixel dell'immagine

    // Converti i valori dei pixel in scala di grigi e salva nell'array pixelArray
    for (int i = 0; i < pixels.length; i++) {
      color c = pixels[i];
      int gray = (int) (red(c) * 0.299 + green(c) * 0.587 + blue(c) * 0.114); // Converti in scala di grigi
      pixelArray[i] = gray;

      if (gray == 0) {
        blackPxIdx.add(i); // Aggiungi l'indice del pixel nero alla lista
      }
    }
  }
  
  float chladni(int x, int y) {
    float Ly = height;
    float Lx = width;
    return cos(n * PI * x / Lx) * cos(m * PI * y / Ly) - cos(m * PI * x / Lx) * cos(n * PI * y / Ly);
  }
}
