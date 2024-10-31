import socket
import threading
import json
import uuid
import classes
from queue import Queue
import time

def nettoyer_fichier(nom_fichier):
    with open(nom_fichier, 'r+') as fw:
        lignes = fw.readlines()
        if lignes and lignes[0].strip() == 'SEND_FILE{':
            lignes[0] = '{\n'
        if lignes and lignes[-1].strip() == '}ENDED':
            lignes.pop()
            fw.seek(0)
            fw.writelines(lignes)
            fw.write('}')
            fw.truncate()

def charger_batiments(nom_fichier):
    batiments = []
    with open(nom_fichier, "r") as f:
        data = json.load(f)

        # Boucle sur chaque bateau dans la liste des bateaux du fichier JSON
        for bateau in data["bateaux"]:
            # Accès direct aux valeurs, avec des valeurs par défaut en cas d'absence
            position = bateau["position"] if "position" in bateau else (0, 0)
            taille = bateau["taille"] if "taille" in bateau else 0
            h = bateau["horizontal"] if "horizontal" in bateau else True

            # Construction des positions en fonction de la taille et de l'orientation
            pos = []
            for i in range(taille):
                if h:
                    pos.append((position[0] + i, position[1]))  # Ajout sur l'axe X
                else:
                    pos.append((position[0], position[1] + i))  # Ajout sur l'axe Y
            
            # Création de l'instance Batiment avec la position calculée et la vie
            batiment = classes.Batiment(position=pos, life=taille)
            batiments.append(batiment)

    return batiments


def handle_game(players):
    player_list = []
    n = 0
    text = ["air", "mer", "sous-marin"]
    
    # Initialisation des joueurs
    for conn, client_id in players:
        text_file = f'fileProj_{client_id}.json'
        conn.send(b'SEND_FILE')
        
        # Réception et sauvegarde du fichier
        with open(text_file, "wb") as fw:
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                if chunk.endswith(b'ENDED'):
                    fw.write(chunk[:-5])
                    break
                fw.write(chunk)
        
        nettoyer_fichier(text_file)
        
        # Charger les bateaux et ajouter le joueur
        batiments = charger_batiments(text_file)
        player_list.append([classes.Player(text[n], batiments), client_id, conn])  # Utilise l'UUID pour le joueur
        n += 1

    turn = 0
    while len(player_list) > 1:
        current_player = player_list[turn]
        current_conn = current_player[2]
        current_id = current_player[1]
        print("tpur de " + current_id)
        time.sleep(0.05)
        current_conn.send(b"YOUR_TURN")
        response = current_conn.recv(64).decode('utf-8')
        
        if response.startswith("RESPONSE"):
            _, received_id = response.split(":")
            if received_id != current_id:
                continue  # Ignorer si le mauvais ID a été reçu
            
            json_data = current_conn.recv(1024).decode('utf-8')
            coord_message = json.loads(json_data)
            x = coord_message["coordinates"]["x"]
            y = coord_message["coordinates"]["y"]
            coord_json = json.dumps({"client_id": received_id, "coordinates": {"x": x, "y": y}})
            
            hit = False
            to_remove = []
            
            # Vérifie si un bateau est touché
            for player in player_list:
                if player[1] != current_id:
                    for bat in player[0].bateaux:
                        if (x, y) in bat.position:
                            bat.life -= 1
                            bat.position.remove((x, y))
                            hit = True
                            if bat.life == 0:
                                player[0].bateaux.remove(bat)
                                if not player[0].bateaux:
                                    player[2].send(b"KILL")
                                    to_remove.append(player[1])
            
            # Suppression des joueurs sans bateaux
            player_list = [player for player in player_list if player[1] not in to_remove]
            
            # Confirme si le tir a touché ou non
            if hit:
                current_conn.send(b"HIT")

            # Envoie de l'UPDATE aux autres joueurs
            for play in player_list:
                if play[1] != current_id:  # Exclure le joueur actuel
                    play[2].send(b"UPDATE")
                    time.sleep(0.05)
                    play[2].sendall(coord_json.encode('utf-8'))
                    print("update sent to " + play[1])

            turn = (turn+1) % len(player_list) if player_list else 0

    # Envoi de la victoire au dernier joueur restant
    if player_list:
        player_list[0][2].send(b"WIN")
    for player in player_list:
        player[2].close()

def accept_clients(server_socket):
    queue = Queue()
    player_ids = {}
    while True:
        conn, _ = server_socket.accept()
        print("New client connected.")
        
        # Recevoir l'user ID du client
        user_id = conn.recv(36).decode('utf-8')  # UUID devrait tenir dans 36 caractères
        print(f"User ID {user_id} received from client.")
        
        # Stocker la connexion et l'user ID
        player_ids[user_id] = conn
        queue.put((conn, user_id))
        

        if queue.qsize() >= 3:
            players = {queue.get() for _ in range(3)}
    
    # Démarrer une partie en passant directement le dictionnaire des joueurs
            threading.Thread(target=handle_game, args=(players,)).start()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((socket.gethostname(), 8756))
    server_socket.listen()
    print("Server is listening for connections...")

    accept_thread = threading.Thread(target=accept_clients, args=(server_socket,))
    accept_thread.start()
    accept_thread.join()

start_server()
