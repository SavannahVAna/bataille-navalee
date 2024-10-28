import random

class Batiment:
    def __init__(self, position: list[tuple[int, int]], life: int):
        self.position = position
        self.life = life

class Player:
    def __init__(self, environment : str, bat : list[Batiment]=[]):
        print("Initialisation du joueur...")
        self.grille = [[0 for _ in range(10)] for _ in range(10)]
        self.bateaux: list[Batiment] = []  # Liste pour stocker jusqu'à 5 bateaux
        self.taille_bateaux = [2, 3, 3, 4, 5]  # Tailles des bateaux
        if len(bat) ==0:
            self.placer_bateaux_aleatoires()
        print("Initialisation terminée.")
        self.environment = environment

    def placer_bateaux_aleatoires(self):
        print("Placement des bateaux aléatoires...")
        for size in self.taille_bateaux:
            placed = False
            while not placed:
                placed = self.creat_boat(size)
        print("Placement des bateaux terminé.")

    def creat_boat(self, size):
        print(f"Tentative de création d'un bateau de taille {size}...")
        start_x = random.randint(0, 9)
        start_y = random.randint(0, 9)
        horizontal = random.choice([True, False])
        positions = []

        for i in range(size):
            if horizontal:
                x = start_x
                y = start_y + i
            else:
                x = start_x + i
                y = start_y
            
            positions.append((x, y))

        bateau = Batiment(positions, size)
        if self.est_position_valide(bateau):
            print(f"Bateau de taille {size} créé avec succès.")
            return self.placer_bateau(bateau)
        print(f"Echec de la création du bateau de taille {size}.")
        return False

    def est_position_valide(self, bateau):
        for coord in bateau.position:
            x, y = coord
            if x < 0 or x >= len(self.grille) or y < 0 or y >= len(self.grille[0]):
                return False
            if self.grille[x][y] != 0:
                return False
        return True

    def placer_bateau(self, bateau):
        print(f"Tentative de placement du bateau de taille {bateau.life} à {bateau.position}...")
        if self.est_position_valide(bateau):
            for coord in bateau.position:
                x, y = coord
                self.grille[x][y] = 1
            self.bateaux.append(bateau)
            print(f"Bateau de taille {bateau.life} placé avec succès.")
            return True
        print(f"Echec du placement du bateau de taille {bateau.life}.")
        return False

class Game:
    def __init__(self):
        self.joueur_air = Player("air",True)
        self.joueur_mer = Player("mer", True)
        self.joueur_sous_marin = Player("sous-marin", True)


