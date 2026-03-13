import class_rectangle.py

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
    
    def limite_taille(self):
        w = self.limite.longueur
        h = self.limite.hauteur
        if w>50 and h>50:
            return True
        return False
        
    def inserer(self, point):
        #ajoute le point a la liste des points
        if not self.limite.contenir(point):
            return False
        if self.diviser:
            return self._inserer_dans_enfant(point)
        if len(self.liste_points) < self.nb_max_point:
            self.liste_points.append(point)
            return True
        if self.limite_taille():
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
        if not self.limite.intersects(rang):
            #Si les bords du rectangle rang ne croisent pas ceux d'un des rectangles du quadtree
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
