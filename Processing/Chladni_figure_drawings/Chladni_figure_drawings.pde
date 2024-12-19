int n = 5;
int m = 1;
float step = 10; // Distance between vector samples

void setup() {
  size(600, 600);
  noLoop();
}

void draw() {
  background(255);
  for (int x = 1; x < width - 1; x += step) {
    for (int y = 1; y < height - 1; y += step) {
      // Calculate brightness and gradient
      float value = chladni(x, y);
      float brightness = map(value, -1, 1, 0, 255);
      PVector gradient = calculateGradient(x, y);
      // Normalize the gradient
      gradient.normalize();
      
      // Scale by brightness
      gradient.mult(brightness / 255.0);

      // Draw the vector
      stroke(0);
      strokeWeight(1);
      line(x, y, x + gradient.x * step, y + gradient.y * step);
    }
  }
}

float chladni(float x, float y) {
  float Ly = height;
  float Lx = width;
  return cos(n * PI * x / Lx) * cos(m * PI * y / Ly) - 
         cos(m * PI * x / Lx) * cos(n * PI * y / Ly);
}

PVector calculateGradient(int x, int y) {
  float delta = 1; // Small value for finite difference approximation

  // Partial derivative w.r.t x
  float dx = (chladni(x + delta, y) - chladni(x - delta, y)) / (2 * delta);

  // Partial derivative w.r.t y
  float dy = (chladni(x, y + delta) - chladni(x, y - delta)) / (2 * delta);

  return new PVector(dx, dy);
}
