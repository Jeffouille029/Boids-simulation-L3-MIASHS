class Point:
    def __init__(self, x, y, boid=None):
        self.x = x
        self.y = y
        self.boid = boid


class Rectangle:
    def __init__(self, x, y, h, w):
        self.x = x
        self.y = y
        self.h = h
        self.w = w

    def contains(self, point):
        return (point.x >= self.x - self.w and
                point.x <= self.x + self.w and
                point.y >= self.y - self.h and
                point.y <= self.y + self.h)

    def intersects(self, other):
        return not (other.x - other.w > self.x + self.w or
                    other.x + other.w < self.x - self.w or
                    other.y - other.h > self.y + self.h or
                    other.y + other.h < self.y - self.h)


class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False

    def subdivide(self):
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.w / 2
        h = self.boundary.h / 2

        ne = Rectangle(x + w, y - h, h, w)
        nw = Rectangle(x - w, y - h, h, w)
        se = Rectangle(x + w, y + h, h, w)
        sw = Rectangle(x - w, y + h, h, w)

        self.northeast = QuadTree(ne, self.capacity)
        self.northwest = QuadTree(nw, self.capacity)
        self.southeast = QuadTree(se, self.capacity)
        self.southwest = QuadTree(sw, self.capacity)

        self.divided = True

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        else:
            if not self.divided:
                self.subdivide()

            return (self.northeast.insert(point) or
                    self.northwest.insert(point) or
                    self.southeast.insert(point) or
                    self.southwest.insert(point))

    def query(self, range_rect, found):
        if not self.boundary.intersects(range_rect):
            return

        for p in self.points:
            if range_rect.contains(p):
                found.append(p)

        if self.divided:
            self.northwest.query(range_rect, found)
            self.northeast.query(range_rect, found)
            self.southwest.query(range_rect, found)
            self.southeast.query(range_rect, found)


# ==========================================
# PARAMÈTRES
# ==========================================

boids = []
predateur = None
NB_BOIDS = 80
MARGE = 50

boids_elimines = 0
boids_crees = 0


# ==========================================
# SETUP
# ==========================================

def setup():
    global predateur
    size(900, 600)

    for i in range(NB_BOIDS):
        boids.append(Boid(random(width), random(height)))

    predateur = Predateur(width/2, height/2)


# ==========================================
# DRAW
# ==========================================

def draw():
    global boids_elimines, boids_crees

    background(240)

    # --------- Construire QuadTree ---------
    boundary = Rectangle(width/2, height/2, height/2, width/2)
    qt = QuadTree(boundary, 4)

    for b in boids:
        qt.insert(Point(b.position.x, b.position.y, b))

    # --------- BOIDS ---------
    for b in boids:
        b.flock(qt, predateur)
        b.update()
        b.display()

    # --------- PREDATEUR ---------
    predateur.chasser(qt)
    predateur.update()
    predateur.display()

    # --------- Compteurs ---------
    fill(0)
    textSize(18)
    text("Boids elimines : " + str(boids_elimines), 20, 25)
    text("Boids crees     : " + str(boids_crees), 20, 50)


# ==========================================
# CLASSE BOID
# ==========================================

