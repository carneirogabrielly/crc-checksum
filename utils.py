from aplicacao import *
from enlace import enlace
import crcmod
import datetime

# Definindo a função de CRC-16 (Modbus, por exemplo)

def calcula_crc(payload):
    crc16 = crcmod.predefined.mkCrcFun('modbus')
    crc = crc16(payload)
    crc_bytes = crc.to_bytes(2, byteorder='big')
    return crc_bytes[0], crc_bytes[1]
    

def fragmenta(mensagem: bytes):
    tamanho = len(mensagem)
    inteiro = tamanho // 50  # Número de fragmentos completos
    resto = tamanho % 50  # Quantidade de bytes restantes
    fragmentos = []

    # Adicionar fragmentos de tamanho 50
    for i in range(inteiro):
        fragmentos.append(mensagem[i * 50: (i + 1) * 50])

    # Adicionar fragmento com o restante
    if resto > 0:
        fragmentos.append(mensagem[inteiro * 50:])

    return fragmentos


def carrega_pacote(com1):
    head, tamanho_head = com1.getData(12)
    tamanho_payload = head[2]
        #pegando o payload
    payload,_ = com1.getData(tamanho_payload)
        #pegando o eop
    eop,_ = com1.getData(3)

    return head, payload, eop

#----------------------CLIENT------------------------
def make_pack(fragmentos : list):
    head = bytearray(12)
    eop = b'\x46\x49\x4D'  # EOP correto
    pacotes = []

    if len(fragmentos) > 255:
        raise ValueError("Número de fragmentos não pode exceder 255.")

    for i, fragmento in enumerate(fragmentos):
        if len(fragmento) > 255:
            raise ValueError(f"Fragmento {i + 1} excede o tamanho máximo de 255 bytes.")

        head[0] = len(fragmentos)  # Número total de fragmentos (máximo 255)
        head[1] = i + 1  # Índice do fragmento (começa do 1)
        head[2] = len(fragmento)  # Tamanho do fragmento/payload (máximo 255)
        head[3] = 0  # indica se houve erro  [0 sem erro, 1 para erro]
        
        payload = fragmento  # O fragmento como payload
        
        #--------------- CRC -----------------------#
        head[4], head[5] = calcula_crc(payload)
        head[6] = len(fragmento) + 15
        #-------------------------------------------#
        
        pacote = bytearray(head) + bytearray(payload) + eop  # Concatenar tudo
        
        pacotes.append(pacote)  # Adicionar o pacote à lista
    
    return pacotes

def log_dado(pacote):
    with open("log_transmissao.txt", "a") as file:
        # Obter o horário atual para cada entrada de log
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Escreve o dado recebido e o timestamp no arquivo
        file.write(f"[{timestamp}] envio / dado / tamanho de bytes: {pacote[6]} / pacote enviado: {pacote[1]} / total de pacotes: {pacote[0]} / CRC: {pacote[4]}{pacote[5]} \n")
        
#---------------------SERVER-------------------------
def verifica_pack(head, payload, eop, numero_esperado):
    qtd_pacotes = head[0]
    numero_pacote = head[1]
    if numero_esperado > numero_pacote:
        print("ERRO -- Ordem errada de pacote")
        return False, 'ordem menor'
    if numero_esperado < numero_pacote:
        print("ERRO -- Ordem errada de pacote")
        return False, 'ordem maior'
    if eop != b'\x46\x49\x4D':
        print("ERRO -- tamanho do payload diferente")
        return False, 'tamanho_payload'
    
    ######----- erro de crc hardcoded ---------#######
    # payload = b'\x46\x49\x4D'
    ######-------------------------------------#######
    
    #-----------CRC-------------#
    crc1, crc2 = calcula_crc(payload)
    if (crc1 != head[4]) or (crc2 != head[5]):
        print("Erro de CRC")
        return False, f'{calcula_crc(payload)}'
    #--------------------------#
    return True, 'ok'
        
def make_pack_server(verifica, msg):
    head = bytearray(12)
    eop = b'\x46\x49\x4D'
    payload = b''
    head[0] = 1
    head[1] = 1
    if verifica:
        head[3] = 0
    else:
        #se for ordem menor, envia 1
        if msg == 'ordem menor':
            head[3] = 1
        elif msg == 'ordem maior':
            head[3] = 2
        #se o tamanho do payload for errado, envia 3
        elif msg == "tamanho_payload":
            head[3] = 3
        #se for erro de crc, envia 4
        else: 
            head[3] = 4
    
    head[4], head[5] = calcula_crc(payload)
    head[6] = 15 #quantidade total de bytes
    
        
    pacote = bytearray(head) + eop
    return pacote

def log_recebimento (head, mensagem):
    with open("log_transmissao.txt", "a") as file:
        # Obter o horário atual para cada entrada de log
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Escreve o dado recebido e o timestamp no arquivo
        file.write(f"[{timestamp}] recebimento / {mensagem} / tamanho de bytes: {head[6]} \n")
        