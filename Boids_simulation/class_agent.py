class Agent(object):
    def __init__(self, x, y, vx, vy, taille, perception, maxVit, maxForce):
        self.pos = PVector(x, y)
        self.vel = PVector(vx, vy)
        self.acc = PVector(0, 0)
        self.taille = taille
        self.perception = perception
        self.maxVit = maxVit
        self.maxForce = maxForce
        
        self.wander_theta = 0
        self.champ_vision = radians(270) 

    def update(self):
        # Mise à jour de la vitesse
        self.vel.add(self.acc)
        # Limiter la vitesse
        self.vel.limit(self.maxVit)
        # Mise à jour position
        self.pos.add(self.vel)
        # Reset accélération
        self.acc.mult(0)
        # Bords de l'écran
        self.gererBords()
    
    def gererBords(self):
        """Wrap around de l'écran"""
        if self.pos.x > width: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = width
        if self.pos.y > height: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = height

    def afficher(self):
        """Affichage par défaut"""
        #triangle orienté
        angle = self.vel.heading() + radians(90)
        
        fill(255, 200, 100)
        noStroke()
        pushMatrix()
        translate(self.pos.x, self.pos.y)
        rotate(angle)
        beginShape()
        vertex(0, -self.taille)
        vertex(-self.taille/2, self.taille)
        vertex(self.taille/2, self.taille)
        endShape(CLOSE)
        popMatrix()

    def calculerWandering(self):
        # Rayon du cercle de wandering
        wander_r = 25 
        # Distance du cercle devant l'agent
        wander_d = 80
        # Changement maximal de direction
        change = 0.4
        
        self.wander_theta += random(-change, change)
        
        # Position du cercle devant l'agent
        circle_pos = self.vel.copy()
        circle_pos.normalize()
        circle_pos.mult(wander_d)
        circle_pos.add(self.pos)
        
        # Position cible sur le cercle
        h = self.vel.heading()
        circle_offset = PVector(wander_r * cos(self.wander_theta + h), wander_r * sin(self.wander_theta + h))
        target = PVector.add(circle_pos, circle_offset)
        
        # Force de direction vers la cible
        steer = PVector.sub(target, self.pos)
        steer.normalize()
        steer.mult(self.maxVit)
        steer.sub(self.vel)
        steer.limit(self.maxForce)
        
        return steer

    def estDansChampVision(self, autre):
        vers_autre = PVector.sub(autre.pos, self.pos)
        angle = PVector.angleBetween(self.vel, vers_autre)
        return angle < self.champ_vision / 2

    def calculerSeparation(self, agents):
        steer = PVector(0, 0)
        count = 0
        for other in agents:
            if type(other) is type(self):
                d = PVector.dist(self.pos, other.pos)
                if d > 0 and d < self.taille * 2:
                    diff = PVector.sub(self.pos, other.pos)
                    diff.normalize()
                    diff.div(d)
                    steer.add(diff)
                    count += 1
        
        if count > 0:
            steer.div(count)
        if steer.mag() > 0:
            steer.normalize()
            steer.mult(self.maxVit)
            steer.sub(self.vel)
            steer.limit(self.maxForce)
        return steer

    def calculerAlignement(self, agents):
        sum = PVector(0, 0)
        count = 0
        for other in agents:
            if type(other) is type(self):
                d = PVector.dist(self.pos, other.pos)
                if d > 0 and d < self.perception and self.estDansChampVision(other):
                    sum.add(other.vel)
                    count += 1
        
        if count > 0:
            sum.div(count)
            sum.normalize()
            sum.mult(self.maxVit)
            steer = PVector.sub(sum, self.vel)
            steer.limit(self.maxForce)
            return steer
        return PVector(0, 0)

    def calculerCohesion(self, agents):
        sum = PVector(0, 0)
        count = 0
        for other in agents:
            if type(other) is type(self):
                d = PVector.dist(self.pos, other.pos)
                if d > 0 and d < self.perception and self.estDansChampVision(other):
                    sum.add(other.pos)
                    count += 1
        
        if count > 0:
            sum.div(count)
            desired = PVector.sub(sum, self.pos)
            desired.normalize()
            desired.mult(self.maxVit)
            steer = PVector.sub(desired, self.vel)
            steer.limit(self.maxForce)
            return steer
        return PVector(0, 0)

    def appliquerRegles(self, agents):
        """Comportement neutre par défaut"""
        sep = self.calculerSeparation(agents)
        ali = self.calculerAlignement(agents)
        coh = self.calculerCohesion(agents)
        wand = self.calculerWandering()
        
        #Poids neutres par défaut
        sep.mult(1.0)
        ali.mult(1.0)
        coh.mult(1.0)
        wand.mult(1.0)
        
        self.acc.add(sep)
        self.acc.add(ali)
        self.acc.add(coh)
        self.acc.add(wand)
