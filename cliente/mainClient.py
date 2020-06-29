from ClaseCliente import ClientManagement
from Clasetramas import HandlingInstructions
from Globales import*
import logging
import time
import threading
import os

mainchat = True 


logging.basicConfig(level=logging.INFO, format='\n[%(levelname)s] (%(threadName)-10s) %(message)s')

main_Client = ClientManagement(MQTT_HOST, MQTT_USER, MQTT_PASS, MQTT_PORT, TCP_PORT, user=FILE_USERS, rooms=FILE_ROOMS, group=GROUP_NUMBER)
main_Client.server_mqtt()
main_Client.connect()
main_Client.subscription()
print(main_Client.subscribers())
print (main_Client.get_userClient())


def tramaAlive(topic_c = 'comandos', grupo = '09'):
    global mainchat
    trama = HandlingInstructions(code='ALIVE', transmitter=main_Client.get_userClient())
    cont =0
    main_Client.ackactivado = False
    while cont<205:
        while main_Client.ackactivado:
            cont+=1
            main_Client.publish_data(topic_c, grupo, trama.get_finally_code())
            time.sleep(2)
            if cont >3:
                cont =0
                main_Client.ackactivado = False
        while not main_Client.ackactivado:
            if cont<= 4:
                main_Client.publish_data(topic_c, grupo, trama.get_finally_code())
                cont+=1
                time.sleep(2)
            else:
                main_Client.publish_data(topic_c, grupo, trama.get_finally_code())
                cont+=1
                time.sleep(0.1)
                if cont>205:
                    break
    logging.error('No hay server')
    mainchat = False

threading.Thread(name = 'Trama ALIVE',target =tramaAlive,args = (()),daemon = True).start()


main_Client.banner1()



try:
    while mainchat:
        try:
            main_Client.banner2()
            opcion = int(input('Escoja una opcion: '))
            
            if opcion == 1 :
                main_Client.banner3()
                destino = int(input('Enviar a usuario o sala? '))
                x, y = main_Client.destinatario(destino)
                mensaje_a_enviar = str(input('Escriba el mensaje:\n\n'))
                main_Client.publish_data(y, str(x), mensaje_a_enviar)
                logging.info("El mensaje ha sido enviado")

            elif opcion == 2:
                duracion = int(input('Ingrese la duracion en segundos(max 30): '))
                if duracion <= 30:
                    main_Client.banner3()
                    destino = int(input('Enviar a usuario o sala? '))
                    x, y = main_Client.destinatario(destino)
                    logging.info('Grabe su mensaje')
                    os.system('arecord -d '+ str(duracion)+ ' -f U8 -r 8000 audior.wav')
                    logging.info('Mensaje grabado')
                    negociacion_audio = HandlingInstructions(code='FTR', transmitter=main_Client.get_userClient(), addressee=str(x), file_size=str(os.stat('audior.wav').st_size))
                    main_Client.publish_data('comandos/09', str(x), negociacion_audio.get_finally_code())
                    time.sleep(1)          
                else:
                    logging.warning('Valor incorrecto. Intente de nuevo')    
            elif opcion == 3:
                break
            else:
                logging.warning('Opcion incorrecta. Intente de nuevo')
        except ValueError:
            if mainchat:
                logging.warning('Error mal ingreso espere')
            else:
                logging.warning('Servidor fuera de linea')
        time.sleep(DEFAULT_DELAY)
except KeyboardInterrupt:
    pass

finally:
    logging.warning("Saliendo del programa...")
    main_Client.disconnect()