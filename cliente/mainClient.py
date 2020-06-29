from ClaseCliente import ClientManagement
from Clasetramas import HandlingInstructions
from Globales import*
import logging
import time
import threading
import os


ackactivado = False
mainchat = True 


logging.basicConfig(level=logging.INFO, format='\n[%(levelname)s] (%(threadName)-10s) %(message)s')

main_Client = ClientManagement(MQTT_HOST, MQTT_USER, MQTT_PASS, MQTT_PORT, user=FILE_USERS, rooms=FILE_ROOMS, group=GROUP_NUMBER)
main_Client.server_mqtt()
main_Client.connect()
main_Client.subscription()
print(main_Client.subscribers())

main_Client.banner1()

try:
    while True:
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
                    os.system('arecord -d '+ str(duracion)+ ' -f U8 -r 8000 audioparaenviar.wav')
                    logging.info('Mensaje grabado')
                    negociacion_audio = HandlingInstructions(code='FTR', transmitter='201700796', addressee=str(x), file_size=str(os.stat('audioparaenviar.wav').st_size))
                    main_Client.publish_data('comandos/09', str(x), negociacion_audio.get_finally_code())
                    time.sleep(1)          
                else:
                    logging.warning('Valor incorrecto. Intente de nuevo')    
            elif opcion == 3:
                break
            else:
                logging.warning('Opcion incorrecta. Intente de nuevo')
        except ValueError:
            logging.error('Error: Respuesta invalida')
        time.sleep(DEFAULT_DELAY)
except KeyboardInterrupt:
    pass

finally:
    logging.warning("Saliendo del programa...")
    main_Client.disconnect()