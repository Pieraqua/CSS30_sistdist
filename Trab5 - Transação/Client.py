
import logging
import threading
import sys
import os

import Pyro5.api

class Client:

    def __init__(self) -> None:
        pass

    def inicializaDaemon(self, daemon):
        daemon.requestLoop()


# Inicializa o logger
logging.basicConfig(stream=sys.stderr,
                    format="[%(asctime)s,%(name)s,%(levelname)s] %(message)s")
log = logging.getLogger("Pyro5")
log.setLevel(logging.WARNING)

# Registra a gerenciadora de callbacks e o client no daemon
daemon = Pyro5.api.Daemon()
client = Client()
uriCliente = daemon.register(client)
#callback = CallbackHandler()
#uriCallback = daemon.register(callback)
#print('Criado cliente: ' + client.nome)
print('URI client: ')
print(uriCliente)
print('---------------------')

# Inicializa o deamon em background
daemonThread = threading.Thread(target=client.inicializaDaemon, args=(daemon,), daemon=True)
daemonThread.start()

# Loclaiza o servidor de nomes
uriNS = Pyro5.api.locate_ns()
print('Nameserver:')
print(uriNS)
print('---------------------')

# Localiza o servidorLeilao
uriServer = uriNS.lookup("ServidorProdutores")
serverProdutores = Pyro5.api.Proxy(uriServer)
print('Servidor:')
print(uriServer)
print('---------------------')

opcao = 1
while(opcao != 0):
    print('****Menu:****')
    print('1: Consultar estoque dos produtores')
    print('2: Fazer um pedido')
    print('5: Testar conexao')
    print('0: Encerrar o programa')

    opcao = input()
    os.system('cls')

    if opcao == '1':
        estoque,quanti = serverProdutores.consultaEstoque()
        print(estoque)
    
    elif opcao == '2':
        estoque,quanti = serverProdutores.consultaEstoque()
        print(estoque)
        pedido = {}
        for i in range(quanti):
            pedido[str(i)] = int(input("Quanto deseja do item " + str(i) + ": "))
            #pedido[str(i)] = 1
        
        print(serverProdutores.fazerPedido(pedido))


    elif opcao == '5':
        print('Enviei alo, quero receber ola:')
        print("Recebi: " + str(serverProdutores.alo()))
    elif opcao == '0':
        sys.exit()
    else:
        print('Digite uma opcao valida')
        print('---------------------\n')
