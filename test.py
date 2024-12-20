import pygame
import sys
import json
import gameclient
import threading
from queue import Queue
import os

def checkpos(liste, el):
    tmp = []
    tmp2 = []
    
    # Vérifier chaque élément de la liste principale
    if liste:
        for element in liste:
            if len(element) < 3:
                print(f"Erreur : Element incorrect dans liste : {element}")
                continue
            for i in range(element[2]):
                if element[1]:  # Si horizontal
                    tmp.append((element[0][0] + i, element[0][1]))
                else:
                    tmp.append((element[0][0], element[0][1] + i))
    
    # Vérifier `el` comme élément unique, au lieu d'itérer
    if len(el) >= 3:
        for i in range(el[2]):
            if el[1]:  # Si horizontal
                tmp2.append((el[0][0] + i, el[0][1]))
            else:
                tmp2.append((el[0][0], el[0][1] + i))
    
    # Vérifier s'il y a des conflits dans les coordonnées
    for item in tmp2:
        if item in tmp:
            print("invalid coordinates")
            return False
    
    return True

        

def background_await_response(socket, response_q):
    global response_result
    while True:
        response_result = gameclient.await_response(socket)
        response_q.put(response_result)
        #if response_result[0] == 1:
            #print(response_result)
            #print("update made here")

def dictapped(de : list):
    bati = {
        "bateaux" :[
            {"position": de[0][0], "horizontal" : de[0][1], "taille" : de[0][2]},
            {"position": de[1][0], "horizontal" : de[1][1], "taille" : de[1][2]},
            {"position": de[2][0], "horizontal" : de[2][1], "taille" : de[2][2]},
            {"position": de[3][0], "horizontal" : de[3][1], "taille" : de[3][2]},
            {"position": de[4][0], "horizontal" : de[4][1], "taille" : de[4][2]}
        ]
    }
    with open('positions.json', 'w') as f:
        json.dump(bati, f, indent=4)
    a, id = gameclient.envoi()
    return a, id

class GameObject:
    def __init__(self, image, x, y, size):
        self.image = image
        self.pos = pygame.Vector2(x, y)
        self.target_pos = pygame.Vector2(x, y)  
        self.horizontal = True  # Orientation du bateau : horizontal = True, vertical = False
        self.size = size

    def move(self, up=False, down=False, left=False, right=False):
        
        new_target_pos = self.target_pos.copy()

        if up:
            new_target_pos.y -= 24
        elif down:
            new_target_pos.y += 24
        elif left:
            new_target_pos.x -= 24
        elif right:
            new_target_pos.x += 24

        # Limites pour empêcher l'objet de sortir de la grille en fonction de son orientation
        if self.horizontal:
            # Limites pour un objet horizontal
            if new_target_pos.x < 6 or new_target_pos.x > 6 + (9 * 24 - (self.size - 1) * 24):  # S'assure qu'il ne sort pas à gauche ou à droite
                return
            if new_target_pos.y < -18 or new_target_pos.y > -18 + (9 * 24):  # S'assure qu'il ne sort pas en haut ou en bas
                return
        else:
            # Limites pour un objet vertical
            if new_target_pos.x < -18 or new_target_pos.x > -18 + (9 * 24):  # S'assure qu'il ne sort pas à gauche ou à droite
                return
            if new_target_pos.y < 6 or new_target_pos.y > 6 + (9 * 24 - (self.size - 1) * 24):  # S'assure qu'il ne sort pas en haut ou en bas
                return

        # Applique le mouvement seulement si le nouvel emplacement est dans les limites
        self.target_pos = new_target_pos  
        self.pos = self.target_pos  

    def rotate(self):
    # Vérifie que la rotation reste dans les limites
        if self.horizontal:  # Si l’objet passe de horizontal à vertical
            # Limites pour un objet vertical
            if (self.pos.x < 6 or 
                self.pos.x > 6 + (9 * 24 - (self.size - 1) * 24) or
                self.pos.y < 6 or 
                self.pos.y > 6 + (7 * 24 - (self.size - 1) * 24)):  
                return
        else:  # Si l’objet passe de vertical à horizontal
            # Limites pour un objet horizontal
            if (self.pos.x < 6 or 
                self.pos.x > 6 + (7 * 24 - (self.size - 1) * 24) or 
                self.pos.y < -18 or 
                self.pos.y > -18 + (9 * 24)):
                return


        self.horizontal = not self.horizontal  
        self.image = pygame.transform.rotate(self.image, 90)  # Pivote l'image de 90 degrés
    
