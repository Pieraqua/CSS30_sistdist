# Servidor da aplicacao de leiloes.
# Deve gerenciar a criacao e o estado de todos os leiloes.
# Deve gerenciar o envio de lances e o fim dos leiloes.
# Deve notificar os clientes interessados sobre o fim dos leiloes ou os lances realizados.
# Deve tambem ser capaz de registrar clientes.
# Deve verificar que os lances recebidos contem uma assinatura valida.

# Retornos:
# 0: Sucesso
# 1: Erro desconhecido
# 2: Valor invalido
# 3: Objeto finalizado

import sys
import threading
import logging
from Leilao import Leilao
import Pyro5.api
import Pyro5.server
import Pyro5.errors
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

class Server:
    def __init__(self):
        self.__leiloes = []
        self.__usuarios = []
        self.cod = 0

    @Pyro5.server.expose
    @Pyro5.server.oneway
    def registrarCliente(self, user):
        print('Tentativa de registro:')
        self.__usuarios.append(user)
        print('---------------------')
        print("Foi registrado o cliente: " + user["nome"])
    
    @Pyro5.server.expose
    @Pyro5.server.oneway
    def consultaLeiloes(self, callback):
        callback._pyroClaimOwnership()
        print('---------------------')
        print('Enviando lista de leiloes')
        self.imprimeLeiloes()
        leiloes = ""
        for leilao in self.__leiloes:
            leiloes += leilao.retornaInformacoes()
            leiloes += "    ---------------------"
        callback.consultaCallback(leiloes)

    @Pyro5.server.expose
    @Pyro5.server.oneway
    def cadastraLeilao(self, nome, descricao, val, tempo, dono):
        leilao = Leilao(self.cod, nome, descricao, val, tempo, dono)
        self.__leiloes.append(leilao)
        self.cod = self.cod + 1
        print('---------------------')
        print('Foi cadastrado o ' + nome + ' de ' + dono["nome"])
        interessados = self.__usuarios
        for item in interessados:
            uri = item["uri"]
            user = Pyro5.api.Proxy(uri)
            user.notificaNovo(leilao.retornaInformacoes())
        p = threading.Thread(target=self.timerLeilao(leilao, self, leilao.tempo()))
        p.start()

    @Pyro5.server.expose
    @Pyro5.server.oneway
    def darLance(self, cod, valor, comprador, mensagemCodificada, callback):
        callback._pyroClaimOwnership()

        usuario = None
        for item in self.__usuarios:
            if item["uri"] == comprador["uri"]:
                usuario = item
        
        if usuario == None:
            callback.lanceCallback('Voce nao esta cadastrado no server')
            return
        
        encryptor = PKCS1_OAEP.new(usuario["chavePublica"])
        mensagem = base64.b64decode(mensagemCodificada)
        mensagemDecodificada = encryptor.decrypt(mensagem)
        if mensagemDecodificada != "ass"+usuario["nome"]:
            callback.lanceCallback('Problema na assinatura')
            return

        try:
            leilao = self.__leiloes[cod]
        except:
            print('---------------------')
            print('Cod de produto invalido')
            callback.lanceCallback('Cod de produto invalido')
            return
        
        if leilao.dono() == comprador:
            callback.lanceCallback('Dono nao pode dar lance!!!')
            return

        print('---------------------')
        print('Dando lance de: ' + comprador["nome"])
        retorno = leilao.realizar_lance(valor, comprador)
        if retorno == 3:
            print('---------------------')
            print('Leilao finalizado')
            callback.lanceCallback('Leilao finalizado')
        elif retorno == 2:
            print('---------------------')
            print('Valor menor que o lance atual')
            print('---------------------\n')
            callback.lanceCallback('Valor menor que o lance atual')
        elif retorno == 0:
            print('---------------------')
            print('Lance dado com sucesso')
            interessados = leilao.interessados()
            for item in interessados:
                uri = item["uri"]
                user = Pyro5.api.Proxy(uri)
                user.notificaLance(leilao.retornaInformacoes())
    
    def imprimeLeiloes(self):
        print('---------------------')
        print('Imprimindo leiloes: ')
        leiloes = ""
        for leilao in self.__leiloes:
            leiloes += leilao.retornaInformacoes()
            leiloes += "    ---------------------"
        print(leiloes)

    def leilaoFinalizado(self, leilao):
        interessados = leilao.interessados()
        print('---------------------')
        print('Leilao: ' + leilao.nome() + ' finalizado, notificando interessados')
        for item in interessados:
            uri = item["uri"]
            user = Pyro5.api.Proxy(uri)
            user.notificaFim(leilao.retornaInformacoes())
    
    def timerLeilao(self, leilao, servidor, tempo):
        for i in range(tempo):
            leilao.tick_tempo()
            time.sleep(1)
        
        servidor.leilaoFinalizado(leilao)
    
    #-------------------------------------------#
    
    @Pyro5.server.expose
    @Pyro5.server.oneway
    def alo(self, callback):
        callback._pyroClaimOwnership()
        print('---------------------')
        print('Recebi alo, devolvendo alo')
        try:
            callback.alo_callback()
        except:
            print('Exception do callback')
        print('Fim do alo')


# Inicializa o logger
logging.basicConfig(stream=sys.stderr,
                    format="[%(asctime)s,%(name)s,%(levelname)s] %(message)s")
log = logging.getLogger("Pyro5")
log.setLevel(logging.WARNING) 
    
#Cria o daemon e se registra
daemon = Pyro5.api.Daemon()
server = Server()
uriServer = daemon.register(server)
print('URi do server:')
print(uriServer)
print('---------------------\n')

#Loclaiza o servidor de nomes
uriNS = Pyro5.api.locate_ns()
print('Nameserver:')
print(uriNS)

#Se registra no servidor de nomes
uriNS.register("ServidorLeilao", uriServer)
print('---------------------')

#-------------- teste leiloes
# server.imprimeLeiloes()

print('Aguardando requests\n')
daemon.requestLoop()