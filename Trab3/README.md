# Descricao

Trabalho 3 de Sistemas Distribuidos. Middleware Pyro.

# Requisitos

- Executar um processo servidor e ao menos tres processos clientes
- Utilizar PyRO para comunicacao cliente-servidor
- Cada cliente pode participar e criar leiloes
- Havera apenas um servidor DNS na maquina, criado pelo processo servidor

# Servidor

O servidor gerenciara os leiloes criados, cadastrara usuarios e registrara lances em leiloes.

## Metodos do Servidor

- Cadastro de Usuario
- Consulta de leiloes ativos
- Cadastro de produto para leilao
- Lance em um produto


# Cliente

O cliente ira se cadastrar no servidor em sua primeira conexao. Ele podera criar leiloes e lances em leiloes.

## Metodos do Cliente

- Notificacao de eventos

