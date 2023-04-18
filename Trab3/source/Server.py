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

class Server:
    def __init__(self):
        self.__leiloes = []

    def criar_leilao(self, val, dono):
        print("Foi criado um leilao com valor " + val + ". Dono: " + dono + ".\n")
        self.__leiloes.append(Leilao(val, 30, dono))
        return 0

    def registrar_cliente():
        print("Foi registrado um cliente\n")

        return 0
    
