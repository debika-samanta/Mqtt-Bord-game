import paho.mqtt.client as mqttClient
import time
import sys
import ssl
# Function to read coordinates from the text file
def read_coordinates(filename):
    coordinates = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # Skip the first line
            parts = line.strip().split()
            x = int(parts[0])
            y = int(parts[1])
            power = int(parts[2])
            coordinates.append({"x": x, "y": y, "power": power})
    return coordinates

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else:
        print("Connection failed Return Code : ", rc)

def on_message(client, userdata, message):
    if message.topic == "location/life":
        print("Player Died:", message.payload.decode())
    else:
        print("Player", message.payload,"was killed.")

Connected = False  # Global variable for the state of the connection

# Check if the correct number of arguments is provided
if len(sys.argv) != 3:
    print("Usage: python3 script.py <player_id> <filename>")
    sys.exit(1)

client_name = "player-" + sys.argv[1]  # Add player_id to the client name
filename = sys.argv[2]  # Get filename from command-line arguments
broker_address = "127.0.0.1"  # Broker address
port = 1883  # Broker port default for MQTT

# Read coordinates from the text file
coordinates = read_coordinates(filename)

#AWS_PART
client = mqttClient.Client(mqttClient.CallbackAPIVersion.VERSION1, client_name)  # create new instance
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message
awshost = "a2ecittjwkr9t9-ats.iot.ap-south-1.amazonaws.com" #replace
awsport = 8883

caPath = "root-CA.crt" # Root certificate authority, comes from AWS (Replace)
certPath = "iot.cert.pem" #Replace
keyPath = "iot.private.key" 

client.tls_set(caPath, 
    certfile=certPath, 
    keyfile=keyPath, 
    cert_reqs=ssl.CERT_REQUIRED, 
    tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

client.connect(host=awshost, port=awsport)  # connect to broker

client.loop_start()  # start the loop

# Subscribe to location/life topic
client.subscribe("location/life")

while not Connected:  # Wait for connection
    time.sleep(0.1)

try:
    for coord in coordinates:
        client.publish("location/"+client_name, str(coord))
        time.sleep(10)

except KeyboardInterrupt:
    print("Exiting")
    client.disconnect()
    client.loop_stop()
