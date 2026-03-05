from class_agent import Agent 

class Insect(Agent):
    """
    Classe Insect héritant d'Agent.
    Comportement de nuées d'insectes
    """
    
    def __init__(self, x, y):
        vx = random(-3, 3)
        vy = random(-3, 3)
        taille = 6
        perception = 40
        maxVit = 5
        maxForce = 0.3   
        super(Insect, self).__init__(x, y, vx, vy, taille, perception, maxVit, maxForce)
        
        # Paramètres du jitter
        self.jitter_force   = 1.8    
        self.jitter_offset  = random(1000)  
        self.impulse_timer  = 0      
        self.impulse_rate   = int(random(8, 20)) 
        self.couleur = color(random(180, 255), random(100, 160), random(0, 60))
    
    def calculerJitter(self):
        """
        Création force chaotique:
        - Bruit de Perlinuuuuu
        - Impulsions brusques périodiques
        """
        t = frameCount * 0.15 
        # Bruit de Perlin 2D
        nx = noise(self.jitter_offset, t) * 2 - 1
        ny = noise(self.jitter_offset + 100, t) * 2 - 1
        jitter = PVector(nx, ny)
        jitter.mult(self.jitter_force)
        self.impulse_timer += 1
        if self.impulse_timer >= self.impulse_rate:
            self.impulse_timer = 0
            self.impulse_rate  = int(random(8, 20)) 
            burst = PVector(random(-1, 1), random(-1, 1))
            burst.normalize()
            burst.mult(self.maxVit * 1.5)
            jitter.add(burst)
        
        jitter.limit(self.maxForce * 3)
        return jitter

    def afficher(self):
        """Affichage insecte : corps rond + ailes en ligne"""
        pushMatrix()
        translate(self.pos.x, self.pos.y)
        rotate(self.vel.heading())
        
        # Corps
        fill(self.couleur)
        noStroke()
        ellipse(0, 0, self.taille, self.taille)
        
        # Ailes
        stroke(self.couleur)
        strokeWeight(1)
        line(0, 0, -self.taille,  -self.taille * 0.8)
        line(0, 0, -self.taille,   self.taille * 0.8)
        
        noStroke()
        popMatrix()
        
    def appliquerRegles(self, agents):
        sep  = self.calculerSeparation(agents)
        ali  = self.calculerAlignement(agents)
        coh  = self.calculerCohesion(agents)
        jitt = self.calculerJitter()
        

        sep.mult(2.0)
        ali.mult(0.4)
        coh.mult(0.8)
        jitt.mult(1.5)
        
        self.acc.add(sep)
        self.acc.add(ali)
        self.acc.add(coh)
        self.acc.add(jitt)
