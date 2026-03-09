class Boid:

    def __init__(self, x, y):
        self.position = PVector(x, y)
        self.velocity = PVector.random2D()
        self.velocity.mult(random(2,3))
        self.acceleration = PVector(0,0)

        self.maxSpeed = 3
        self.maxForce = 0.2
        self.perception = 60

        self.bloque = False
        self.perceptionPredateur = 120  # distance de fuite

    def flock(self, boids, predateur):

        if self.bloque:
            return

        align = self.alignement(boids)
        coh = self.cohesion(boids)
        sep = self.separation(boids)
        bord = self.evitementBords()
        fuite = self.fuirPredateur(predateur)  # <-- fonction fuite

        # Pondération
        align.mult(1.0)
        coh.mult(0.8)
        sep.mult(1.5)
        bord.mult(2.0)
        fuite.mult(3.0)  # priorité très forte

        self.acceleration.add(align)
        self.acceleration.add(coh)
        self.acceleration.add(sep)
        self.acceleration.add(bord)
        self.acceleration.add(fuite)

# FUITE PROGRESSIVE ANTI-VIBRATION
    def fuirPredateur(self, predateur):

        steering = PVector(0,0)
        d = PVector.dist(self.position, predateur.position)

        self.panique = False

        if d < self.perceptionPredateur and d > 0:

            self.panique = True

            diff = PVector.sub(self.position, predateur.position)
            diff.normalize()

            # Force progressive selon distance
            intensite = map(d, 0, self.perceptionPredateur,
                           self.maxForce*3, 0)

            diff.mult(intensite)

            steering = diff
            steering.limit(self.maxForce*3)

        return steering


    def update(self):

        if not self.bloque:
            self.velocity.add(self.acceleration)
            self.velocity.limit(self.maxSpeed)
            self.position.add(self.velocity)

        self.acceleration.mult(0)

    # --------------------------------------
    def alignement(self, boids):
        steering = PVector(0,0)
        total = 0

        for other in boids:
            d = PVector.dist(self.position, other.position)
            if other != self and d < self.perception:
                steering.add(other.velocity)
                total += 1

        if total > 0:
            steering.div(total)
            steering.setMag(self.maxSpeed)
            steering.sub(self.velocity)
            steering.limit(self.maxForce)

        return steering

    def cohesion(self, boids):
        steering = PVector(0,0)
        total = 0

        for other in boids:
            d = PVector.dist(self.position, other.position)
            if other != self and d < self.perception:
                steering.add(other.position)
                total += 1

        if total > 0:
            steering.div(total)
            steering.sub(self.position)
            steering.setMag(self.maxSpeed)
            steering.sub(self.velocity)
            steering.limit(self.maxForce)

        return steering

    def separation(self, boids):
        steering = PVector(0,0)
        total = 0

        for other in boids:
            d = PVector.dist(self.position, other.position)
            if other != self and d < self.perception/2 and d > 0:
                diff = PVector.sub(self.position, other.position)
                diff.div(d)
                steering.add(diff)
                total += 1

        if total > 0:
            steering.div(total)
            steering.setMag(self.maxSpeed)
            steering.sub(self.velocity)
            steering.limit(self.maxForce)

        return steering

    def evitementBords(self):

        steering = PVector(0,0)
        distanceActivation = MARGE

        dG = self.position.x
        dD = width - self.position.x
        dH = self.position.y
        dB = height - self.position.y

        if dG < distanceActivation:
            force = map(dG, 0, distanceActivation, self.maxForce*3, 0)
            steering.x += force

        if dD < distanceActivation:
            force = map(dD, 0, distanceActivation, self.maxForce*3, 0)
            steering.x -= force

        if dH < distanceActivation:
            force = map(dH, 0, distanceActivation, self.maxForce*3, 0)
            steering.y += force

        if dB < distanceActivation:
            force = map(dB, 0, distanceActivation, self.maxForce*3, 0)
            steering.y -= force

        steering.limit(self.maxForce*3)
        return steering

    def display(self):

        angle = self.velocity.heading()

        pushMatrix()
        translate(self.position.x, self.position.y)
        rotate(angle)

        if self.bloque:
            fill(120)  # gris si bloqué
        else:
            fill(0,150,255)

        noStroke()

        beginShape()
        vertex(12,0)
        vertex(-12,6)
        vertex(-12,-6)
        endShape(CLOSE)

        popMatrix()
