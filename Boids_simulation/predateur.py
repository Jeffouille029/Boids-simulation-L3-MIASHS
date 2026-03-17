# -*- coding: utf-8 -*-
from agent import Agent

class Predateur(Agent):
    def __init__(self, x, y):
        Agent.__init__(self, x, y, 
            vx=random(-2, 2), 
            vy=random(-2, 2),
            taille=15,          # plus grand que les autres
            perception=150,     # voit loin
            maxVit=4,           # plus rapide
            maxForce=0.3)
    
    def afficher(self):
        """Triangle rouge pour le prédateur"""
        angle = self.vel.heading() + radians(90)
        
        fill(255, 0, 0)  # rouge
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


    # ---------------------------
    # Fonction utilitaire : carré de la distance
    # ---------------------------
    def dist2(self, v1, v2):
        dx = v1.x - v2.x
        dy = v1.y - v2.y
        return dx*dx + dy*dy

    # ---------------------------
    # Chasse les agents
    # ---------------------------
    def chasser(self, agents):
        """Se dirige vers l'agent le plus proche"""
        cible = None
        dist_min2 = self.perception * self.perception  # on compare les carrés

        for agent in agents:
            if type(agent) is not Predateur:
                d2 = self.dist2(self.pos, agent.pos)
                if d2 < dist_min2:
                    dist_min2 = d2
                    cible = agent

        if cible is not None:
            desired = PVector.sub(cible.pos, self.pos)
            desired.normalize()
            desired.mult(self.maxVit)
            steer = PVector.sub(desired, self.vel)
            steer.limit(self.maxForce)
            return steer

        return PVector(0, 0)

    # ---------------------------
    # Mange les agents trop proches
    # ---------------------------
    def manger(self, agents):
        """Mange les agents trop proches"""
        DIST_MANGER2 = (self.taille * 2) ** 2  # carré de la distance pour manger

        for agent in agents[:]:
            if type(agent) is not Predateur:
                d2 = self.dist2(self.pos, agent.pos)
                if d2 < DIST_MANGER2:
                    agents.remove(agent)

    # ---------------------------
    # Applique les règles
    # ---------------------------
    def appliquerRegles(self, agents):
        chasse = self.chasser(agents)
        wand = self.calculerWandering()

        if chasse.mag() > 0:
            chasse.mult(2.0)  # il y a une proie, on chasse
            self.acc.add(chasse)
        else:
            wand.mult(1.0)    # pas de proie, on erre
            self.acc.add(wand)

    
