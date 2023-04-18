import paho.mqtt.client as mqtt

# Publicar um ataque para a cidade especificada
def atacar(cidade, client):
    client.publish(cidade, "ataque!")

# Se "Aliar" (inscrever) a uma cidade e ficar ouvindo por ataques
def defender(cidade, client):
    client.subscribe(cidade)
    