int xCount = 120;
int yCount = 120;

float n = 6;
float m = 3;
float randNM = 20;

Particle[] myParticles = new Particle[xCount*yCount];

void setup() {
  size(1200,1200,P2D);
  background(0);
  smooth();

  initParticle();
  shuffle();
}

void draw() {
  translate(width / 2, height / 2);
  scale(1.0 * width/2, 1.0 * height/2);
  background(0);

  noFill();
  stroke(255,180);
  strokeWeight(0.003);

  for (int i = 0; i < myParticles.length; i++) {
    myParticles[i].update();
    myParticles[i].display();
  }
}

void shuffle() {
  n = floor(random(randNM));
  m = floor(random(randNM));
  while (m == n) {
    m = floor(random(randNM));
  }
}

void initParticle() {
  int i = 0;
  for (int y = 0; y < yCount; y++) {
    for (int x = 0; x < xCount; x++) {
      myParticles[i] = new Particle();
      i++;
    }
  }
}

class Particle extends PVector {
  float x,y;
  float speed;

  Particle() {
    x = random(-1, 1);
    y = random(-1, 1);
    speed = 0.035;
  }

  void update() {
    float vibrationmax = 0.003;
    float vibrationX = random(-vibrationmax, vibrationmax);
    float vibrationY = random(-vibrationmax, vibrationmax);

    float amount = chladni(x, y);
    float randomNum = random(-0.2,0.5);

    if (amount >= 0) {
      if (chladni(x + vibrationmax, y) >= amount) {
        x = constrain(x - randomNum * amount * speed + vibrationX, -1, 1);
      } else {
        x = constrain(x + randomNum * amount * speed + vibrationX, -1, 1);
      }
      if (chladni(x, y + vibrationmax) >= amount) {
        y = constrain(y - randomNum * amount * speed + vibrationY, -1, 1);
      } else {
        y = constrain(y + randomNum * amount * speed + vibrationY, -1, 1);
      }

    } else {
      if (chladni(x + vibrationmax, y) <= amount) {
        x = constrain(x + randomNum * amount * speed + vibrationX, -1, 1);
      } else {
        x = constrain(x - randomNum * amount * speed + vibrationX, -1, 1);
      }
      if (chladni(x, y + vibrationmax) <= amount) {
        y = constrain(y + randomNum * amount * speed + vibrationY, -1, 1);
      } else {
        y = constrain(y - randomNum * amount * speed + vibrationY, -1, 1);
      }
    }
  }

  float chladni(float x, float y) {
    float L = 2;
    return cos(n * PI * x / L) * cos(m * PI * y / L) - cos(m * PI * x / L) * cos(n * PI * y / L);
  }

  void display() {
    point(x, y);
  }
}
