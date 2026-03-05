from class_agent import Agent
# ============================================
# CLASSE FISH (Poisson)
# ============================================

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

# ============================================
# CLASSE SIMULATION
# ============================================

class Simulation:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.agents = []
        self.afficher_perception = False
        self.afficher_stats = True
        self.paused = False

    def initialiser(self, nb_agents=10, type_agent=Agent):
        """Initialise avec un type d'agent spécifique"""
        self.agents = []
        for i in range(nb_agents):
            if type_agent == Fish:
                # Fish n'a besoin que de x, y
                self.ajouterFish(random(self.largeur), random(self.hauteur))
            else:
                # Agent classique
                self.ajouterAgent(random(self.largeur), random(self.hauteur))
            
    def ajouterAgent(self, x, y):
        """Ajoute un Agent par défaut"""
        agent = Agent(x, y, random(-2, 2), random(-2, 2), 10, 50, 4, 0.1)
        self.agents.append(agent)
    
    def ajouterFish(self, x, y):
        """Ajoute un Fish"""
        fish = Fish(x, y)
        self.agents.append(fish)

    def executer(self):
        background(30)
        
        if self.afficher_stats:
            self._afficherStats()
            
        if self.paused:
            fill(255, 0, 0)
            textSize(30)
            text("PAUSE", self.largeur / 2 - 50, 50)
            for agent in self.agents:
                agent.afficher()
            return
        
        for agent in self.agents:
            agent.appliquerRegles(self.agents)
            agent.update()
            agent.afficher()
            if self.afficher_perception:
                self._afficherRayonPerception(agent)

            
    def reinitialiser(self):
        """Réinitialise la simulation en vidant tous les agents"""
        self.agents = []
        print("Simulation réinitialisée")
    
    def togglePause(self):
        """Active/désactive la pause"""
        self.paused = not self.paused
        print("Pause: {}".format(self.paused))
    
    def togglePerception(self):
        """Active/désactive l'affichage des rayons de perception"""
        self.afficher_perception = not self.afficher_perception
        print("Affichage perception: {}".format(self.afficher_perception))
    
    def toggleStats(self):
        """Active/désactive l'affichage des statistiques"""
        self.afficher_stats = not self.afficher_stats
        print("Affichage stats: {}".format(self.afficher_stats))
    
    def getNbAgents(self):
        """Retourne le nombre d'agents dans la simulation"""
        return len(self.agents)
    
    def getVitesseMoyenne(self):
        """Calcule et retourne la vitesse moyenne de tous les agents"""
        if len(self.agents) == 0:
            return 0
        
        total = 0
        for agent in self.agents:
            total += agent.vel.mag()
        
        return total / len(self.agents)
    
    def _afficherStats(self):
        """Affiche les statistiques de la simulation"""
        fill(255)
        textSize(14)
        text("Nombre d'agents: {}".format(self.getNbAgents()), 10, 20)
        text("FPS: {:.1f}".format(frameRate), 10, 40)
        text("Vitesse moyenne: {:.2f}".format(self.getVitesseMoyenne()), 10, 60)
        text("", 10, 80)
        
        # Instructions
        textSize(12)
        fill(200)
        text("R: Reset | P: Pause | V: Perception | S: Stats", 10, self.hauteur - 20)
    
    def _afficherRayonPerception(self, agent):
        """Affiche le rayon de perception d'un agent avec son champ de vision"""
        angle_agent = agent.vel.heading()
        
        # Dessiner le champ de vision (arc)
        noFill()
        stroke(100, 255, 100, 80)
        strokeWeight(2)
        
        # Arc pour le champ de vision
        arc(
            agent.pos.x, agent.pos.y,
            agent.perception * 2, agent.perception * 2,
            angle_agent - agent.champ_vision / 2,
            angle_agent + agent.champ_vision / 2
        )
        
        # Lignes pour les limites du champ de vision
        stroke(100, 255, 100, 60)
        angle_debut = angle_agent - agent.champ_vision / 2
        angle_fin = angle_agent + agent.champ_vision / 2
        
        line(
            agent.pos.x, agent.pos.y,
            agent.pos.x + cos(angle_debut) * agent.perception,
            agent.pos.y + sin(angle_debut) * agent.perception
        )
        line(
            agent.pos.x, agent.pos.y,
            agent.pos.x + cos(angle_fin) * agent.perception,
            agent.pos.y + sin(angle_fin) * agent.perception
        )
        
        noStroke()

# ============================================
# MAIN
# ============================================

sim = None

def setup():
    size(800, 600)
    global sim
    sim = Simulation(width, height)
    
    # Initialiser avec des Fish 
    sim.initialiser(30, Fish)
    
    print("Simulation démarrée avec des Fish")
    print("Clic gauche: Ajouter un poisson")
    print("Clic droit: Ajouter un oiseau")

def draw():
    sim.executer()

def mousePressed():
    if mouseButton == LEFT:
        # Ajouter un poisson
        sim.ajouterFish(mouseX, mouseY)
        print("Fish ajouté - Total: {}".format(len(sim.agents)))
    elif mouseButton == RIGHT:
        # Ajouter un oiseau
        sim.ajouterAgent(mouseX, mouseY)
        print("Agent ajouté - Total: {}".format(len(sim.agents)))
    
        
def keyPressed():
    if key=='r' or key=='R':
        sim.reinitialiser()
    elif key == 'v' or key == 'V':
        sim.togglePerception()
    elif key == 's' or key == 'S':
        sim.toggleStats()
    elif key == 'p' or key == 'P':
        sim.togglePause()
    
