/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.tiago.leilao;

import com.here.oksse.OkSse;
import com.here.oksse.ServerSentEvent;
import java.io.IOException;
import java.util.Scanner;
import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.sse.SseEventSource;
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
    
    private static OkSse okSse = null;
    
    private static ServerSentEvent sseCadastroLeilao = null;
    
    private static final ServerSentEvent.Listener sseListener = new ServerSentEvent.Listener() {
        @Override
        public void onOpen(ServerSentEvent sse, Response response) {
            // When the channel is opened
            //System.out.println("Escutando por eventos SSE");
        }

        @Override
        public void onMessage(ServerSentEvent sse, String id, String event, String message) {
            // When a message is received
            System.out.println("aaaa" + message);
        }
        @Override
        public void onComment(ServerSentEvent sse, String comment) {
           // When a comment is received
            System.out.println("aaaa" + comment);
        }
        @Override
        public boolean onRetryTime(ServerSentEvent sse, long milliseconds) {
            return true; // True to use the new retry time received by SSE
        }
        @Override
        public boolean onRetryError(ServerSentEvent sse, Throwable throwable, Response response) {
            return true; // True to retry, false otherwise
        }
        @Override
        public void onClosed(ServerSentEvent sse) {
            // Channel closed
        }

        @Override
        public Request onPreRetry(ServerSentEvent sse, Request rqst) {
            //throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
            return rqst;
        }
    };
    
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
        Response response = null;
        try {
            response = client.newCall(request).execute();
            String resposta = response.body().string();
            if(resposta != null)
                System.out.println(resposta);
        } catch (IOException ex) {
            System.out.println("Erro: " + ex);
            if(response != null)
                response.close();
        }
    }
    private static SseEventSource source = null;
    private static WebTarget target = null;
    private static Client client = null;
    private static Thread thread_sse = null;
    public static void startSSE()
    {
        client = ClientBuilder.newClient();
        target = client.target(urlServer + "/stream?channel="+nome);
        thread_sse = new Thread() {

            @Override
            public void run() {
                try {
                    source = SseEventSource.target(target).build();
                    source.register((inboundSseEvent) -> {
                        System.out.println(inboundSseEvent.readData());
                    });
                    source.open();
                }catch(Exception e)
                {
                    e.printStackTrace();
                }
            }
          };
        thread_sse.start();
    }
    
    public static void closeSSEs()
    {
        if(thread_sse != null)
        {
            thread_sse.interrupt();
            source.close();
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
                        startSSE();
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
        
        closeSSEs();
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
