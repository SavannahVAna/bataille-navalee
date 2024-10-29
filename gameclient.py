import socket
import uuid
import json

def envoi_bateaux(csFT, bateaux_data):
    """Envoie la liste des bateaux en format JSON au serveur."""
    json_data = json.dumps(bateaux_data)
    csFT.sendall(json_data.encode('utf-8'))
    print("Sent ships' positions to the server.")

def envoi(): 
    csFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    csFT.connect((socket.gethostname(), 8756))
    #client_id = str(uuid.uuid4())  # Remplacez par un identifiant dynamique si nécessaire
    #csFT.send(client_id.encode('utf-8'))
    
    # Envoyer une commande au serveur pour indiquer qu'un fichier va être envoyé
    while True:
        data = csFT.recv(32)
        if data == b'SEND_FILE':
            print("Server requested ships' positions.")

            # Chargement des bateaux depuis un fichier ou configuration
            with open("positions.json", "r") as f:
                bateaux_data = json.load(f)
            
            # Envoyer les bateaux
            envoi_bateaux(csFT, bateaux_data)
            message = "ENDED"
            csFT.sendall(message.encode('utf-8'))
            break


    return csFT

def await_response(client_socket: socket.socket):
    while True:
        try:
            server_message = client_socket.recv(32).decode('utf-8', errors='ignore')  # Réception et décodage du message
            if not server_message:
                print("Connection closed by server.")
                break

            # Vérifier si le message commence par "YOUR_TURN" ou "UPDATE"
            if server_message.startswith("YOUR_TURN"):
                print("It's your turn!")
                return 0, client_socket, []

            elif server_message.startswith("UPDATE"):
                print("Update received.")
                json_data = client_socket.recv(1024).decode('utf-8')
                coord_message = json.loads(json_data)
                x = coord_message["coordinates"]["x"]
                y = coord_message["coordinates"]["y"]
                return 1, client_socket, (x, y)

            elif server_message.startswith("KILL"):
                return 2, client_socket, []

            elif server_message.startswith("HIT"):
                return 3, client_socket, []

            elif server_message.startswith("WIN"):
                return 4, client_socket, []

            else:
                print("Unknown message received:", server_message)

        except Exception as e:
            print(f"Error receiving data: {e}")
            break
        
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
