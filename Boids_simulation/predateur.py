# -*- coding: utf-8 -*-
from class_agent import Agent

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

    def chasser(self, agents):
        """Se dirige vers l'agent le plus proche"""
        cible = None
        dist_min = self.perception
        
        for agent in agents:
            if type(agent) is not Predateur:
                d = PVector.dist(self.pos, agent.pos)
                d2 = d * d
                if d2 < dist_min * dist_min:
                    dist_min = d
                    cible = agent
        
        if cible is not None:
            desired = PVector.sub(cible.pos, self.pos)
            desired.normalize()
            desired.mult(self.maxVit)
            steer = PVector.sub(desired, self.vel)
            steer.limit(self.maxForce)
            return steer
        
        return PVector(0, 0)

    
    def manger(self, agents):
        """Mange les agents trop proches"""
        for agent in agents[:]:
            if type(agent) is not Predateur:
                d = PVector.dist(self.pos, agent.pos)
                d2 = d * d
                DIST_MANGER = (self.taille * 2) * (self.taille * 2)
                if d2 < DIST_MANGER:
                    agents.remove(agent)
                
                
    def appliquerRegles(self, agents):
        chasse = self.chasser(agents)
        wand = self.calculerWandering()
    
        if chasse.mag() > 0:
            chasse.mult(2.0)  # il y a une proie, on chasse
            self.acc.add(chasse)
        else:
            wand.mult(1.0)    # pas de proie, on erre
            self.acc.add(wand)
