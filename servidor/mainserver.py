''' JDCR Este es el main del server se utilizaon diferentes archivos 
    en donde se llamaron las clases para se usadas aqui''' 
from ClaseServer import ServerManagement
from Globales import*
import logging
import time
import threading

# JDCR se crea el objeto de tiop manejo de servidor con todos los atributos 
main_server =  ServerManagement(MQTT_HOST, MQTT_USER, MQTT_PASS, MQTT_PORT, TCP_PORT, user=FILE_USERS, rooms=FILE_ROOMS, group=GROUP_NUMBER)
# JDCR se configura el objeto como mqtt
main_server.server_mqtt()
# JDCR se conecta con el broker
main_server.connect()
# JDCR se suscribe a los topics que fueron obtenidos de los archivos de texto
main_server.subscription()
# JDCR se crea el hilo   ue verifica los usuarios conectados
threading.Thread(name = 'usuarios Conectados',target = main_server.lista_conectados(),args = (), daemon = True).start()


# JDCR inicia el programa principal
try:
    while True:
        time.sleep(DEFAULT_DELAY)

except KeyboardInterrupt:
    pass
finally:
    logging.warning("Saliendo del programa...")
    main_server.disconnect()
