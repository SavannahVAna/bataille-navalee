import socket
import uuid
import json
def envoi(): 
    csFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    csFT.connect((socket.gethostname(), 8756))
    client_id = str(uuid.uuid4())  # Remplacez par un identifiant dynamique si nécessaire
    csFT.send(client_id.encode('utf-8'))
    # Envoyer une commande au serveur pour indiquer qu'un fichier va être envoyé
    csFT.send(b'SEND_FILE')  # Indiquer au serveur que l'on va envoyer un fichier

    text_file = 'positions.json'
    
    # Envoyer le fichier
    with open(text_file, 'rb') as fs: 
        # Indiquer le début de l'envoi
        csFT.send(b'BEGIN')
        
        while True:
            data = fs.read(1024)
            if not data:
                print('No more data to send. Breaking from sending data.')
                break  # Sortir de la boucle si aucune donnée n'est lue
            
            print('Sending data:', data.decode('utf-8', errors='ignore'))  # Ignorer les erreurs de décodage
            csFT.send(data)  # Envoyer les données lues
            print('Sent data:', data.decode('utf-8', errors='ignore'))

        csFT.send(b'ENDED')  # Envoyer le signal de fin après avoir terminé d'envoyer
        print('Sent END signal.')

    return csFT,client_id

def await_response(socket : socket, id : str):
    while True:
        server_message = socket.recv(32).decode('utf-8', errors='ignore')  # Réception et décodage du message
        if not server_message:
            print("Connection closed by server.")
            break

        # Vérifier si le message commence par "YOUR_TURN" ou "UPDATE"
        if server_message.startswith("YOUR_TURN"):
            print("It's your turn!")
            # Ici, vous pourriez ajouter la logique pour l'action à réaliser lors du tour du client
            # Exemple : envoyer un coup de jeu
            return 0, socket, []
            #socket.send(b'MOVE_POSITION')   Envoyer la commande pour effectuer une action (exemple)
        elif server_message.startswith("UPDATE"):
            print("Update received.")
            json_data = socket.recv(1024).decode('utf-8')
            coord_message = json.loads(json_data)
            x = coord_message["coordinates"]["x"]
            y = coord_message["coordinates"]["y"]
            # Ici, traiter les informations d’update envoyées par le serveur
            # Ex : recevoir l'état mis à jour du jeu et l’afficher
            return 1, socket, (x,y)
        elif server_message.startswith("KILL"):
            return 2, socket, []
        elif server_message.startswith("HIT"):
            return 3, socket, []
        else:
            print("Unknown message received:", server_message)

def play(socket :socket, coo : tuple):
    try:
        # Envoyer le message d'identification "RESPONSE"
        message_type = "RESPONSE"
        socket.sendall(message_type.encode('utf-8'))
        
        # Préparer les coordonnées en format JSON
        coord_message = {
            "coordinates": {
                "x": coo[0],
                "y": coo[1]
            }
        }
        # Convertir le dictionnaire en une chaîne JSON
        coord_json = json.dumps(coord_message)

        # Envoyer les coordonnées
        socket.sendall(coord_json.encode('utf-8'))
        print("Response and coordinates sent to server.")
        
    except socket.error as e:
        print(f"An error occurred: {e}")



# Exemple d'appel de la fonction
