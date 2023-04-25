# Cliente da aplicacao de leilao.
# Deve ser capaz de criar leiloes e realizar lances.
# Deve ter uma funcao para ser notificado a cada lance ou ao fim de um leilao.
# Todo lance realizado deve ser assinado digitalmente.

# Retornos:
# 0: Sucesso
# 1: Erro desconhecido
# 2: Valor invalido
# 3: Objeto finalizado

import Pyro5.api
import logging
import threading
import sys
import os
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class CallbackHandler(object):

    @Pyro5.api.expose
    @Pyro5.api.callback
    def alo_callback(self):
        print('---------------------')
        print('Recebi alo')
        print('---------------------\n')
        # return 1//0

    @Pyro5.api.expose
    @Pyro5.api.callback
    def consultaCallback(self, leiloes):
        print('---------------------')
        print('Leiloes ativos:')
        print(leiloes)
        print('---------------------\n')
        # return 1//0
    
    @Pyro5.api.expose
    @Pyro5.api.callback
    def lanceCallback(self, retorno):
        print('---------------------')
        print(retorno)
        print('---------------------\n')
        # return 1//0


class Client:

    def __init__(self):
        print('Digite seu nome')
        self.nome = input()
        self.registrado = False
        self.registroCliente = {
            "nome" : "",
            "uri" : None,
            "chavePublica" : None
        }
        self.chavePrivada = None

    def inicializaDaemon(self, daemon):
        daemon.requestLoop()

    @Pyro5.api.expose
    @Pyro5.api.callback
    def notificaLance(self, leilao):
        print('---------------------')
        print("Foi realizado um lance no leilao")
        print(leilao)
        print('---------------------\n')

    @Pyro5.api.expose
    @Pyro5.api.callback
    def notificaNovo(self, leilao):
        print('---------------------')
        print("Um novo leilao foi cadastrado: ")
        print(leilao)
        print('---------------------\n')

    @Pyro5.api.expose
    @Pyro5.api.callback
    def notificaFim(self, leilao):
        print('---------------------')
        print("O seguinte leilao foi finalizado: ")
        print(leilao)
        print('---------------------\n')


# Inicializa o logger
logging.basicConfig(stream=sys.stderr,
                    format="[%(asctime)s,%(name)s,%(levelname)s] %(message)s")
log = logging.getLogger("Pyro5")
log.setLevel(logging.WARNING)

# Registra a gerenciadora de callbacks e o client no daemon
daemon = Pyro5.api.Daemon()
client = Client()
uriCliente = daemon.register(client)
callback = CallbackHandler()
uriCallback = daemon.register(callback)
print('Criado cliente: ' + client.nome)
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
uriServer = uriNS.lookup("ServidorLeilao")
serverLeilao = Pyro5.api.Proxy(uriServer)
print('Servidor Leilao:')
print(uriServer)
print('---------------------')

opcao = 1
while(opcao != 0):
    print('****Menu:****')
    print('1: Se registrar no servidor')
    print('2: Consultar leiloes ativos')
    print('3: Cadastrar um produto para leilão')
    print('4: Dar lance em leilão')
    print('5: Testar conexao')
    print('0: Encerrar o programa')

    opcao = input()
    os.system('cls')

    match opcao:
        case '1':
            if client.registrado == False:
                print('---------------------')
                print('Se registrando no server')
                client.chavePrivada = RSA.generate(2048)
                chavePublica = client.chavePrivada.public_key()
                client.registroCliente = {
                    "nome" : client.nome,
                    "uri" : uriCliente,
                    "chavePublica" : list(chavePublica.public_key().export_key())
                }
                serverLeilao.registrarCliente(client.registroCliente)
                client.registrado = True
                print('---------------------\n')
            else:
                print('Ja esta cadastrado')
                print('---------------------\n')
        case '2':
            serverLeilao.consultaLeiloes(callback)
        case '3':
            #nome = input('Nome do produto: ')
            #descricao = input('Descricao do produto: ')
            #val = input('Preco inicial do produto: ')
            #tempo = input('Tempo em segundos do leilao: ')
            #serverLeilao.cadastraLeilao(cod, nome, descricao, val, tempo, client.registroCliente)
            serverLeilao.cadastraLeilao('Leilao teste', 'teste', 0, 60, client.registroCliente)
        case '4':
            cod = input('Cod do produto: ')
            valor = input('Valor: ')
            assinada = pkcs1_15.new(client.chavePrivada).sign(SHA256.new(b'Assinado'))
            serverLeilao.darLance(int(cod), int(valor), client.registroCliente, assinada, callback)
        case '5':
            print('Testando funcao alo:')
            serverLeilao.alo(callback)
        case '0':
            sys.exit()
        case _:
            print('Digite uma opcao valida')
            print('---------------------\n')