class Cursor:
    def __init__(self, image, x, y):
        self.image = image
        self.pos = pygame.Vector2(x, y)
        self.target_pos = pygame.Vector2(x, y) 
        

    def move(self, up=False, down=False, left=False, right=False):
       
        new_target_pos = self.target_pos.copy()

        if up:
            new_target_pos.y -= 24
        elif down:
            new_target_pos.y += 24
        elif left:
            new_target_pos.x -= 24
        elif right:
            new_target_pos.x += 24

        # Limites pour empêcher l'objet de sortir de la grille en fonction de son orientation
        
            # Limites pour un objet horizontal 
        if new_target_pos.x < 276 or new_target_pos.x > 276 + (10 * 24 ):  # S'assure qu'il ne sort pas à gauche ou à droite
            return
        if new_target_pos.y < 0 or new_target_pos.y > -18 + (11 * 24):  # S'assure qu'il ne sort pas en haut ou en bas
            return

        # Applique le mouvement seulement si le nouvel emplacement est dans les limites
        self.target_pos = new_target_pos  # Met à jour la position cible
        self.pos = self.target_pos  # Déplace directement vers la cible


# Initialisation de Pygame
pygame.init()

# Création de la fenêtre
screen = pygame.display.set_mode((540, 270))
clock = pygame.time.Clock()

