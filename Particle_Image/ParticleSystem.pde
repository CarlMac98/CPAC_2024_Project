class ParticleSystem {
  ArrayList<Pparticle> particles;
  ArrayList<PVector> positions;

  ParticleSystem() {
    particles = new ArrayList();
    positions = new ArrayList();
  }

  void run() {
    loadPixels();

    // Dividi le particelle in gruppi per il multithreading
    int particlesPerThread = particles.size() / numThreads;
    ArrayList<Future<?>> futures = new ArrayList<>();

    for (int i = 0; i < numThreads; i++) {
      final int startIndex = i * particlesPerThread;
      final int endIndex = (i == numThreads - 1) ? particles.size() : (i + 1) * particlesPerThread;

      futures.add(executor.submit(new Runnable() {
        public void run() {
          updateParticleRange(startIndex, endIndex);
        }
      }
      ));
    }

    // Attendi che tutti i thread completino
    for (Future<?> future : futures) {
      try {
        future.get();
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }

    updatePixels();
  }

  void updateParticleRange(int start, int end) {
    for (int i = start; i < end; i++) {
      Pparticle p = particles.get(i);
      p.update();

      // Aggiorna i pixel direttamente invece di usare point()
      int x = (int)p.pos.x;
      int y = (int)p.pos.y;
      if (x >= 0 && x < width && y >= 0 && y < height) {
        pixels[y * width + x] = p.c;
      }
    }
  }

  void addParticle(color c, float x, float y) {
    particles.add(new Pparticle(c, x, y));
    positions.add(new PVector(x, y));
  }

  void removeParticle(int i) {
    particles.remove(i);
  }

  void applyForce() {
    for (Pparticle p : particles) {
      PVector force = new PVector(random(-1, 1), random(-1, 1));
      p.applyForce(force);
    }
  }

  void changeColor(color c, int i) {
    Pparticle p = particles.get(i);
    p.getColor(c);
  }

  void changePosition(PVector loc, int i) {
    Pparticle p = particles.get(i);
    p.pos.mult(0);
    p.pos.add(loc);
    p.vel.mult(0);
  }

  void toPos(int i) {
    Pparticle p = particles.get(i);
    p.arrive(positions.get(i));
  }

  void ff(FlowField field, int  min, int max, ArrayList<Cluster> clusters) {
    for (int i = min; i<max; i++) {
      boolean insideAnyCircle = false;
      Pparticle p = particles.get(i);
      for (Cluster cluster : clusters) {
        if (dist(positions.get(i).x, positions.get(i).y, cluster.x, cluster.y) <= cluster.r) {
          insideAnyCircle = true;
          break; // No need to check further if already inside a circle
        }
      }
      if (insideAnyCircle) {
        p.arrive(positions.get(i)); // Behavior for being inside a circle
      } else {
        p.follow(field); // Behavior for being outside all circles
      }
    }
  }
}
