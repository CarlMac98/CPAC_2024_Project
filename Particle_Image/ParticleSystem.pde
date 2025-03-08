class ParticleSystem {
  ArrayList<Pparticle> particles;
  ArrayList<PVector> positions;
  boolean insideAnyCircle;
  PImage copy;
  ParticleSystem() {
    particles = new ArrayList();
    positions = new ArrayList();
    insideAnyCircle = false;
    copy = new PImage();
  }

  void run(PGraphics pg) {
    if (move) {
      copy = video.copy();
      copy.filter(GRAY);
      //copy.filter(POSTERIZE, 3);
      copy.filter(BLUR, 8);
      copy.loadPixels();
    }
    // Dividi le particelle in gruppi per il multithreading
    int particlesPerThread = particles.size() / numThreads;
    ArrayList<Future<?>> futures = new ArrayList<>();

    for (int i = 0; i < numThreads; i++) {
      final int startIndex = i * particlesPerThread;
      final int endIndex = (i == numThreads - 1) ? particles.size() : (i + 1) * particlesPerThread;

      futures.add(executor.submit(new Runnable() {
        public void run() {
          updateParticleRange(startIndex, endIndex, pg);
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
  }

  void updateParticleRange(int start, int end, PGraphics pg) {
    for (int i = start; i < end; i++) {
      Pparticle p = particles.get(i);
      p.update();

      // Use the particle's current position as the anchor (or use the stored original grid position,
      // whichever fits your intention)
      int baseX = (int) p.pos.x;
      int baseY = (int) p.pos.y;

      // For each pixel in the 3x3 block, use the corresponding pixel from the video image.
      // Here, (dx,dy) spans -1 to 1.
      for (int dx = -1; dx <= 1; dx++) {
        for (int dy = -1; dy <= 1; dy++) {
          int drawX = baseX + dx;   // coordinate in pg (and assumed same resolution as video)
          int drawY = baseY + dy;
          // For the video pixel, you might want to use the same coordinates.
          int sampleX = constrain(baseX + dx, 0, video.width - 1);
          int sampleY = constrain(baseY + dy, 0, video.height - 1);
          int vidIndex = sampleX + sampleY * video.width;

          // Check that our drawing position is within the pg bounds.
          if (drawX >= 0 && drawX < pg.width && drawY >= 0 && drawY < pg.height) {
            boolean useVideo = !move;  // if not in move mode, always use video
            if (move) {
              // When in move mode, check all clusters.
              for (Cluster cluster : clusters) {
                // If the pixel is inside any cluster, use the video pixel.
                if (dist(drawX, drawY, cluster.x, cluster.y) <= cluster.r) {
                  useVideo = true;
                  break;
                }
              }
            }
            if (useVideo) {
              pg.pixels[drawY * pg.width + drawX] = video.pixels[vidIndex];
            } else {
              pg.pixels[drawY * pg.width + drawX] = copy.pixels[vidIndex];
            }
          }
        }
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
      insideAnyCircle = false;
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
