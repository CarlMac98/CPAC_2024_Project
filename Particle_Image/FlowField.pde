// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Flow Field Following

class FlowField {

  // A flow field is a two dimensional array of PVectors
  PVector[][] field;
  int cols, rows; // Columns and Rows
  int resolution; // How large is each "cell" of the flow field
  public int n;
  public int m;

  FlowField(int r, int nn, int mm) {
    resolution = r;
    // Determine the number of columns and rows based on sketch's width and height
    cols = width/resolution;
    rows = height/resolution;
    field = new PVector[cols][rows];
    m = nn;
    n = mm;
    init();
  }

  void init() {
    // Reseed noise so we get a new flow field every time
    //noiseSeed((int)random(10000));
    for (int i = 0; i < cols; i++) {
      //float theta = map(i, 0, cols, 0, TWO_PI* 4);
      for (int j = 0; j < rows; j++) {
        float value = chladni(i, j);
        if(value > -0.1 && value < 0.1) value = 0;
        //if (dist(i, j, 100, 200) < 200) value = 0;
        //println(value);
        float brightness = map(-value, -1, 1, -0.2, 0.2);
        PVector gradient = calculateGradient(i, j);
        // Normalize the gradient
        gradient.normalize();

        // Scale by brightness
        gradient.mult(brightness);
        field[i][j] = gradient.copy();
        // Polar to cartesian coordinate transformation to get x and y components of the vector
        /*if (i< cols/2) {
          field[i][j] = PVector.fromAngle(theta).add(2, 0).mult(2);
        } else {
          field[i][j] = PVector.fromAngle(theta).add(2, 0).mult(-2);
        }*/
      }
    }
  }

  void update() {
    for (int i = 0; i < cols; i++) {
      float gamma = map(i, 0, cols, 0, 10*TWO_PI);
      for (int j = 0; j < rows; j++) {
        //float theta = map(noise(xoff,yoff,zoff),0,1,0,TWO_PI);
        float theta = map(j, 0, rows, 0, 10*TWO_PI);
        // Make a vector from an angle
        field[i][j] = new PVector(cos(theta), sin(gamma));
      }
    }
  }
  float chladni(float x, float y) {
    
    float Ly = rows;
    float Lx = cols;
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
  // Draw every vector
  void display() {
    for (int i = 0; i < cols; i++) {
      for (int j = 0; j < rows; j++) {
        drawVector(field[i][j], i*resolution, j*resolution, resolution-2);
      }
    }
  }

  // Renders a vector object 'v' as an arrow and a position 'x,y'
  void drawVector(PVector v, float x, float y, float scayl) {
    pushMatrix();
    //float arrowsize = 4;
    // Translate to position to render vector
    translate(x, y);
    stroke(0, 150);
    // Call vector heading function to get direction (note that pointing up is a heading of 0) and rotate
    rotate(v.heading());
    // Calculate length of vector & scale it to be bigger or smaller if necessary
    float len = v.mag()*scayl;
    // Draw three lines to make an arrow (draw pointing up since we've rotate to the proper direction)
    line(0, 0, len, 0);
    //line(len,0,len-arrowsize,+arrowsize/2);
    //line(len,0,len-arrowsize,-arrowsize/2);
    popMatrix();
  }

  PVector lookup(PVector lookup) {
    int column = int(constrain(lookup.x/resolution, 0, cols-1));
    int row = int(constrain(lookup.y/resolution, 0, rows-1));
    return field[column][row].copy();
  }
}
