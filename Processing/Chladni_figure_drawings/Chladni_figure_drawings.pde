int n, m;

void setup() {
  n = 4;
  m = 5;
  //size(800, 800);
  fullScreen();
  frameRate(30);
}
void draw(){
  background(255);
  for (int i = 0; i < width; i++) {
    for (int j = 0; j < height; j++) {
      strokeWeight(2);
      if(chladni(i, j) > -0.05 && chladni(i,j) < 0.05) point(i,j);
    }
  }
}

float chladni(int x, int y) {
  float Ly = height;
  float Lx = width;
  return cos(n * PI * x / Lx) * cos(m * PI * y / Ly) - cos(m * PI * x / Lx) * cos(n * PI * y / Ly);
}
