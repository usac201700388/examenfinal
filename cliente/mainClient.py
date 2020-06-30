#JGPA Importamos las librerias a usar y las clases propias
from ClaseCliente import ClientManagement
from Clasetramas import HandlingInstructions
from Globales import*
import logging
import time
import threading
import os
from Encriptacion_txt import Encriptacion

#EMVB Se define la palabra clave de encriptacion
seguridad = Encriptacion('grupo9')

#JGPA Booleano para activar el menu
mainchat = True 

#JGPA Configuracion del logging
logging.basicConfig(level=logging.INFO, format='\n[%(levelname)s] (%(threadName)-10s) %(message)s')

#JGPA Creamos un objeto para poder iniciar la conexion con el server y mqtt con las credenciales correspondientes
#JGPA Nos suscribimos a los temas e iniciamos la conexion
main_Client = ClientManagement(MQTT_HOST, MQTT_USER, MQTT_PASS, MQTT_PORT, TCP_PORT, user=FILE_USERS, rooms=FILE_ROOMS, group=GROUP_NUMBER)
main_Client.server_mqtt()
main_Client.connect()
main_Client.subscription()

print(main_Client.subscribers())
print (main_Client.get_userClient())

#JGPA Funcion que se ejecuta en un hilo para enviar tramas alive
def tramaAlive(topic_c = 'comandos', grupo = '09'):
    global mainchat
    #JGPA Creamos un objeto para la trama alive
    trama = HandlingInstructions(code='ALIVE', transmitter=main_Client.get_userClient())
    #JGPA Contador para saber cuantas tramas no han recivido ACK
    cont =0
    #JGPA Iniciamos una bool para indicar si recibimos ACK
    main_Client.ackactivado = False
    #JGPA Iniciamos el while para que envie siempre que este corriendo el programa
    while cont<205:
        #JGPA Primero mandamos tramas cada 2 seg
        while main_Client.ackactivado:
            cont+=1
            #JGPA Se envia la trama cada 2 seg con un metodo de la clase
            main_Client.publish_data(topic_c, grupo, trama.get_finally_code())
            time.sleep(2)
            #JGPA Si despues de 3 tramas no hay respuesta se aumenta las velocidad de envio
            if cont >3:
                cont =0
                main_Client.ackactivado = False
        #JGPA WHILE para enviar mas rapido        
        while not main_Client.ackactivado:
            #JGPA Las primeras se envian a 2 segundos
            if cont<= 4:
                main_Client.publish_data(topic_c, grupo, trama.get_finally_code())
                #JGPA Aumenta el contador con cada trama
                cont+=1
                time.sleep(2)
            else:
                #JGPA las tramas se envian mas rapido 
                main_Client.publish_data(topic_c, grupo, trama.get_finally_code())
                cont+=1
                time.sleep(0.1)
                #JGPA depues de 20 seg dejamos de mandar mas tramas
                if cont>205:
                    break
    #JGPA indicamos que el servidor no esta enviando tramas
    logging.error('No hay server')
    #JGPA desactivamos el menu
    mainchat = False

#JGPA hilo que manda las tramas alive
threading.Thread(name = 'Trama ALIVE',target =tramaAlive,args = (()),daemon = True).start()

#JGPA Imprimimos el mensaje inicial
main_Client.banner1()


#JGPA  Inicia el proceso principal del menu
try:
    #JGPA verificamos que el menu este activado
    while mainchat:
        try:
            #JGPA Se escoge una opcion del menu
            main_Client.banner2()
            opcion = int(input('Escoja una opcion: '))
            #JGPA si la opcion fue uno...
            if opcion == 1 :
                main_Client.banner3()
                #JGPA Preguntamos el detinatario
                destino = int(input('Enviar a usuario o sala? '))
                x, y = main_Client.destinatario(destino)
                #JGPA Se ingresa el mensaje que queremos enviar
                mensaje_a_enviar = str(input('Escriba el mensaje:\n\n'))
                #EMVB Se llama la funcion para encriptar el texto
                mensaje_a_enviar = seguridad.encriptacion(mensaje_a_enviar)
                #JGPA Se envia el mensaje
                main_Client.publish_data(y, str(x), mensaje_a_enviar)
                logging.info("El mensaje ha sido enviado")

            #JGPA Si la opcion es 2
            elif opcion == 2:
                #JGPA Preguntamos la duracion del mensaje de voz
                duracion = int(input('Ingrese la duracion en segundos(max 30): '))
                #JGPA comprobamos que sea correcta
                if duracion <= 30:
                    main_Client.banner3()
                    #JGPA preguntamos el destino 
                    destino = int(input('Enviar a usuario o sala? '))
                    #JGPA otro objeto para enviar trama FTR
                    x, y = main_Client.destinatario(destino)
                    logging.info('Grabe su mensaje')
                    #JGPA Se inicia la grabacion
                    os.system('arecord -d '+ str(duracion)+ ' -f U8 -r 8000 audior.wav')
                    logging.info('Mensaje grabado')
                    #JGPA Se envia la trama FTR con sus parametros
                    negociacion_audio = HandlingInstructions(code='FTR', transmitter=main_Client.get_userClient(), addressee=str(x), file_size=str(os.stat('audior.wav').st_size))
                    main_Client.publish_data('comandos/09', str(x), negociacion_audio.get_finally_code())
                    time.sleep(1)          
                else:
                    #JGPA Error de ingreso
                    logging.warning('Valor incorrecto. Intente de nuevo')    
            elif opcion == 3:
                #JGPA Si la opcion fue 3 nos salimos del programa
                break
            else:
                #JGPA Error cuando se ingresa una opcion invalida
                logging.warning('Opcion incorrecta. Intente de nuevo')
        except ValueError:
            #JGPA excepcion cuando se ingresa un valor incorrecto
            if mainchat:
                #JGPA Error si hay server
                logging.warning('Error mal ingreso espere')
            else:
                #JGPA Error si no hay server
                logging.warning('Servidor fuera de linea')
        #JGPA tiempo de espera 
        time.sleep(DEFAULT_DELAY)
except KeyboardInterrupt:
    #JGPA excepcion cuando se interrumpe el programa
    pass

finally:
    #JGPA Desconectamos todo en caso de salir del programa o responda el server
    logging.warning("Saliendo del programa...")
    main_Client.disconnect()
