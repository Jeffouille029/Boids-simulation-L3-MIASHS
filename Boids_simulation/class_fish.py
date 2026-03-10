from class_agent import Agent 
class Fish(Agent):
    """
    Classe Fish héritant d'Agent.
    Comportement de banc de poissons
    """
    
    def __init__(self, x, y):
        vx = random(-2, 2)
        vy = random(-2, 2)
        taille = 10
        perception = 50
        maxVit = 4
        maxForce = 0.1
        
        # Appel du constructeur parent
        super(Fish, self).__init__(x, y, vx, vy, taille, perception, maxVit, maxForce)
        
        # Couleur spécifique aux poissons
        self.couleur = color(random(100, 150), random(150, 255), random(200, 255))
    
    def afficher(self):
        """Affichage en forme de poisson """
        angle = self.vel.heading()
        
        fill(self.couleur)
        noStroke()
        pushMatrix()
        translate(self.pos.x, self.pos.y)
        rotate(angle)
        
        # Corps du poisson (ellipse allongée)
        ellipse(0, 0, self.taille * 2.5, self.taille * 1.2)
        
        # Queue triangulaire
        triangle(
            -self.taille * 1.2, 0,
            -self.taille * 1.8, -self.taille * 0.6,
            -self.taille * 1.8, self.taille * 0.6
        )
        
        popMatrix()
    
    def appliquerRegles(self, agents):
        """Poids optimisés pour une ressemblance avec un banc de poissons"""
        sep = self.calculerSeparation(agents)
        ali = self.calculerAlignement(agents)
        coh = self.calculerCohesion(agents)
        wand = self.calculerWandering()
        
        sep.mult(1.2)   # Distance
        ali.mult(1.0)   # Alignement 
        coh.mult(1.1)   # Cohésion 
        wand.mult(1.0)  # Errance
        
        self.acc.add(sep)
        self.acc.add(ali)
        self.acc.add(coh)
        self.acc.add(wand)
