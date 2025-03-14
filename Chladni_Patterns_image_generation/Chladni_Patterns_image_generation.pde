int n = 20;
int m = 20;
float threshold = 0.1;  // Adjust this threshold to better highlight the nodal lines

void setup() {
  size(1280, 720);
  noLoop();   // Draw the pattern only once
}

void draw() {
  background(0);
  loadPixels();
  // Loop over every pixel
  for (int a = 4; a < n; a++) {
    for (int b = a; b < m; b++) {
      if(a==b) continue;
      for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
          // Map pixel coordinates (i, j) to a normalized coordinate system [-1, 1]
          float x = map(i, 0, width, -1, 1);
          float y = map(j, 0, height, -1, 1);

          // Compute the Chladni function value
          float val = chladni(a, b, x, y);

          // If the function is close to zero, set the pixel to white, otherwise black.
          // This highlights the nodal lines.
          if (abs(val) < threshold) {
            pixels[j * width + i] = color(255);
          } else {
            pixels[j * width + i] = color(0);
          }
        }
      }
      updatePixels();
      saveFrame("chladni_" + a +"_" + b +".png");
    }
  }
  noLoop();
}

float chladni(float nn, float mm, float x, float y) {
  float L = 2;
  return cos(nn * PI * x / L) * cos(mm * PI * y / L) - cos(mm * PI * x / L) * cos(nn * PI * y / L);
}
