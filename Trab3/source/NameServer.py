import Pyro5.api as Pyro

def main():
        #Executa o servidor de nomes
        Pyro.start_ns_loop()

        print('Hello Server')

if __name__ == "__main__":
    main()