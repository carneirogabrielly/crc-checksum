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
import numpy as nps
from utils import *

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)

imageR = "imgs/image.png"

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        print("Abriu a comunicação")
        
        #prevenção de erros
        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(1)   
                
                
                
                
         ##### VERIFICAR SE O SERVIDOR ESTÁ VIVO #####
        print("Verificando se o servidor está vivo")
        # Espera resposta do servidor
        pacote0 = make_pack_server(True)
        verifica = True
        start_time = time.time()
        while verifica:
            tam = com1.rx.getBufferLen()
            atraso = time.time() - start_time
            if tam >= 1:
                print("Servidor está ativo.")
                break
            else:
                if atraso >= 5:
                    resposta = input("Servidor Inativo. Tentar novamente? s/n?").lower()
                    if resposta == 's':
                        com1.sendData(pacote0)  ###vai substituir pelo pacote
                        print("Verificando se o servidor está vivo")
                        start_time = time.time()
                    elif resposta == 'n':
                        print("Encerrando comunicação")
                        com1.disable()
                        verifica = False
                        
        com1.rx.clearBuffer()
        
        #aqui você deverá gerar os dados a serem transmitidos. 
        
        #txBuffer = imagem em bytes!
        mensagem = open(imageR, 'rb').read()
        
        #########AQUI VOU CHAMAR A FUNÇÃO QUE CRIA OS PACOTES#########
        #Vai me devolver uma lista de pacotes
        fragmentos = fragmenta(mensagem)
        pacotes = make_pack(fragmentos)
        
        while verifica:
            for i in range(len(pacotes)):
                #vou enviar o pacote
                
                #------------------------ erro ordem do pacote ---------------------------------#
                com1.sendData(pacotes[i+1])
                # com1.sendData(pacotes[i])
                #------------------------------------------------------------------------------#
                #esperar a resposta
                #pegar o head
                
                
                #### ------------------ tentativa de A+ -------------------------------#
                print(com1.rx.getBufferLen())
                time0 = time.time()
                while (com1.rx.getBufferLen() < 15):
                    atraso1 = time.time() - time0
                    if atraso1 > 2:
                        com1.sendData(pacotes[i])
                        time.sleep(1)
                   
                    
                #----------------------------------------------------------------------#
                if com1.rx.getBufferLen() >= 15:    
                    head, _, eop = carrega_pacote(com1)
                    #verificar o head
                    if head[3] == 0:
                        print("Pacote {} enviado com sucesso" .format(i+1))
                    else:
                        print(f"Erro com o pacote {i+1}")
                        verifica = False
                        break
                    
            verifica = False
            
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
