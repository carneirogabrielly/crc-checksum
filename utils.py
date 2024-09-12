from aplicacao import *
from enlace import enlace
import crcmod

# Definindo a função de CRC-16 (Modbus, por exemplo)

def calcula_crc(payload):
    crc16 = crcmod.predefined.mkCrcFun('modbus')
    crc_int = crc16(payload)
    crc = crc_int.to_bytes(2, byteorder='big')
    crc1 = crc16[:len(crc)//2]
    crc2 = crc16[(len(crc)//2)+1:]
    return crc1, crc2
    

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
        head[2] = len(fragmento)  # Tamanho do fragmento (máximo 255)
        head[3] = 0  # indica se houve erro  [0 sem erro, 1 para erro]
        
        payload = fragmento  # O fragmento como payload
        
        #--------------- CRC -----------------------#
        head[4], head[5] = calcula_crc(payload)
        #-------------------------------------------#
        
        
        pacote = bytearray(head) + bytearray(payload) + eop  # Concatenar tudo
        
        pacotes.append(pacote)  # Adicionar o pacote à lista
    
    return pacotes
#---------------------SERVER-------------------------
def verifica_pack(head, payload, eop, numero_esperado):
    qtd_pacotes = head[0]
    numero_pacote = head[1]
    if numero_esperado != numero_pacote:
        print("ERRO -- Ordem errada de pacote")
        return False
    if eop != b'\x46\x49\x4D':
        print("ERRO -- tamanho do payload diferente")
        return False
    
    #-----------CRC-------------#
    crc1, crc2 = calcula_crc(payload)
    if (crc1 != head[4]) or (crc2 != head[5]):
        print("Erro de CRC")
        return False
    #--------------------------#
    return True
        
def make_pack_server(verifica):
    head = bytearray(12)
    eop = b'\x46\x49\x4D'
    if verifica:
        head[3] = 0
    else:
        head[3] = 1
    pacote = bytearray(head) + eop
    return pacote