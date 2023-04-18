from faccao import atacar
from faccao import defender
import paho.mqtt.client as mqtt

def main():
    cmd = 0
    client = mqtt.Client()
    
    def on_connect(client, userdata, flags, rc):
        print("Conectado ao sistema!\n")
        
    def on_message(client, userdata, msg):
        print("\nCidade " + msg.topic + " esta sendo atacada!\n")

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)

    client.loop_start()

    while(1):
        cmd = input("1. Atacar \n2. Defender\n")
        # Atacar
        if(cmd == '1'):
            cmd = input("Atacar o que?\n")
            client.publish(cmd, "ataque!")

        # Defender
        elif(cmd == '2'):
            cmd = input("Defender o que?\n")
            client.subscribe(cmd)

if __name__ == "__main__":
    main()