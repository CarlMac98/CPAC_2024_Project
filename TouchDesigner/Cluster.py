class Cluster:
    def __init__(self, id, center):
        self.id = id
        self.center = center
        self.alive = True
        self.scale = 0.1

    def update(self, center):
        self.center = center

    def kill(self):
        self.alive = False

    def check_scaling(self):
        if self.alive and self.scale < 1:
            self.scale += 0.1

        if not self.alive and self.scale > 0:
            self.scale -= 0.1

    def completely_dead(self):
        return self.scale <= 0