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
