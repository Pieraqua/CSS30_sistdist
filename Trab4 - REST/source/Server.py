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
from flask_sse import sse
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

Server = Flask(__name__)
Server.config["REDIS_URL"] = "redis://localhost"
Server.register_blueprint(sse, url_prefix='/stream')

def send_message(message = '', channel = ''):
    with Server.app_context():
        if(message != '' ):
            sse.publish(message, type='message', channel=channel)
            print("mensagem sse " + str(message))
            return 'sent message ' + str(message)
        else:
            return 'subscribed to sse-stream'

class ServerData:
    leiloes = []
    usuarios = []
    cod = 0

    def getLeiloes(self):
        return self.leiloes

    def getCod(self):
        return self.cod
    def setCod(self, val):
        self.cod = val

    def imprimeLeiloes(self):
        print('---------------------')
        print('Imprimindo leiloes: ')
        leiloes = ""
        for leilao in self.getLeiloes():
            leiloes += leilao.retornaInformacoes()
            leiloes += "    ---------------------"
        print(leiloes)

    # Funcao de encerrar leiloes
    def verifica_leiloes(self):
        for leilao in self.leiloes:
            if(leilao.tick_tempo() == 3):
                # Acabou tempo do leilao
                print("Leilao " + leilao.nome() + " encerrado.")

                for item in leilao.interessados():
                    print("notificar " + item["nome"][0])
                    print(leilao.nome())
                    print(leilao.comprador_atual())
                    if(leilao.comprador_atual() != None):
                        send_message({"message" : "Leilao " + leilao.nome() + " encerrado. Ganhador: " 
                                      + leilao.comprador_atual()["nome"][0]}, channel = item["nome"][0])
                    else:
                        send_message({"message" : "Leilao " + leilao.nome() 
                                      + " encerrado. Ganhador: Ninguem."}, channel=item["nome"][0])
                self.leiloes.remove(leilao)

server = ServerData()

# Create the background scheduler
scheduler = BackgroundScheduler()
# Create the job
scheduler.add_job(func=server.verifica_leiloes, trigger="interval", seconds=1)
# Start the scheduler
scheduler.start()

# /!\ IMPORTANT /!\ : Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

#-------------------------------------------#
#1: Se registrar no servidor
@Server.post("/cliente")
def registrarCliente():
    user = request.get_json()
    print('Tentativa de registro:')
    server.usuarios.append(user)
    print('---------------------')
    print("Foi registrado o cliente: " + user["nome"][0])
    return "Cliente Registrado"

#2: Consultar leiloes ativos
@Server.get("/leilao")
def consultaLeiloes():
    print('---------------------')
    print('Enviando lista de leiloes')
    server.imprimeLeiloes()
    leiloes = ""
    for leilao in server.getLeiloes():
        leiloes += leilao.retornaInformacoes()
        leiloes += "    ---------------------"

    print(leiloes)
    return leiloes

#3: Cadastrar um produto para leilão
@Server.post("/produto")
def cadastraLeilao():
    pkg = request.get_json()
    usuario = None
    print(pkg)
    for item in server.usuarios:
        if item["nome"] == pkg["dono"]:
            usuario = item

    print(usuario)
    if usuario == None:
        print('---------------------')
        print('Erro ao cadastrar leilao, usuario invalido\n')
        return "Erro ao cadastrar leilão, usuario invalido"
    
    leilao = Leilao(server.getCod(), pkg["nome"][0], pkg["descricao"][0], int(pkg["val"][0]), int(pkg["tempo"][0]), usuario)
    server.leiloes.append(leilao)
    server.setCod(server.getCod() + 1)
    print('Foi cadastrado o ' + pkg["nome"][0] + ' de ' + usuario["nome"][0])

    interessados = server.usuarios

    for item in interessados:
        print("criado novo leilao " + leilao.nome())
        print(leilao.nome())
        print(leilao.dono())
        send_message({"message" : "Leilao " + str(leilao.nome()) 
                      + " criado. Dono: " + str(leilao.dono()["nome"][0])}, channel=item["nome"][0])


    return "Leilao cadastrado"

#4: Dar lance em leilão
@Server.post("/lance")
def darLance():
    pkg = request.get_json()
    usuario = None
    for item in server.usuarios:
        if item["nome"] == pkg["nome"]:
            usuario = item

    if usuario == None:
        print('---------------------')
        print('Erro ao dar lance, usuario invalido\n')
        return "Erro ao dar lance, usuario invalido"

    try:
        leilao = server.leiloes[pkg["cod"]]
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
            print("Interessado no lance: " + item["nome"])
            send_message({"message" : "Leilao " + leilao.nome() 
                          + " com novo lance. Lance por: " 
                          + usuario["nome"][0]}, type='publish', channel=item["nome"][0])

        return "Lance dado com sucesso"

#5: Testar conexao
@Server.get("/ping")
def alo():
    print('---------------------')
    print('Recebi alo, devolvendo alo')
    return "Alo"