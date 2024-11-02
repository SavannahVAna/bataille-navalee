import socket
import uuid
import json

def envoi_bateaux(csFT, client_id, bateaux_data):
    """Envoie la liste des bateaux et l'UUID du client en format JSON au serveur."""
    data = {
        "client_id": client_id,
        "bateaux": bateaux_data
    }
    json_data = json.dumps(data)
    csFT.sendall(json_data.encode('utf-8'))
    print("Sent ships' positions to the server.")

def envoi(): 
    csFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    csFT.connect((socket.gethostname(), 8756))
    client_id = str(uuid.uuid4())  # Génère un identifiant unique pour le client
    print(client_id)
    csFT.sendall(client_id.encode('utf-8'))
    
    while True:
        data = csFT.recv(32)
        if data == b'SEND_FILE':
            print("Server requested ships' positions.")

            # Chargement des bateaux depuis un fichier ou configuration
            with open("positions.json", "r") as f:
                bateaux_data = json.load(f)
            
            # Envoyer les bateaux avec l'UUID
            envoi_bateaux(csFT, client_id, bateaux_data)
            message = "ENDED"
            csFT.sendall(message.encode('utf-8'))
            break

    return csFT, client_id 

def await_response(client_socket: socket.socket):
    while True:
        try:
            server_message = client_socket.recv(32).decode('utf-8', errors='ignore')
            if not server_message:
                print("Connection closed by server.")
                break

            if server_message.startswith("YOUR_TURN"):
                print("It's your turn!")
                return 0, client_socket, []

            elif server_message.startswith("UPDATE"):
                print("Update received.")
                json_data = client_socket.recv(1024).decode('utf-8')
                coord_message = json.loads(json_data)
                x = coord_message["coordinates"]["x"]
                y = coord_message["coordinates"]["y"]
                print(x,y)
                return 1, client_socket, (x, y)

            elif server_message.startswith("KILL"):
                return 2, client_socket, []

            elif server_message.startswith("HIT"):
                return 3, client_socket, []

            elif server_message.startswith("WIN"):
                return 4, client_socket, []
            
            elif server_message.startswith("COULE"):
                return 5, client_socket, []

            else:
                print("Unknown message received:", server_message)

        except Exception as e:
            print(f"Error receiving data: {e}")
            break
        
def play(socket: socket.socket, client_id: str, coo: tuple):
    try:
        message_type = "RESPONSE"
        socket.sendall(f"{message_type}:{client_id}".encode('utf-8')) 

        coord_message = {
            "client_id": client_id,  
            "coordinates": {
                "x": coo[0],
                "y": coo[1]
            }
        }
        coord_json = json.dumps(coord_message)
        socket.sendall(coord_json.encode('utf-8'))
        print("Response and coordinates sent to server.")
        
    except socket.error as e:
        print(f"An error occurred: {e}")

