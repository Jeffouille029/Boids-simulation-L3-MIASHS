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
