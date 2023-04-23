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

from Leilao import Leilao
import Pyro5.api
import Pyro5.server
import Pyro5.errors

class Server:
    def __init__(self):
        self.__leiloes = []
        self.__usuarios = []
        self.cod = 0

    @Pyro5.server.expose
    @Pyro5.server.oneway
    def registrarCliente(self, user):
        self.__usuarios.append(user)
        print("Foi registrado o cliente: " + user["nome"])
    
    @Pyro5.server.expose
    @Pyro5.server.oneway
    def consultaLeiloes(self, callback):
        callback._pyroClaimOwnership()
        print('Enviando lista de leiloes')
        self.imprimeLeiloes()
        leiloes = ""
        for leilao in self.__leiloes:
            leiloes += leilao.retornaInformacoes()
        callback.consultaCallback(leiloes)

    @Pyro5.server.expose
    @Pyro5.server.oneway
    def cadastraLeilao(self, nome, descricao, val, tempo, dono):
        leilao = Leilao(self.cod, nome, descricao, val, tempo, dono)
        self.__leiloes.append(leilao)
        self.cod = self.cod + 1
        print('Foi cadastrado o ' + nome + ' de ' + dono["nome"])
        interessados = self.__usuarios
        for item in interessados:
            uri = item["uri"]
            user = Pyro5.api.Proxy(uri)
            user.notificaNovo(leilao.retornaInformacoes())

    @Pyro5.server.expose
    @Pyro5.server.oneway
    def darLance(self, cod, valor, comprador, callback):
        callback._pyroClaimOwnership()
        try:
            leilao = self.__leiloes[cod]
        except:
            print('Cod de produto invalido')
            callback.lanceCallback('Cod de produto invalido')
            return
        
        if leilao.dono() == comprador:
            callback.lanceCallback('Dono nao pode dar lance!!!')
            return

        print('Dando lance')
        retorno = leilao.realizar_lance(valor, comprador)
        if retorno == 3:
            print('Leilao finalizado')
            callback.lanceCallback('Leilao finalizado')
        elif retorno == 2:
            print('Valor menor que o lance atual')
            callback.lanceCallback('Valor menor que o lance atual')
        elif retorno == 0:
            print('Lance dado com sucesso')
            interessados = leilao.interessados()
            for item in interessados:
                uri = item["uri"]
                user = Pyro5.api.Proxy(uri)
                user.notificaLance(leilao.retornaInformacoes())
    
    #-------------------------------------------#
    
    @Pyro5.server.expose
    @Pyro5.server.oneway
    def alo(self, callback):
        callback._pyroClaimOwnership()
        print('Recebi alo, devolvendo alo')
        try:
            callback.alo_callback()
        except:
            print('Exception do callback')
        print('Fim do alo')
        print('---------------------\n')
    
    def imprimeLeiloes(self):
        print('Imprimindo leiloes: ')
        leiloes = ""
        for leilao in self.__leiloes:
            leiloes += leilao.retornaInformacoes()
        print(leiloes)
        
    
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