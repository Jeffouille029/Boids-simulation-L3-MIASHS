from Agent import Agent
from Fish import Fish
from Insect import Insect
from Dimulation import Simulation
from Rectangle import Rectangle
from QuadTree import QuadTree
from Predateur import Predateur


# ============================================
# MAIN
# ============================================

sim = None


def setup():
    size(800, 600)
    global sim
    sim = Simulation(width, height, Rectangle(400, 300, 300, 400), 10)

    # Initialiser avec des Fish 
    sim.initialiser(30, Fish)
    # initialisation predateur
    sim.ajouterPredateur(width/2, height/2) #Mettre cette ligne en commentaire quand calcul de performance
    
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
    