class Boid:

    def __init__(self, x, y):
        self.position = PVector(x, y)
        self.velocity = PVector.random2D()
        self.velocity.mult(random(2,3))
        self.acceleration = PVector(0,0)

        self.maxSpeed = 3
        self.maxForce = 0.35
        self.perception = 60
        self.perceptionPredateur = 120
        self.marge = 50

    def flock(self, qt, predateur):
        align = self.alignement(qt)
        coh = self.cohesion(qt)
        sep = self.separation(qt)
        fuite = self.fuirPredateur(predateur)
        bords = self.eviterBords()

        self.acceleration.add(align.mult(0.5))
        self.acceleration.add(coh.mult(0.4))
        self.acceleration.add(sep.mult(1.0))
        self.acceleration.add(fuite.mult(2.0))
        self.acceleration.add(bords.mult(1.5))

    def alignement(self, qt):
        steering = PVector(0, 0)
        total = 0

        zone = Rectangle(self.position.x, self.position.y,
                     self.perception, self.perception)
        points = []
        qt.query(zone, points)

        for p in points:
            other = p.boid
            if other != self:
                d = PVector.dist(self.position, other.position)
                if d < self.perception:
                    steering.add(other.velocity)
                    total += 1

        if total > 0:
            steering.div(total)
            steering.normalize()
            steering.mult(self.maxSpeed)
            steering.sub(self.velocity)
            steering.limit(self.maxForce)

        return steering

    def cohesion(self, qt):
        steering = PVector(0, 0)
        total = 0

        zone = Rectangle(self.position.x, self.position.y,
                     self.perception, self.perception)
        points = []
        qt.query(zone, points)

        for p in points:
            other = p.boid
            if other != self:
                d = PVector.dist(self.position, other.position)
                if d < self.perception:
                    steering.add(other.position)
                    total += 1

        if total > 0:
            steering.div(total)
            steering.sub(self.position)
            steering.normalize()
            steering.mult(self.maxSpeed)
            steering.sub(self.velocity)
            steering.limit(self.maxForce)

        return steering

    def separation(self, qt):
        steering = PVector(0, 0)
        total = 0
        rayon = self.perception * 0.6

        zone = Rectangle(self.position.x, self.position.y, rayon, rayon)
        points = []
        qt.query(zone, points)

        for p in points:
            other = p.boid
            if other != self:
                d = PVector.dist(self.position, other.position)
                if 0 < d < rayon:
                    diff = PVector.sub(self.position, other.position)
                    diff.normalize()
                    diff.div(d)  # 🔥 plus ils sont proches, plus c'est fort
                    steering.add(diff)
                    total += 1

        if total > 0:
            steering.div(total)
            steering.setMag(self.maxSpeed)
            steering.sub(self.velocity)
            steering.limit(self.maxForce * 2)  # 🔥 séparation plus forte

        return steering
    
    def eviterBords(self):
        steering = PVector(0, 0)
        marge = self.marge

        # Gauche
        if self.position.x < marge:
            steering.x += (marge - self.position.x) / marge * self.maxForce
        # Droite
        elif self.position.x > width - marge:
            steering.x -= (self.position.x - (width - marge)) / marge * self.maxForce
        # Haut
        if self.position.y < marge:
            steering.y += (marge - self.position.y) / marge * self.maxForce
        # Bas
        elif self.position.y > height - marge:
            steering.y -= (self.position.y - (height - marge)) / marge * self.maxForce

        return steering

    def fuirPredateur(self, predateur):
        steering = PVector(0,0)
        d = PVector.dist(self.position, predateur.position)

        if d < self.perceptionPredateur and d > 0:
            diff = PVector.sub(self.position, predateur.position)
            diff.normalize()
            diff.mult(self.maxForce*3)
            steering = diff

        return steering

    def update(self):
        self.velocity.add(self.acceleration)
        self.velocity.limit(self.maxSpeed)
        self.position.add(self.velocity)
        self.acceleration.mult(0)
        
        if self.position.x < 0 or self.position.x > width:
            self.velocity.x *= -1

        if self.position.y < 0 or self.position.y > height:
            self.velocity.y *= -1

    def display(self):
        angle = self.velocity.heading()
        pushMatrix()
        translate(self.position.x, self.position.y)
        rotate(angle)
        fill(0,150,255)
        noStroke()
        beginShape()
        vertex(12,0)
        vertex(-12,6)
        vertex(-12,-6)
        endShape(CLOSE)
        popMatrix()


# ==========================================
# CLASSE PREDATEUR
# ==========================================

class Predateur:

    def __init__(self, x, y):
        self.position = PVector(x, y)
        self.velocity = PVector.random2D()
        self.acceleration = PVector(0,0)
        self.maxSpeed = 4
        self.maxForce = 0.3

    def chasser(self, qt):
        global boids, boids_elimines, boids_crees

        zone = Rectangle(self.position.x, self.position.y, 200, 200)
        points = []
        qt.query(zone, points)

        if not points:
            return

        cible_point = min(points, key=lambda p: PVector.dist(self.position, p.boid.position))

        cible = cible_point.boid
        distance = PVector.dist(self.position, cible.position)

    # --------- ELIMINATION ---------
        if distance < 15:     # distance de contact (ajuste si besoin)
            if cible in boids:
                boids.remove(cible)
                boids_elimines += 1
                
                # Création d’un nouveau boid
                while True:
                    x = random(width)
                    y = random(height)
                    if PVector.dist(PVector(x, y), self.position) > 150:
                        nouveau = Boid(x, y)
                        break
                boids.append(nouveau)
                boids_crees += 1
            return

    # --------- POURSUITE ---------
        desired = PVector.sub(cible.position, self.position)
        desired.setMag(self.maxSpeed)

        steer = PVector.sub(desired, self.velocity)
        steer.limit(self.maxForce)

        self.acceleration.add(steer)

    def update(self):
        self.velocity.add(self.acceleration)
        self.velocity.limit(self.maxSpeed)
        self.position.add(self.velocity)
        self.acceleration.mult(0)
        
        if self.position.x > width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = width
        if self.position.y > height:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = height

    def display(self):
        pushMatrix()
        translate(self.position.x, self.position.y)
        fill(120, 70, 20)
        noStroke()
        rectMode(CENTER)
        rect(0,0,70,30)
        popMatrix()