# Chargement des images
player3 = pygame.image.load('sprites/bateau3.png').convert_alpha()
player2 = pygame.image.load('sprites/bateau2.png').convert_alpha()
player4 = pygame.image.load('sprites/bateau4.png').convert_alpha()
player5 = pygame.image.load('sprites/bateau5.png').convert_alpha()
background = pygame.image.load('sprites/grille.bmp').convert() 
blue_player_image3 = pygame.image.load('sprites/bateau3blue.png').convert_alpha()
blue_player_image2 = pygame.image.load('sprites/bateau2blue.png').convert_alpha()
blue_player_image4 = pygame.image.load('sprites/bateau4blue.png').convert_alpha()
blue_player_image5 = pygame.image.load('sprites/bateau5blue.png').convert_alpha()
cross = pygame.image.load('sprites/cross.png').convert_alpha()
cursor = pygame.image.load('sprites/cursor.png').convert_alpha()
hit = pygame.image.load('sprites/hit.png').convert_alpha()
play = False
# Dessin de l'arrière-plan
screen.blit(background, (0, 0))
blue_ships = []
cross_list = []
hit_list = []
# Création de l'objet joueur en haut à gauche
p = GameObject(player2, 6, -18, 2)
tour = 0
total = []
enabled = False
phase1 = True
response_lock = threading.Lock()
response_result = None
response_queue = Queue()
# Boucle principale
while True:
    screen.blit(background, (0, 0))  # Redessiner l'arrière-plan
    if (p!=None):
        screen.blit(p.image, p.pos)  # Afficher le joueur
    for blue_ship in blue_ships:
        screen.blit(blue_ship[0], blue_ship[1])
    for crossi in cross_list:
        try :
            screen.blit(crossi[0], crossi[1])
        except Exception:
            print(cross)
    for crosst in hit_list:
        screen.blit(crosst[0], crosst[1])


    for event in pygame.event.get():
        if phase1:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
               
                if event.key == pygame.K_UP:
                    p.move(up=True)
                elif event.key == pygame.K_DOWN:
                    p.move(down=True)
                elif event.key == pygame.K_LEFT:
                    p.move(left=True)
                elif event.key == pygame.K_RIGHT:
                    p.move(right=True)
                elif event.key == pygame.K_t:  # Rotation sur appui de 't'
                    p.rotate()
                elif event.key == pygame.K_RETURN:  # Touche Entrée pour valider
                    temp = []
                    adjusted_x = (p.pos.x - 6) / 24
                    adjusted_y = (p.pos.y + 18) / 24

                    if p.horizontal:
                        coords = (adjusted_x, adjusted_y)
                        horizon = True
                    else:
                        coords = (adjusted_x + 1, adjusted_y - 1)
                        horizon = False

                    print("Coordonnées du bateau:", coords)

                    # Ajout de `coords` et `horizon` à `temp`
                    temp.append(coords)
                    temp.append(horizon)

                    # Conditions pour chaque tour
                    if tour == 0 and checkpos(total, [coords, horizon, 2]):
                        temp.append(2)
                        bl = blue_player_image2
                        if not p.horizontal:
                            bl = pygame.transform.rotate(bl, 90)
                        blue_ships.append([bl, (p.pos.x, p.pos.y)])
                        p = GameObject(player2, 6, -18, size=2)

                    elif tour == 1 and checkpos(total, [coords, horizon, 2]):
                        temp.append(2)
                        bl = blue_player_image2
                        if not p.horizontal:
                            bl = pygame.transform.rotate(bl, 90)
                        blue_ships.append([bl, (p.pos.x, p.pos.y)])
                        p = GameObject(player3, 6, -18, size=3)

                    elif tour == 2 and checkpos(total, [coords, horizon, 3]):
                        temp.append(3)
                        bl = blue_player_image3
                        if not p.horizontal:
                            bl = pygame.transform.rotate(bl, 90)
                        blue_ships.append([bl, (p.pos.x, p.pos.y)])
                        p = GameObject(player4, 6, -18, size=4)

                    elif tour == 3 and checkpos(total, [coords, horizon, 4]):
                        temp.append(4)
                        bl = blue_player_image4
                        if not p.horizontal:
                            bl = pygame.transform.rotate(bl, 90)
                        blue_ships.append([bl, (p.pos.x, p.pos.y)])
                        p = GameObject(player5, 6, -18, size=5)

                    elif tour == 4 and checkpos(total, [coords, horizon, 5]):
                        temp.append(5)
                        bl = blue_player_image5
                        if not p.horizontal:
                            bl = pygame.transform.rotate(bl, 90)
                        blue_ships.append([bl, (p.pos.x, p.pos.y)])
                    if len(temp) == 3:
                        total.append(temp)
                        tour += 1

                    # Vérifier la fin de la phase 1
                    if tour == 5:
                        con, ide = dictapped(total)
                        phase1 = False
                        client_thread = threading.Thread(target=background_await_response, args=(con, response_queue,))
                        client_thread.daemon = True
                        client_thread.start()
                        a = -1
                    

                
        else :
            """with response_lock:
                if response_result is not None:
                    b, conn, cordss = response_result  # Unpack de la réponse
                    response_queue.put((b,conn,cordss))
                    response_result = None  # Reset pour la prochaine réponse"""
            #if not play:
                #a, con, cords = gameclient.await_response(con) # mettre ça juste dans le else et apre changer une autre valeur su c'est phase tour ou phase update
            if not response_queue.empty():
                a, con, cords = response_queue.get()
                #print(a)
                #print(cords)
                if a ==0:
                    if p == None :
                        p = Cursor(cursor, 290, 18)
                    play = True
                    
                    
                            
                if a ==1:
                    #faire la focntion await response retourner un tuple de coordonées en plus
                    pixel_x = cords[0] * 24 +18
                    pixel_y = (cords[1] + 1.5) * 24 - 18
                    hit_list.append([cross,(pixel_x,pixel_y)])
                    print("update happened")
                    
                if a == 3:
                    e = cross_list.pop()
                    e[0] = hit
                    cross_list.append(e)
                    #print(cross_list)
                    print("hit")
                    
                if a == 2 :
                    print("you're dead")
                    os.remove("positions.json")
                    pygame.quit()
                    sys.exit()
                if a == 4 :
                    print("you won")
                    os.remove("positions.json")
                    pygame.quit()
                    sys.exit()
                if a ==5:
                    print("vous avez coulé un bateau!")
                    e = cross_list.pop()
                    e[0] = hit
                    cross_list.append(e)
                    #print(cross_list)
            if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
            if play:
                if event.type == pygame.KEYDOWN:
                    
                    if event.key == pygame.K_UP:
                        p.move(up=True)
                    elif event.key == pygame.K_DOWN:
                        p.move(down=True)
                    elif event.key == pygame.K_LEFT:
                        p.move(left=True)
                    elif event.key == pygame.K_RIGHT:
                        p.move(right=True)
                    
                    elif event.key == pygame.K_RETURN:  
                        
                        cross_list.append([cross,(p.pos.x, p.pos.y)])
                        print(cross_list)
                        adjusted_x = (p.pos.x - 290) / 24
                        adjusted_y = (p.pos.y + 18) / 24 -1.5 
                        
                        p =None
                        play =False
                        gameclient.play(con,ide, (adjusted_x, adjusted_y))
                


                

    # Mettre à jour l'écran
    pygame.display.update()
    clock.tick(60)
