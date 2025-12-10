import socket
from AlphaBot import AlphaBot
import time
import sqlite3
import RPi.GPIO as GPIO

ADDRESS = ('0.0.0.0', 3333)
MAX_CONNECTIONS = 3
BUFFER = 4096

DR=16 #sensore destro
DL=19 #sensore sinistro

comandoPrecedente = 'stop'

ab = AlphaBot()
ab.stop()  # OBBLIGATORIO

def funzione_sensori():
    print("entrato")
    #setto le resistenze in pull up
    GPIO.setup(DR, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(DL, GPIO.IN, GPIO.PUD_UP)

    #while True:
    DR_status= GPIO.input(DR)
    DL_status= GPIO.input(DL)

    if(DR_status==0 or DL_status==0):
        rilevato = 0
        print("rilevato")
    else:
        rilevato = 1

    return rilevato

# creo un socket TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(ADDRESS)
s.listen(MAX_CONNECTIONS)
connection, sender_address = s.accept()


while True:

    message_bin = connection.recv(BUFFER)
    if not message_bin:
        break

    comando = message_bin.decode().strip()
    print(f"comandoPrecedente = {comandoPrecedente}")
    print(f"messaggio ricevuto da client = {comando}")

    vicinanza = funzione_sensori()
    if vicinanza==0:
        ab.stop()
        print("MI FERMO")
        if comando=='avanti':
            ab.stop()
        elif comando == "indietro":
            ab.backward()
        elif comando == "destra":
            ab.right()
        elif comando == "sinistra":
            ab.left()
        
        vicinanza = funzione_sensori()
        comando = message_bin.decode().strip()
        

    if comando == comandoPrecedente:
        continue

    comandoPrecedente = comando

    if comando == "avanti":
        ab.forward()
    elif comando == "indietro":
        ab.backward()
    elif comando == "destra":
        ab.right()
    elif comando == "sinistra":
        ab.left()
    elif comando == "stop":
        ab.stop()
    elif comando == "quadrato" or comando == "avanti_indietro":
        con = sqlite3.connect("./alphaBot_DB.db")
        cur = con.cursor()

        cur.execute(f"SELECT movimento, tempi FROM Comandi WHERE nome_comando LIKE '{comando}'")
        righe = cur.fetchall()
        con.close()

        print(f"righe: {righe}")

        movimenti_str, tempi_str = righe[0]
        lista_mov = [m.strip() for m in movimenti_str.split(',')]
        lista_tempi = [t.strip() for t in tempi_str.split(',')]

        for mov, temp in zip(lista_mov, lista_tempi):
            print(f"Eseguo: {mov} per {temp} secondi")

            if mov == "avanti":
                ab.forward()
                time.sleep(float(temp))
            elif mov == "indietro":
                ab.backward()
                time.sleep(float(temp))
            elif mov == "sinistra":
                ab.left()
                time.sleep(float(temp))
            elif mov == "destra":
                ab.right()
                time.sleep(float(temp))
            elif mov == "aspetta":
                ab.stop()
                time.sleep(float(temp))


        ab.stop()

s.close()
