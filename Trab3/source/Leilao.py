# Leilao da aplicacao de leiloes.
# Deve ter um preco atual.
# Tambem deve ser possivel realizar lances sobre o leilao, aumentando o preco atual.
# Deve ser possivel verificar o valor atual do leilao.
# Ao acabar o tempo, deve fechar.

# Retornos:
# 0: Sucesso
# 1: Erro desconhecido
# 2: Valor invalido
# 3: Objeto finalizado

class Leilao:
    def __init__(self, val, tempo, dono):
        self.__val = val
        self.__tempo = tempo
        self.__dono = dono
        self.__comprador_atual = ""

    def valor_atual(self):
        return self.__val

    def comprador_atual(self):
        return self.__comprador_atual

    def dono(self):
        return self.__dono

    def realizar_lance(self, val, comprador):
        if self.__tempo <= 0:
            return 3
        if val < self.valor_atual():
            return 2
        self.__val = val
        self.__comprador_atual = comprador
        return 0

    def tick_tempo(self):
        if(self.__tempo > 0):
            self.__tempo = self.__tempo - 1
        if(self.__tempo <= 0):
            return 3
        return 0
        