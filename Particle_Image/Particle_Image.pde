import java.util.concurrent.*;
import processing.video.*;
import oscP5.*;
import netP5.*;
//import themidibus.*; //Import the library

//MidiBus myBus; // The MidiBus
boolean oldMove;
float inc;
float scaling;


OscP5 oscP5;
NetAddress myRemoteLocation;

Capture video;
PImage img, bck;
ParticleSystem ps;
boolean move = false;
boolean debug = false;
int numThreads = 1;//Runtime.getRuntime().availableProcessors();
ExecutorService executor;
FlowField flowfield;
int oldPitch = 0;
Cluster cl1, cl2;
ArrayList<Cluster> clusters;
int w, h;
PGraphics pg, backGround;


void setup() {
  w = 1280;
  h = 720;
  oldMove = false;
  //MidiBus.list();

  size(1280, 720);
  clusters = new ArrayList<Cluster>();
  //blendMode(MULTIPLY);

  //fullScreen();
  
  pg = createGraphics(w, h);
  backGround = createGraphics(w, h);
  inc = 0.005;
  scaling = 0.01;
  noiseDetail(12);
  back();

  println(numThreads);
  video = new Capture(this, w, h);
  video.start();
  executor = Executors.newFixedThreadPool(numThreads);
  //loadPixels();
  video.loadPixels();
  /* start oscP5, listening for incoming messages at port 12000 */
  oscP5 = new OscP5(this, 5008);


  myRemoteLocation = new NetAddress("127.0.0.1", 2346);
  flowfield = new FlowField(15, 3, 7);

  // Inizializza il sistema di particelle usando i pixel del video invece di img
  ps = new ParticleSystem();

  int groupSize = 3; // 3x3 block
  for (int x = 1; x < video.width; x += groupSize) {
    for (int y = 1; y < video.height; y += groupSize) {
      if (x < video.width && y < video.height) {
        int index = x + y * video.width;
        ps.addParticle(video.pixels[index], x, y);
      }
    }
  }

  cl1 = new Cluster(100, 200, 200);
  clusters.add(cl1);
  //cl2 = new Cluster(600, 200, 200);
  //clusters.add(cl2);
  //back2();
  //bck = new PImage();
}


void draw() {


  pg.beginDraw();
  pg.background(0);

  //println(frameRate);
  if (video.available()) { // Controlla se ci sono nuovi frame disponibili
    video.read();        // Aggiorna il frame della webcam
  }


  video.loadPixels();
  //flowfield.update();

  if (debug) flowfield.display();

  // Mantieni la manipolazione dei pixel se necessario
  if (move) {

    // Update the cluster position using scaled mouse coordinates
    Cluster cl = clusters.get(0);
    cl.x = mouseX * ((float) w / width);
    cl.y = mouseY * ((float) h / height);

    // Use the particle list size (not video.width*video.height)
    int numParticles = ps.particles.size();
    ps.ff(flowfield, 0, numParticles, clusters); // update particles using flow field

    // Now update the color for each particle based on its current position
    for (int i = 0; i < numParticles; i++) {
      Pparticle p = ps.particles.get(i);
      int vx = constrain((int)p.pos.x, 0, video.width - 1);
      int vy = constrain((int)p.pos.y, 0, video.height - 1);
      int vidIndex = vx + vy * video.width;
      ps.changeColor(video.pixels[vidIndex], i);
      // Note: We do NOT call ps.toPos(i) here, so the particle continues following the flow
    }
    //back();
  } else {
    // When not in move mode, you can update both color and target position
    int numParticles = ps.particles.size();
    for (int i = 0; i < numParticles; i++) {
      Pparticle p = ps.particles.get(i);
      int vx = constrain((int)p.pos.x, 0, video.width - 1);
      int vy = constrain((int)p.pos.y, 0, video.height - 1);
      int vidIndex = vx + vy * video.width;
      ps.changeColor(video.pixels[vidIndex], i);
      ps.toPos(i);  // reset particle toward its stored target position
    }
  }



  //pg.image(backGround, 0, 0, pg.width, pg.height);
  //ps.run();
  pg.loadPixels();
  ps.run(pg);


  pg.updatePixels();



  // Finish drawing on the off-screen buffer
  pg.endDraw();

  // Draw the off-screen buffer to the main display, scaling it up to full screen

  image(pg, 0, 0, width, height);
}

void mousePressed() {
  move = !move;
  //println(move);
  //sendMidi();
}

void exit() {
  executor.shutdown();
  super.exit();
}

void captureEvent(Capture video) {
  video.read();
}

void keyPressed() {
  if (key == ' ') {
    for (Cluster cl : clusters) {
      cl.x = random(0, video.width);
      cl.y = random(0, video.height);
    }
    //GroupPeople.x = random(0, width);
    //GroupPeople.y = random(0, height);
  }
  if (key == 'c' && move) {
    flowfield = new FlowField(10, floor(random(3, 5)), floor(random(6, 8)));
  }
}

/* incoming osc message are forwarded to the oscEvent method. */
void oscEvent(OscMessage theOscMessage) {
  /* print the address pattern and the typetag of the received OscMessage */
  print("### received an osc message.");
  print(" addrpattern: " + theOscMessage.addrPattern());
  if (theOscMessage.addrPattern().equals("/cluster")) {
    println(theOscMessage.typetag());
    if (theOscMessage.typetag().equals("T")) {
      move = true;
      //sendMidi();
    } else {
      move = false;
      //sendMidi();
    }
  } else if (theOscMessage.addrPattern().equals("/center")) {
    println(theOscMessage.get(0).floatValue() + ", " + theOscMessage.get(1).floatValue());
    GroupPeople.x = theOscMessage.get(0).floatValue() * video.width;
    GroupPeople.y = theOscMessage.get(1).floatValue() * video.height;
  }
}

void delay(int time) {
  int current = millis();
  while (millis () < current+time) Thread.yield();
}

void back() {
  float offsetY = 0;
  backGround.beginDraw();
  backGround.loadPixels();
  backGround.background(0);
  // Loop over all pixels.
  for (int y = 0; y < backGround.height; y++) {
    float offsetX = 0;
    for (int x = 0; x < backGround.width; x++) {
      // Use the same offsets for all pixels in this frame.
      float val1 = noise(offsetX, offsetY, frameCount * scaling) * 255;
      float val2 = noise(offsetX + 100, offsetY + 100, frameCount * scaling) * 255;
      float val3 = noise(offsetX + 200, offsetY + 200, frameCount * scaling) * 255;
      backGround.pixels[x + y * backGround.width] = color(val1, val2, val3, 127);

      offsetX += inc;
    }
    offsetY += inc;
  }
  backGround.updatePixels();
  backGround.endDraw();
}

void back2() {
  backGround.beginDraw();
  //backGround.loadPixels();

  bck = video.copy();
  bck.filter(GRAY);
  bck.filter(BLUR, 10);
  bck.filter(INVERT);
  backGround.image(bck, 0, 0, backGround.width, backGround.height);

  //backGround.updatePixels();
  backGround.endDraw();
}
