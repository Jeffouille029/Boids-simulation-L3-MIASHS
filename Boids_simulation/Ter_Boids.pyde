from class_agent import Agent
from class_fish import Fish
from class_simulation import Simulation

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
    
