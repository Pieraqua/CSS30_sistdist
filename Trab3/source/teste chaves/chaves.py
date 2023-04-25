
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

chavePrivada = RSA.generate(2048)
chavePublica = chavePrivada.public_key()
lista = list(chavePublica.public_key().export_key())

assinada = pkcs1_15.new(chavePrivada).sign(SHA256.new(b'Hello World'))

try:
    pkcs1_15.new(RSA.import_key(bytes(lista))).verify(SHA256.new(b'Hello World'), assinada)
    print('Assinatura valida')
except:
    print('Assinatura invalida')