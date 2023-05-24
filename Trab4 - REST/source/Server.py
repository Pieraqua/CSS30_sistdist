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
# 4: Cliente nao cadastrado
# 5: Problema de assinatura
# 6: Operacao invalida

# flask --app Server.py run

import threading
import time
from Leilao import Leilao
from flask import Flask, request, jsonify

Server = Flask(__name__)

leiloes = []
usuarios = []
cod = 0

def imprimeLeiloes():
    print('---------------------')
    print('Imprimindo leiloes: ')
    leiloes = ""
    for leilao in leiloes:
        leiloes += leilao.retornaInformacoes()
        leiloes += "    ---------------------"
    print(leiloes)

def leilaoFinalizado(leilao):
    interessados = leilao.interessados()
    print('---------------------')
    print('Leilao: ' + leilao.nome() + ' finalizado, notificando interessados')
    for item in interessados:
        uri = item["uri"]
        user = Pyro5.api.Proxy(uri)
        user.notificaFim(leilao.retornaInformacoes())

def timerLeilao(leilao, servidor, tempo):
    for i in range(tempo):
        leilao.tick_tempo()
        time.sleep(1)
    
    servidor.leilaoFinalizado(leilao)
    leiloes.remove(leilao)

#-------------------------------------------#

#1: Se registrar no servidor
@Server.post("/cliente")
def registrarCliente():
    user = request.get_json()
    print('Tentativa de registro:')
    usuarios.append(user)
    print('---------------------')
    print("Foi registrado o cliente: " + user["nome"])
    return 201

#2: Consultar leiloes ativos
@Server.get("/leilao")
def consultaLeiloes():
    print('---------------------')
    print('Enviando lista de leiloes')
    imprimeLeiloes()
    leiloes = ""
    for leilao in leiloes:
        leiloes += leilao.retornaInformacoes()
        leiloes += "    ---------------------"
    return leiloes

#3: Cadastrar um produto para leilão
@Server.post("/produto")
def cadastraLeilao():
    pkg = request.get_json()
    usuario = None
    for item in usuarios:
        if item["nome"] == pkg["dono"]:
            usuario = item

    if usuario == None:
        print('---------------------')
        print('Erro ao cadastrar leilao, usuario invalido\n')
        return "Erro ao cadastrar leilão, usuario invalido"
    
    leilao = Leilao(cod, pkg["nome"], pkg["descricao"], pkg["val"], pkg["tempo"], usuario)
    leiloes.append(leilao)
    cod = cod + 1
    print('---------------------')
    print('Foi cadastrado o ' + pkg["nome"] + ' de ' + usuario["nome"])

    interessados = usuarios

    for item in interessados:
        uri = item["uri"]
        user = Pyro5.api.Proxy(uri)
        user.notificaNovo(leilao.retornaInformacoes())

    # Nao consegui um jeito melhor de fazer isso.
    p = threading.Thread(target=timerLeilao(leilao, leilao.tempo()))
    p.start()
    #return 0

#4: Dar lance em leilão
@Server.post("/lance")
def darLance():
    pkg = request.get_json()
    usuario = None
    for item in usuarios:
        if item["nome"] == pkg["nome"]:
            usuario = item

    if usuario == None:
        print('---------------------')
        print('Erro ao dar lance, usuario invalido\n')
        return "Erro ao dar lance, usuario invalido"

    try:
        leilao = leiloes[pkg["cod"]]
    except:
        print('---------------------')
        print('Erro ao dar lance, cod de leilao invalido\n')
        return "Erro ao dar lance, cod de leilao invalido"
    
    if leilao.dono() == usuario:
        print('---------------------')
        print('Erro ao dar lance, dono nao pode dar lance\n')
        return "Erro ao dar lance, dono nao pode dar lance"

    print('---------------------')
    print('Dando lance de: ' + usuario["nome"])
    retorno = leilao.realizar_lance(pkg["val"], usuario)
    if retorno == 3:
        print('---------------------')
        print('Erro ao dar lance, leilao finalizado\n')
        return "Erro ao dar lance, leilao finalizado"
    elif retorno == 2:
        print('---------------------')
        print('Erro ao dar lance, valor menor que o lance atual\n')
        return "Erro ao dar lance, valor menor que o lance atual"
    elif retorno == 0:
        print('---------------------')
        print('Lance dado com sucesso')


        interessados = leilao.interessados()
        for item in interessados:
            uri = item["uri"]
            user = Pyro5.api.Proxy(uri)
            user.notificaLance(leilao.retornaInformacoes())
        

        return "Lance dado com sucesso"

#5: Testar conexao
@Server.get("/ping")
def alo():
    print('---------------------')
    print('Recebi alo, devolvendo alo')
    return "Alo"