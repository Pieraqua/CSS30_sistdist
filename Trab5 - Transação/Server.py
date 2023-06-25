# Fila para pedidos
# 5 recursos
# Mutex para cada recurso (ou algo do tipo)

import Pyro5.api
import Pyro5.server
import Pyro5.errors

import sys
import threading
import logging
import random
import time
import continuous_threading

# Cliente pode:

# Se registrar ???
# Pedir lista de itens

# Fazer um pedido:
# Enfilera o pedido:
# Trava o mutex de cada recurso
# Cada recurso:
# Aleatoriamente é feito um delay para cada entrega
# Aleatoriamente é feita uma chance de erro para cada entrega
# Não erro:
# Salva o valor atual num arquivo
# Notifica o server que a dedução foi feita
# Erro:
# Notifica erro ao server
# Caso todos os recursos cheguem em segurança:
# Faz a entrega
# Libera os mutex
# Atualiza os valores dos recursos
# Caso algum recurso dê erro:
# Volta todos os recursos ao valor do arquivo de log
# Notifica o usuário do erro
# Desenfilera o pedido

# Pedido:
# uri dono?
# id do pedido
# quanto de cada recurso:
# r1
# r2
# r3
# ...

locks = []

class ProdutorRecurso:
    def __init__(self, nome, id):
        self.nome = nome
        self.id = id

        self.intervaloProd = 1
        # self.intervaloProd = random.randrange(1,10)
        # Mudar para ler de arquivo talvez
        f = open(self.nome+".txt", "r")
        self.armazenamento = int(f.readline())
        #self.armazenamento = 50

        self.chanceFalha = 0
        self.tempoDemora = 0

    def desejaEfetivar(self, pedido):
        global locks
        if locks[self.id].acquire(blocking=True, timeout=13) == False:
            print(str(self.id) + "nao conseguiu acessar o lock")
            return False, self.nome + " nao conseguiu acessar o lock"

        if self.armazenamento < pedido[str(self.id)]:
            locks[self.id].release()
            return False, self.nome + " nao possui material o suficiente"

        rollFalha = random.randrange(0, 100)
        if rollFalha < self.chanceFalha:
            locks[self.id].release()
            return False, self.nome + "falhou",
        
        f = open(self.nome+".txt", "w")
        f.write(str(self.armazenamento - pedido[str(self.id)]))
        f.close()

        time.sleep(self.tempoDemora)

        return True, ""
    
    def efetivar(self):
        f = open(self.nome+".txt", "r")
        self.armazenamento = int(f.readline())
        locks[self.id].release()

    def abortar(self):
        locks[self.id].release()


class Server:
    def __init__(self):
        self.pedidos = []
        self.contPedidos = 0
        self.contRecursos = 0

        self.produtores = []
        self.criaRecurso("Mineirador de pedra", self.contRecursos)
        self.criaRecurso("Lenhador de carvalho", self.contRecursos)
        self.criaRecurso("Pescador de bagre", self.contRecursos)

    def criaRecurso(self, nome, id):
        global locks

        self.produtores.append(ProdutorRecurso(nome, id))
        locks.append(threading.Lock())
        self.contRecursos += 1

    @Pyro5.server.expose
    def consultaEstoque(self):
        estoque = "Estoque:\n"
        for produtor in self.produtores:
            estoque += (str(produtor.id) + " " + produtor.nome 
                        + " " + str(produtor.armazenamento) + "\n")
            
        return estoque, self.contRecursos
    
    @Pyro5.server.expose
    def fazerPedido(self, pedido):
        respostas = []

        # Primeira etapa: pergunta se todos desejam efetivar
        for i in range(self.contRecursos):
            if pedido[str(i)] != 0:
                respostas.append(self.produtores[i].desejaEfetivar(pedido))
            else:
                respostas.append((True, ""))
        
        # Checa os votos de todos
        for resposta in respostas:
            # Caso um queira abortar, aborta todos
            if resposta[0] == False:
                for i in range(self.contRecursos):
                    if pedido[str(i)] != 0 and respostas[i][0] == True:
                        self.produtores[i].abortar()
                return resposta[1]
        
        # Caso chegue aqui, todos votaram para efetivar
        for i in range(self.contRecursos):
            if pedido[str(i)] != 0:
                self.produtores[i].efetivar()
        return "Seu pedido foi feito com sucesso, novo estoque:\n" + (self.consultaEstoque())[0]

    # Teste de conexão
    @Pyro5.server.expose
    def alo(self):
        print('---------------------')
        print('Recebi alo, devolvendo ola')
        return "ola"


# Inicializa o logger
logging.basicConfig(stream=sys.stderr,
                    format="[%(asctime)s,%(name)s,%(levelname)s] %(message)s")
log = logging.getLogger("Pyro5")
log.setLevel(logging.WARNING)

# Cria o daemon e se registra
daemon = Pyro5.api.Daemon()
server = Server()
uriServer = daemon.register(server)
print('URi do server:')
print(uriServer)
print('---------------------\n')

# Loclaiza o servidor de nomes
uriNS = Pyro5.api.locate_ns()
print('Nameserver:')
print(uriNS)

# Se registra no servidor de nomes
uriNS.register("ServidorProdutores", uriServer)
print('---------------------')

# -------------- teste leiloes
# server.imprimeLeiloes()

print('Aguardando requests\n')
daemon.requestLoop()
