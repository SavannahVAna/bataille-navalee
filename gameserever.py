import socket
import threading
import json
import uuid
import classes
from queue import Queue

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
        for bateau in data.get("bateaux", []):
            position = bateau.get("position", [])
            taille = bateau.get("taille", 0)
            h = bateau.get("horizontal", True)
            pos = []
            for i in range(taille):
                if h:
                    pos.append((position[0] + i, position[1]))
                else:
                    pos.append((position[0], position[1] + i))
            batiment = classes.Batiment(position=pos, life=taille)
            batiments.append(batiment)
    return batiments

def handle_game(player_conns):
    """Fonction pour gérer la logique de jeu d'une partie entre trois joueurs."""
    player_list = []
    for i, conn in enumerate(player_conns):
        text_file = f'fileProj_{i + 1}.json'
        conn.send(b'SEND_FILE')

        # Réception et enregistrement des fichiers
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

        # Charger les bateaux du joueur
        batiments = charger_batiments(text_file)
        player_list.append(classes.Player(f"player_{i+1}", batiments))

    turn = 0
    while len(player_list) > 1:
        current_conn = player_conns[turn]
        current_conn.send(b"YOUR_TURN")

        response = current_conn.recv(32).decode('utf-8')
        if response == "RESPONSE":
            json_data = current_conn.recv(1024).decode('utf-8')
            coord_message = json.loads(json_data)
            x = coord_message["coordinates"]["x"]
            y = coord_message["coordinates"]["y"]
            coord_json = json.dumps({"coordinates": {"x": x, "y": y}})

            hit = False
            to_remove = []
            for i, player in enumerate(player_list):
                if i != turn:
                    for bat in player.bateaux:
                        if (x, y) in bat.position:
                            bat.life -= 1
                            bat.position.remove((x, y))
                            hit = True
                            if bat.life == 0:
                                player.bateaux.remove(bat)
                                if not player.bateaux:
                                    player_conns[i].send(b"KILL")
                                    to_remove.append(i)

            for i in sorted(to_remove, reverse=True):
                player_list.pop(i)
                player_conns.pop(i)

            if hit:
                current_conn.send(b"HIT")
            #else:
                #current_conn.send(b"MISS")

            turn = (turn + 1) % len(player_list)

    player_conns[0].send(b"WIN")
    for conn in player_conns:
        conn.close()

def accept_clients(server_socket):
    queue = Queue()
    while True:
        conn, _ = server_socket.accept()
        print("New client connected.")
        queue.put(conn)

        # Quand trois joueurs sont en file, démarre une partie
        if queue.qsize() >= 3:
            players = [queue.get(), queue.get(), queue.get()]
            threading.Thread(target=handle_game, args=(players,)).start()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((socket.gethostname(), 8756))
    server_socket.listen()
    print("Server is listening for connections...")

    accept_thread = threading.Thread(target=accept_clients, args=(server_socket,))
    accept_thread.start()

start_server()
