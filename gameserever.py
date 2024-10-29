import socket
import classes
import uuid
import json
def nettoyer_fichier(nom_fichier):
    """Nettoie le fichier en supprimant la dernière ligne et en ajoutant une accolade fermante."""
    with open(nom_fichier, 'r+') as fw:  # Ouvrir en mode lecture/écriture
        lignes = fw.readlines()  # Lire toutes les lignes
        if lignes and lignes[0].strip() == 'SEND_FILE{':
            lignes[0] = '{\n'  # Remplacer par une accolade ouvrante
        if lignes and lignes[-1].strip() == '}ENDED':
            lignes.pop()  # Supprimer la dernière ligne
            fw.seek(0)  # Revenir au début du fichier
            fw.writelines(lignes)  # Écrire les lignes restantes
            fw.write('}')  # Ajouter une accolade fermante
            fw.truncate()  # Truncate le fichier pour enlever le reste
            # Réécrire le fichier sans la dernière ligne

def charger_batiments(nom_fichier):
    batiments = []
    with open(nom_fichier, "r") as f:
        data = json.load(f)
        
        # Parcourir chaque bateau dans le JSON
        for bateau in data.get("bateaux", []):
            position = bateau.get("position", [])
            taille = bateau.get("taille", 0)
            h = bateau.get("horizontal", True)
            # Créer un objet Batiment avec position et vie
            pos = []
            for i in range(taille):
                if h :
                    pos.append((position[0] + i,position[1]))
                else :
                    pos.append((position[0] ,position[1]+i))
            batiment = classes.Batiment(position=pos, life=taille)
            batiments.append(batiment)
    
    return batiments

# Créer un socket serveur
ssFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssFT.bind((socket.gethostname(), 8756))
ssFT.listen(1)
con_liest = []
id_list = []
# Boucle pour accepter plusieurs connexions
while True:
    conn, address = ssFT.accept()
    client_id = conn.recv(1024).decode('utf-8')
    print(f"Connected to {address} with ID: {client_id}")
    id_list.append(client_id)
    con_liest.append(conn)
    for i in range(1, 4):  # Limiter à 3 fichiers
        text_file = f'fileProj{i}.json'  # Nom des fichiers pour les 3 envois
        data = conn.recv(32)  # Recevoir les données

        if not data:
            print("No more data received, closing connection.")
            break  # Si aucune donnée, sortir de la boucle

        if data == b'SEND_FILE':
            print(f"Starting to receive file {i}...")
            with open(text_file, "wb") as fw:
                while True:
                    chunk = conn.recv(32)
                    if not chunk:
                        print("No more data received, closing file.")
                        break
                    elif chunk == b'BEGIN':
                        print("File transmission has begun.")
                        continue
                    elif chunk == b'ENDED':
                        print('Ending the file transfer.')
                        break
                    else:
                        fw.write(chunk)  # Écrire les données dans le fichier
                        print('Wrote to file:', chunk.decode('utf-8', errors='ignore'))

            print(f"File {i} received successfully.")
            nettoyer_fichier(text_file)  # Nettoyer le fichier reçu

        else:
            print(f"Unknown command received: {data.decode('utf-8', errors='ignore')}")

    batiments1 = charger_batiments("fileProj1.json")
    batiments2 = charger_batiments("fileProj2.json")
    batiments3 = charger_batiments("fileProj3.json")
    Player1 = classes.Player("air", batiments1)
    Player2 = classes.Player("mer", batiments2)
    Player3 = classes.Player("sous-marin", batiments3)
    player_list = [Player1, Player2, Player3]
    turn = 0
    while len(player_list) >1:
        message = "YOUR_TURN"
        con_liest[turn].send(message.encode('utf-8'))
        response = con_liest[turn].recv(32).decode('utf-8')
        if response == "RESPONSE":
            # Recevoir les coordonnées sous forme de JSON
            json_data = con_liest[turn].recv(1024).decode('utf-8')
            coord_message = json.loads(json_data)
            x = coord_message["coordinates"]["x"]
            y = coord_message["coordinates"]["y"]
            print(f"Received coordinates: x={x}, y={y}")
            #TODO traiter le message
            coord_message = {
                        "coordinates": {
                            "x": x,
                            "y": y
                        }
                    }
            coord_json = json.dumps(coord_message)
            to_remove = []

            for i in range(len(player_list)):
                hit = False
                if i != turn:
                    # HERE
                    for bat in player_list[i].bateaux:
                        for pos in bat.position:
                            if pos == (x, y):
                                bat.life -= 1
                                hit = True
                                bat.position.remove(pos)  # Enlève la position touchée
                                break  # Sort de la boucle une fois qu'on a trouvé la position
                        
                        if bat.life == 0:
                            # Si le bateau a 0 de vie, le retire de la liste
                            player_list[i].bateaux.remove(bat)
                            # Vérifier si le joueur a perdu tous ses bateaux
                            if len(player_list[i].bateaux) == 0:
                                message = "KILL"
                                turn %= len(player_list)
                                con_liest[i].send(message.encode('utf-8'))
                                to_remove.append(i)  # Ajoute l'index à supprimer
                                break  # Sort de la boucle dès qu'un bateau est détruit
                                

                    # Envoyer la mise à jour si le joueur n'est pas mort
                    if i not in to_remove:
                        message = "UPDATE"
                        con_liest[i].send(message.encode('utf-8'))

        # Envoyer les coordonnées
                        con_liest[i].sendall(coord_json.encode('utf-8'))
            if hit:
                con_liest[turn].send("HIT".encode('utf-8'))

            # Supprimer les joueurs et les connexions
            for j in sorted(to_remove, reverse=True):  # Tri en ordre décroissant pour éviter les problèmes d'index
                player_list.pop(j)  # Retire le joueur
                con_liest.pop(j)  # Retire le socket correspondant
            turn = (turn +1)%len(player_list) 
        
        else:
            print("Unexpected response from client:", response)
        

# Vous pouvez garder le socket serveur actif si nécessaire
# ssFT.close()   Cela devrait être géré selon la logique de votre programme