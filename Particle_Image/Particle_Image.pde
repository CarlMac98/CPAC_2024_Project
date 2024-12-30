import java.util.concurrent.*;
import processing.video.*;
import oscP5.*;
import netP5.*;
import themidibus.*; //Import the library

MidiBus myBus; // The MidiBus
boolean oldMove;


OscP5 oscP5;
NetAddress myRemoteLocation;

Capture video;
PImage img;
ParticleSystem ps;
boolean move = false;
boolean debug = false;
int numThreads = Runtime.getRuntime().availableProcessors();
ExecutorService executor;
FlowField flowfield;
int oldPitch = 0;
Cluster cl1, cl2;
ArrayList<Cluster> clusters;

void setup() {
  oldMove = false;
  MidiBus.list();
  
  size(1280, 720);
  clusters = new ArrayList<Cluster>();
  blendMode(MULTIPLY);
  //fullScreen();
  println(numThreads);
  video = new Capture(this, width, height);
  video.start();
  executor = Executors.newFixedThreadPool(numThreads);
  //loadPixels();
  video.loadPixels();
  /* start oscP5, listening for incoming messages at port 12000 */
  oscP5 = new OscP5(this, 5008);

  /* myRemoteLocation is a NetAddress. a NetAddress takes 2 parameters,
   * an ip address and a port number. myRemoteLocation is used as parameter in
   * oscP5.send() when sending osc packets to another computer, device,
   * application. usage see below. for testing purposes the listening port
   * and the port of the remote location address are the same, hence you will
   * send messages back to this sketch.
   */
  myRemoteLocation = new NetAddress("127.0.0.1", 2346);
  flowfield = new FlowField(1, 3, 7);

  // Inizializza il sistema di particelle usando i pixel del video invece di img
  ps = new ParticleSystem();
  for (int x = 0; x < width; x++) {
    for (int y = 0; y < height; y++) {
      ps.addParticle(video.pixels[x + y * width], x, y);
    }
  }
  cl1 = new Cluster(100, 200, 200);
  clusters.add(cl1);
  cl2 = new Cluster(600, 200, 200);
  clusters.add(cl2);
  myBus = new MidiBus(new MidiBus(), 0, 5);
}

// Resto del codice rimane invariato...

void draw() {
  background(0);
  //println(frameRate);
  if (video.available()) { // Controlla se ci sono nuovi frame disponibili
    video.read();        // Aggiorna il frame della webcam
  }

  video.loadPixels();
  //flowfield.update();

  if (debug) flowfield.display();
  
  // Mantieni la manipolazione dei pixel se necessario
  if (move) {
    //ps.applyForce();
    //image(video, 0, 0);
    ps.ff(flowfield, 0, width*height, clusters);
    for (int x = 0; x < width; x++) {
      for (int y = 0; y < height; y++) {
        ps.changeColor(video.pixels[x + y * width], y + x * height);
      }
    }
  } else {
    for (int x = 0; x < video.width; x++) {
      for (int y = 0; y < video.height; y++) {
        ps.changeColor(video.pixels[x + y * video.width], y + x * video.height);
        //ps.changePosition(ps.positions.get(y + x * video.height), y + x * video.height);
        ps.toPos(y + x * video.height);
      }
    }
  }

  ps.run();
}

void mousePressed() {
  move = !move;
  //println(move);
  sendMidi();
  if(move){
    flowfield = new FlowField(1, floor(random(3, 5)), floor(random(6, 8)));
  }
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
    GroupPeople.x = random(0, width);
    GroupPeople.y = random(0, height);
  }
}

/* incoming osc message are forwarded to the oscEvent method. */
void oscEvent(OscMessage theOscMessage) {
  /* print the address pattern and the typetag of the received OscMessage */
  print("### received an osc message.");
  print(" addrpattern: " + theOscMessage.addrPattern());
  if (theOscMessage.addrPattern().equals("/cluster")) {
    println(theOscMessage.typetag());
    if (theOscMessage.typetag().equals("T")){
      move = true;
      sendMidi();
    }
    else {
      move = false;
      sendMidi();
    }
  } else if (theOscMessage.addrPattern().equals("/center")) {
    println(theOscMessage.get(0).floatValue() + ", " + theOscMessage.get(1).floatValue());
    GroupPeople.x = theOscMessage.get(0).floatValue() * width;
    GroupPeople.y = theOscMessage.get(1).floatValue() * height;
  }
}

void sendMidi() {
  int channel = 2;
  int pitch;
  int velocity = 100;
  
  if (oldMove == false && move == true){
    pitch = floor(random(80, 90));
    myBus.sendNoteOn(channel, pitch, velocity); // Send a Midi noteOn
    myBus.sendNoteOn(channel, pitch + 3, velocity);
    myBus.sendNoteOn(channel, pitch + 6, velocity);
    oldPitch = pitch;
    oldMove = move;
  } if(oldMove == true && move == false){
    myBus.sendNoteOff(channel, oldPitch, velocity); // Send a Midi nodeOff
    myBus.sendNoteOff(channel, oldPitch + 3, velocity);
    myBus.sendNoteOff(channel, oldPitch + 6, velocity);
    oldMove = move;
  }
  //delay(1000);
  int number = 0;
  int value = 90;

  myBus.sendControllerChange(channel, number, value); // Send a controllerChange
}

void noteOn(int channel, int pitch, int velocity) {
  // Receive a noteOn
  println();
  println("Note On:");
  println("--------");
  println("Channel:"+channel);
  println("Pitch:"+pitch);
  println("Velocity:"+velocity);
}

void noteOff(int channel, int pitch, int velocity) {
  // Receive a noteOff
  println();
  println("Note Off:");
  println("--------");
  println("Channel:"+channel);
  println("Pitch:"+pitch);
  println("Velocity:"+velocity);
}

void controllerChange(int channel, int number, int value) {
  // Receive a controllerChange
  println();
  println("Controller Change:");
  println("--------");
  println("Channel:"+channel);
  println("Number:"+number);
  println("Value:"+value);
}

void delay(int time) {
  int current = millis();
  while (millis () < current+time) Thread.yield();
}
