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


class CallbackHandler(object):
    
    @Pyro5.api.expose #???
    @Pyro5.api.callback
    def alo_callback(self):
        print('Recebi alo')
        print('---------------------')
        return 1//0

class Client:
    
    def __criar_leilao():
        print("Criando leilao\n")

    def __realizar_lance():
        print("Realizando lance\n")

    def notificaLance():
        print("Foi realizado um lance\n")

    def notificaFim():
        print("Um leilao foi encerrado\n")

client = Client

#Registra a gerenciadora de callbacks no daemon
daemon = Pyro5.api.Daemon()
callback = CallbackHandler()
daemon.register(callback)

#Loclaiza o servidor de nomes
uriNS = Pyro5.api.locate_ns()
print('Nameserver:')
print(uriNS)

print('---------------------')

try:
    uriServer = uriNS.lookup("ServidorLeilao")
    print('Servidor Leilao:')
    print(uriServer)

    serverLeilao = Pyro5.api.Proxy(uriServer)

    serverLeilao.alo(callback)
    daemon.requestLoop()
except Exception as e:
    print('Servidor nao localizado')
    print(e)

print('---------------------')
listNS = uriNS.list()
print(listNS)
print('---------------------')

