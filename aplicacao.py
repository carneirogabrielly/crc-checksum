#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
from utils import *
from enlaceRx import *

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)

imageW = 'imgs/img.png'
def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        print("Abriu a comunicação")
        
        #-------prevenção de erro -----------#
        # print("esperando 1 byte de sacrifício")
        # rxBuffer, nRx = com1.getData(1)
        #------------------------------------#
        
        com1.rx.clearBuffer()
           
       #-------- VERIFICANDO SE ESTÁ ATIVO ------------
        handshake = True
        while handshake:
            tam = com1.rx.getBufferLen()
            time.sleep(1)
            if tam >= 1:
                print("Recebi mensagem do cliente")
                print("Enviando confirmação de atividade")
                com1.sendData(make_pack_server(True, 'ok'))
                handshake = False
                
        com1.rx.clearBuffer()
        #---------RECEBENDO AS MENSAGENS -------------
        lista_payload = []
        contador = 1
        contador_de_erro = 0
        recebendo = True
        
        while recebendo:
            
            time.sleep(0.2)
            
            tam = com1.rx.getBufferLen()
            
            if ( tam >= 15):    
                head, payload, eop = carrega_pacote(com1)
                tamanho_da_mensagem = head[0]
                verifica, msg = verifica_pack(head,payload, eop, contador)
                if verifica == True:
                    lista_payload.append(payload)
                    pacote = make_pack_server(True, 'ok')
                    com1.sendData(pacote)
                    print(f'recebi o pacote {contador} corretamente')
                    #log do recebimento
                    log_recebimento(head, 'ok')
                    contador +=1 
                    
                elif verifica == False:
                    #vai identificar qual foi o erro:
                    if (msg == 'ordem menor') or (msg== 'ordem maior'):
                        msg_erro = "ordem errada no pacote"
                    elif msg == "tamanho_payload":
                        msg_erro = "tamanho do payload errado"
                    else: 
                        msg_erro = "crc errado: " + msg
                    ##################################
                    print(f'recebi o pacote {contador} com erro: {msg_erro}')
                    
                    #log do recebimento
                    log_recebimento(head, msg_erro)
                    pacote = make_pack_server(False, msg)
                    
                    com1.sendData(pacote)
                    #log da transmissão
                    log_dado(pacote)
                    
                    contador_de_erro += 1
                    #se errar muitas vezes, encerra a comunicação
                    if contador_de_erro == 20:
                        print("Muitas tentativas falhas. Encerrando recebimento!")
                        recebendo = False
                        
                if contador == tamanho_da_mensagem +1:
                    recebendo = False
        
            else:
                time0 = time.time()
                while (com1.rx.getBufferLen() < 15):
                    atraso1 = time.time() - time0
                    if atraso1 > 20:
                        print(f'Cliente desconectou. Recebimento interrompido')
                        recebendo = False
                        break

            payload_completo = b''.join(lista_payload)
            f = open(imageW, 'wb')
            f.write(payload_completo)
            #fecha arquivo de imagem
            f.close()

        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()