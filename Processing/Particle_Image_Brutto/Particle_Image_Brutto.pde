import java.util.concurrent.*;
import processing.video.*;

Capture video;
PImage img;
ParticleSystem ps;
boolean move = false;
boolean debug = false;
int numThreads = Runtime.getRuntime().availableProcessors();
ExecutorService executor;
FlowField flowfield;
int n, m;
BlackPixelData blackPixelData;


void setup() {
    size(1280, 720);
    n = 3;
    m = 2;
    blackPixelData = new BlackPixelData(width, height);
    blackPixelData.calculateBlackPixels();
    //fullScreen();
    println(numThreads);
    video = new Capture(this, width, height);
    video.start();
    executor = Executors.newFixedThreadPool(numThreads);
    //loadPixels();
    video.loadPixels();
    flowfield = new FlowField(20);
    
    // Inizializza il sistema di particelle usando i pixel del video invece di img
    ps = new ParticleSystem();
    for (int x = 0; x < width; x++) {
        for (int y = 0; y < height; y++) {
            ps.addParticle(video.pixels[x + y * width], x, y);
        }
    }
}

// Resto del codice rimane invariato...

void draw() {
  background(0);
  //blendMode(SCREEN);
  println(frameRate);
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
        ps.toGo();
        for (int x = 0; x < width; x++) {
          for (int y = 0; y < height; y++) {
            ps.changeColor(video.pixels[x + y * width], y + x * height);
        }
  }
    }
    else{
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
    debug = !debug;
  }
}
