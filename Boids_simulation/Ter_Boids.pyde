# ============================================
# CLASSE AGENT
# ============================================

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
        self.acc.add(self.gererBords())
    
    def gererBords(self):
        """Gère le comportement de l'agent aux bords de l'écran"""
        # Wrap around
        evitement = PVector(0, 0)
        distance_securite = self.taille * 7
        if self.pos.x < distance_securite:
            diff = PVector(1, 0)
            diff.mult(sqrt((distance_securite - self.pos.x) / distance_securite))
            evitement.add(diff)
        if self.pos.x > width - distance_securite:
            diff = PVector(-1, 0)
            diff.mult(sqrt((self.pos.x - (width - distance_securite)) / distance_securite))
            evitement.add(diff)
        if self.pos.y < distance_securite:
            diff = PVector(0, 1)
            diff.mult(sqrt((distance_securite - self.pos.y) / distance_securite))
            evitement.add(diff)
        if self.pos.y > height - distance_securite:
            diff = PVector(0, -1)
            diff.mult(sqrt((self.pos.y - (height - distance_securite)) / distance_securite))
            evitement.add(diff)
        return evitement

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
# CLASSE RECTANGLE
# ============================================
class Rectangle:
    def __init__(self, x, y, hauteur, longueur):
        #creer un rectangle
        self.x =x
        self.y = y
        self.hauteur = hauteur
        self.longueur = longueur
    
    def contenir(self, point):
        #verifie si le point est dans le rectangle
        return (point.pos.x >= self.x-self.longueur) and (point.pos.x <= self.x + self.longueur) and (point.pos.y >= self.y-self.hauteur) and (point.pos.y <= self.y + self.hauteur) 

    def intersects(self, rang):
        #verifie si le rectangle entre en collision avec l'autre rectangle rang
        return not (rang.x - rang.longueur > self.x + self.longueur or 
                rang.x + rang.longueur < self.x - self.longueur or 
                rang.y + rang.hauteur < self.y - self.hauteur or 
                rang.y - rang.hauteur > self.y + self.hauteur)

# ============================================
# CLASSE QUADTREE
# ============================================
            
class QuadTree:
    def __init__(self, limite, nb_max_point):
        self.limite = limite
        self.nb_max_point = nb_max_point
        self.liste_points = []
        self.diviser = False 
        
    def subdivide(self):
        #coupe un rectangle en 4 parties
        x = self.limite.x
        y = self.limite.y
        w = self.limite.longueur
        h = self.limite.hauteur
        HG = Rectangle(x - (w/2), y - (h/2), h/2, w/2)
        HD = Rectangle(x + (w/2), y - (h/2), h/2, w/2)
        BG = Rectangle(x - (w/2), y + (h/2), h/2, w/2)
        BD = Rectangle(x + (w/2), y + (h/2), h/2, w/2)
        self.HautGauche = QuadTree(HG, self.nb_max_point)
        self.HautDroite = QuadTree(HD, self.nb_max_point)
        self.BasGauche = QuadTree(BG, self.nb_max_point)
        self.BasDroite = QuadTree(BD, self.nb_max_point)
        self.diviser = True
        
    def inserer(self, point):
        #ajoute le point a la liste des points
        if not self.limite.contenir(point):
            return False
        if self.diviser:
            self._inserer_dans_enfant(point)
            return
        if len(self.liste_points) < self.nb_max_point:
            self.liste_points.append(point)
            return True
        self.subdivide()
        anciens = self.liste_points
        self.liste_points = []
        for p in anciens:
            self._inserer_dans_enfant(p)
        self._inserer_dans_enfant(point)
                #self.HautGauche.inserer(point)
                #self.HautDroite.inserer(point)
                #self.BasGauche.inserer(point)
                #self.BasDroite.inserer(point)
    
    def _inserer_dans_enfant(self, point):
        #ajoutes le point à la liste des points dans la zone
            if self.HautGauche.limite.contenir(point):                    
                self.HautGauche.inserer(point)
                return True
            elif self.HautDroite.limite.contenir(point):
                self.HautDroite.inserer(point)
                return True
            elif self.BasGauche.limite.contenir(point):
                self.BasGauche.inserer(point)
                return True
            elif self.BasDroite.limite.contenir(point):
                self.BasDroite.inserer(point)
                return True
    
    def query(self, rang, trouve):
        #renvoie les points que se situent dans le rectangle rang
        if self.limite.intersects(rang):
            return
        for p in self.liste_points:
            if rang.contenir(p):
                trouve.append(p)
        if self.diviser:
            self.HautGauche.query(rang, trouve)
            self.HautDroite.query(rang, trouve)
            self.BasGauche.query(rang, trouve)
            self.BasDroite.query(rang, trouve)
        return trouve
    
    def afficher(self):
        #affiche les rectangles et les points
        stroke(255)
        strokeWeight(1)
        noFill()
        rect(self.limite.x, self.limite.y, self.limite.longueur*2, self.limite.hauteur*2)
        if self.diviser:
            self.HautGauche.afficher()
            self.HautDroite.afficher()
            self.BasGauche.afficher()
            self.BasDroite.afficher()
        for p in self.liste_points:
            strokeWeight(4)
            point(p.pos.x,p.pos.y)

# ============================================
# CLASSE SIMULATION
# ============================================

class Simulation:
    def __init__(self, largeur, hauteur, limite, nb_agent_max):
        global Rectangle
        global QuadTree
        self.largeur = largeur
        self.hauteur = hauteur
        self.agents = []
        self.afficher_perception = False
        self.afficher_stats = True
        self.paused = False
        self.limite = limite
        self.QT = QuadTree(self.limite, nb_agent_max)

    def initialiser(self, nb_agents=10, type_agent=Agent):
        """Initialise avec un type d'agent spécifique"""
        rectMode(CENTER)
        self.agents = []
        for i in range(nb_agents):
            if type_agent == Fish:
                # Fish n'a besoin que de x, y
                self.ajouterFish(random(self.largeur), random(self.hauteur))
            else:
                # Agent classique
                self.ajouterAgent(random(self.largeur), random(self.hauteur))
        self.QT.afficher()
            
    def ajouterAgent(self, x, y):
        """Ajoute un Agent par défaut"""
        agent = Agent(x, y, random(-2, 2), random(-2, 2), 10, 50, 4, 0.1)
        self.agents.append(agent)
        self.QT.inserer(agent)
    
    def ajouterFish(self, x, y):
        """Ajoute un Fish"""
        fish = Fish(x, y)
        self.agents.append(fish)
        self.QT.inserer(fish)

    def executer(self):
        background(30)
        self.QT=QuadTree(self.limite, 10)
        for agent in self.agents:
            self.QT.inserer(agent)
        self.QT.afficher()
        stroke(0,255,0)
        rectMode(CENTER)
        
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
    size(800, 800)
    global sim
    global Rectangle
    global QuadTree
    sim = Simulation(width, height, Rectangle(400,400,400,400), 10)
    
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
    
