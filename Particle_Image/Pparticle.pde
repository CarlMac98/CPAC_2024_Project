class Pparticle {
  color c;
  PVector pos;
  PVector vel;
  PVector acc;
  float maxSpeed;
  float maxForce;

  Pparticle(color c, float x, float y) {
    this.c = c;
    pos = new PVector(x, y);
    acc = new PVector(0, 0);
    vel = new PVector(0, 0);
    maxSpeed = random(7, 12);
    maxForce = random(0.5, 1);
  }

  void update() {
    vel.add(acc);
    pos.add(vel);
    //pos.x = constrain(pos.x, 0, width - 1);
    //pos.y = constrain(pos.y, 0, height - 1);
    acc.mult(0);
    vel.mult(0.95);// Aggiungo un po' di attrito
    //borders();
  }

  void applyForce(PVector f) {
    //PVector force = f.copy();
    //force.add(random(-1, 1), random(-1, 1));
    //acc.add(force);
    acc.add(f);
  }

  void getColor(color col) {
    this.c = col;
  }

  //void seek(PVector target) {
  //  PVector desired = PVector.sub(target, pos);
  //  desired.setMag(maxSpeed);
  //  PVector steer = PVector.sub(desired, vel);
  //  steer.limit(maxForce);

  //  applyForce(steer);

  //}

  void arrive(PVector target) {
    PVector desired = PVector.sub(target, pos);  // A vector pointing from the position to the target
    float d = desired.mag();
    // Scale with arbitrary damping within 100 pixels
    if (d < 10) {
      float m = map(d, 0, 10, 0, maxSpeed);
      desired.setMag(m);
    } else {
      desired.setMag(maxSpeed);
    }

    // Steering = Desired minus Velocity
    PVector steer = PVector.sub(desired, vel);
    steer.limit(maxForce);  // Limit to maximum steering force

    applyForce(steer);
  }

  void follow(FlowField flow) {
    // What is the vector at that spot in the flow field?

    //if (dist(pos.x, pos.y, GroupPeople.x, GroupPeople.y) >= GroupPeople.r) {
    PVector desired = flow.lookup(pos);
    // Scale it up by maxspeed
    desired.mult(maxSpeed);
    // Steering is desired minus velocity
    PVector steer = PVector.sub(desired, vel);
    steer.limit(maxForce).add(random(-1, 1), random(-1, 1));  // Limit to maximum steering force
    applyForce(steer);
    //}
  }

  void borders() {
    int tresh = 1;
    if (pos.x < 0) pos.x = video.width - tresh;
    if (pos.y < 0) pos.y = video.height - tresh;
    if (pos.x > video.width) pos.x = 0 + tresh;
    if (pos.y > video.height) pos.y = 0 + tresh;
  }
}
