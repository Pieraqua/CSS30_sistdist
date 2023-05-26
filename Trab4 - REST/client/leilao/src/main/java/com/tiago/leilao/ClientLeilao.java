/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.tiago.leilao;

import java.io.IOException;
import java.util.Scanner;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import org.json.JSONObject;

/**
 *
 * @author omati
 */
public class ClientLeilao {
    
    private static String nome = "";
    private static boolean registrado = false;
    private static String urlServer = "http://127.0.0.1:5000";
    
    private static void chamadaCliente(String corpo, String url, String metodo)
    {
        OkHttpClient client = new OkHttpClient().newBuilder()
                .build();
        MediaType mediaType = MediaType.parse("application/json");
        RequestBody body = null;
        if(corpo != null)
            body = RequestBody.create(mediaType, corpo);
        
        Request request = new Request.Builder()
                // ---------------------------------- mudar o endereço
                .url(urlServer + url)
                .method(metodo, body)
                .addHeader("Content-Type", "application/json")
                .build();
        
        try {
            Response response = client.newCall(request).execute();
            String resposta = response.body().string();
            if(resposta != null)
                System.out.println(resposta);
        } catch (IOException ex) {
            System.out.println("Erro: " + ex);
        }
    }
    
    
    public static void main(String[] args) {
        
        Scanner sc=new Scanner(System.in);
        int opcao = 1;
        while(opcao != 0)
        {
            System.out.println("****Menu:****");
            System.out.println("1: Se registrar no servidor");
            System.out.println("2: Consultar leiloes ativos");
            System.out.println("3: Cadastrar um produto para leilão");
            System.out.println("4: Dar lance em leilão");
            System.out.println("5: Testar conexao");
            System.out.println("0: Encerrar o programa");
            System.out.println("");
            
            opcao = sc.nextInt();
            sc.nextLine();
            
            switch (opcao) {
                case 1 -> {
                    if(registrado == false)
                    {
                        System.out.println("---------------------");
                        System.out.println("Se registrando no server");
                        System.out.println("Digite seu nome: ");
                        nome = sc.nextLine();
                        JSONObject corpo = new JSONObject();
                        corpo.append("nome", nome);
                        chamadaCliente(corpo.toString(), "/cliente", "POST");
                        registrado = true;
                    }
                    else
                    {
                        System.out.println("Usuario ja registrado");
                    }
                }
                case 2 -> {
                    chamadaCliente(null, "/leilao", "GET");
                }
                case 3 -> {
                    /*
                    System.out.println("Nome: ");
                    String nomeP = sc.nextLine();
                    System.out.println("Descricao: ");
                    String descricao = sc.nextLine();
                    System.out.println("Valor: ");
                    String valor = sc.nextLine();
                    System.out.println("Tempo: ");
                    String tempo = sc.nextLine();
                    */
                    String nomeP = "aaa";
                    String descricao = "bbb";
                    String valor = "300";
                    String tempo = "30";
                    
                    JSONObject corpo = new JSONObject();
                    corpo.append("nome", nomeP);
                    corpo.append("descricao", descricao);
                    corpo.append("val", valor);
                    corpo.append("tempo", tempo);
                    corpo.append("dono", nome);
                    
                    chamadaCliente(corpo.toString(), "/produto", "POST");
                }
                case 4 -> {
                    System.out.println("Ainda nao implementado.");
                    System.out.println("Ainda nao implementado.");
                }
                case 5 -> {
                    System.out.println("---------------------");
                    System.out.println("Enviando alo, esperando resposta...");
                    chamadaCliente(null, "/ping", "GET");
                }
                case 0 -> {
                }
                default -> {
                    System.out.println("Digite uma opcao valida");
                    System.out.println("---------------------\n");
                }
            }
        }
    }
    /*
    opcao = input()

    elif opcao == '4':
        cod = input('Cod do produto: ')
        valor = input('Valor: ')
        assinada = pkcs1_15.new(client.chavePrivada).sign(SHA256.new(b'Assinado'))
        retorno = serverLeilao.darLance(int(cod), int(valor), client.registroCliente['uri'], list(assinada))
        if retorno == 0:
            print('Lance realizado com sucesso\n')
        else:
            print('Erro ao dar lance: ' + str(retorno) + '\n')
    elif opcao == '5':
        print('Testando funcao alo:')
        serverLeilao.alo(callback)
    elif opcao == '0':
        sys.exit()
    */
}
