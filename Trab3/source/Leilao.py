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
    def __init__(self, cod, nome, descricao, val, tempo, dono):
        self.__cod = cod
        self.__nome = nome
        self.__descricao = descricao
        self.__val = val
        self.__tempo = tempo
        self.__dono = dono
        self.__comprador_atual = None
        self.__interessados = [dono]

    def valor_atual(self):
        return self.__val

    def comprador_atual(self):
        return self.__comprador_atual

    def dono(self):
        return self.__dono
    
    def interessados(self):
        return self.__interessados
    
    def tempo(self):
        return self.__tempo
    
    def nome(self):
        return self.__nome
    
    def retornaInformacoes(self):
        retorno = ""
        retorno += 'Codigo: ' + str(self.__cod)
        retorno += '\n' + 'Nome: ' + self.__nome
        retorno += '\n' + 'Descricao: ' + self.__descricao
        retorno += '\n' + 'Valor atual: ' + str(self.__val)
        retorno += '\n' + 'Tempo restante: ' + str(self.__tempo)
        retorno += '\n' + 'Dono: '
        if self.__dono == None:
            retorno += "SEM DONO"
        else:
            retorno += self.__dono["nome"]
        retorno += '\n' + 'Comprador atual: '
        if self.__comprador_atual == None:
            retorno += "SEM COMPRADOR ATUAL"
        else:
            retorno += self.__comprador_atual["nome"]

        retorno += '\n' + 'Interessados: '
        for i in self.__interessados:
            retorno += '\n' + i["nome"]
        retorno += '\n'
        return retorno

    def realizar_lance(self, val, comprador):
        if self.__tempo <= 0:
            return 3
        if val <= self.valor_atual():
            return 2
        self.__val = val
        self.__comprador_atual = comprador

        for item in self.__interessados:
            if(comprador["uri"] == item["uri"]):
                return 0
        self.__interessados.append(comprador)
        return 0

    def tick_tempo(self):
        if(self.__tempo > 0):
            self.__tempo = self.__tempo - 1
        if(self.__tempo <= 0):
            return 3
        return 0
        