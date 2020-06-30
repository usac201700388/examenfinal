#JGPA importamos las librerias necesarias y las clases propias
import paho.mqtt.client as mqtt
import logging
import time
import os 
import threading
from datetime import datetime
import socket
from Clasetramas import HandlingInstructions
from Encriptacion_txt import Encriptacion

#EMVB Se define la palabra clave de encriptacion
seguridad = Encriptacion('grupo9')

#ackactivado = Falsehttps://github.com/usac201700388/examenfinal.git
mainchat = True 

#JGPA Se inicia una nueva instancia de cliente mqtt
def client_instance():
    client = mqtt.Client(clean_session=True)
    return client

#JGPA Definimos toda la clase de manejo de cliente
class ClientManagement:
    #JGPA Constructor
    def __init__(self, ip_address, user_mqtt, password, port_mqtt, port_tcp=None, user=None, rooms=None, group=None):
        #JGPA definimos todas las variables que vamos a usar en la clase
        self.ip = ip_address
        self.user = user_mqtt
        self.password = password
        self.portM = port_mqtt
        self.portT = port_tcp
        self.participants = user
        self.Room = rooms
        self.Groups = group
        self.instance = client_instance()
        self.Quality = 2
        self.Buffer_size = 64 * 1024
        # self.flags = False
        self.ackactivado = False
    
    #JGPA metodo para iniciar el server mqtt
    def server_mqtt(self):

        client = self.instance
        #JGPA Configuracion del logging
        logging.basicConfig(level=logging.INFO, format='\n[%(levelname)s] (%(threadName)-10s) %(message)s')
        logging.basicConfig(level=logging.ERROR, format='\n[%(levelname)s] (%(threadName)-10s) %(message)s')

        #JGPA Funcion para cada vez que se reciba un mensaje 
        def on_message(client, userdata, msg):
            # self.flags = False
            #global ackactivado
            # logging.info("Ha llegado el mensaje al topic: " + str(msg.topic))
            #JGPA Si el mensaje llega al topic de comandos
            if 'comandos/09' in str(msg.topic):
                #JGPA Se crea un objeto con la trama recibida
                x = HandlingInstructions(trama=msg.payload)
                #JGPA Se determina cual es el comando de la trama
                if x.get_Command() == 'OK':
                    # logging.info("El contenido del mensaje es: " + str(msg.payload))
                    #JGPA Si la trama es OK se crea un hilo para enviar por tcp
                    logging.info('El archivo empezara a enviarse...')
                    configurar_hilo(self.envio_tcp())
                    logging.info('Arhivo enviado')
                elif x.get_Command() == 'ACK':
                    #JGPA Indicamos que se recibio un ACK
                    # logging.info("El contenido del mensaje es: " + str(msg.payload))
                    self.ackactivado = True
                elif x.get_Command() == 'NO':
                    #JGPA El server ha enviado una trama NO
                    logging.warning('El destinatario no esta conectado...')
                elif x.get_Command() == 'FRR':
                    #JGPA El server indica que se enviara un archivo
                    logging.debug('Hay una solicitud de transferencia de archivos')
                    logging.debug('Preparando para recibir...')
                    # self.configurar_hilo(self.recibido_tcp())
                    # self.configurar_hilo(self.play_audio('audior.wav'))
            else:
                #EMVB Se llama la funcion para desencriptar el texto recibido
                desencriptado = seguridad.desencriptacion(msg.payload)
                #JGPA Si el mensaje no llega a comandos entonces se muestra en pantalla
                logging.info("El contenido del mensaje es: " + str(desencriptado))

        #JGPA Funcion cuando se conecta al broker
        def on_connect_pub(client, userdata, flags, rc):
            connection_text = "CONNACK recibido del broker con codigo: " + str(rc)
            logging.info(connection_text) 

        #JGPA Funcion cuando se publica
        def on_publish(client, userdata, mid):
            publish_text = "Publicacion satisfactoria"
            logging.debug(publish_text)

        #JGPA Se configuran las funciones mqtt y las credenciales
        client.on_message = on_message 
        client.on_connect_pub = on_connect_pub 
        client.on_publish = on_publish 
        client.username_pw_set(self.user, self.password) 
    
    #JGPA Metodo para conectar el cliente
    def connect(self):
        client = self.instance
        client.connect(host=self.ip, port=self.portM) 

    #JGPA Metodo para desconectar el cliente
    def disconnect(self):
        client = self.instance
        client.disconnect()

    #JGPA Metodo para suscribirse a los topics    
    def subscribers(self):
        topic = []
        #JGPA Abrimos el archivo donde esta nuestro archivo
        with open(self.participants, 'r') as users:
            for i in users:
                #JGPA Separamos por comas
                split_users = i.split(',')
                #JGPA Creamos una tupla con el usuario y los comandos del usuario
                tuple_users = ('usuarios' + '/' + split_users[0], self.Quality)
                tuple_comandos = ('comandos/' + self.Groups + '/' + split_users[0], self.Quality)
                #JGPA Agregamos las tuplas a la lista de topics
                topic.append(tuple_users)
                topic.append(tuple_comandos)
            users.close()
        #JGPA Abrimos el archivo donde estan las salas    
        with open(self.Room, 'r') as rooms:
            for i in rooms:
                #JGPA Separamos por cada enter las salas
                split_rooms = i.split('\n')
                #JGPA Agregamos las salas y los comandos de sala a la tupla 
                tuple_rooms = ('salas' + '/' + self.Groups + '/' + split_rooms[0][2:], self.Quality)
                tuple_commands = ('comandos' + '/' + self.Groups + '/' + split_rooms[0][2:], self.Quality)
                #JGPA Agregamos las tuplas a la lista de topics
                topic.append(tuple_rooms)
                topic.append(tuple_commands)
            rooms.close()
        #JGPA Devolvemos la lista de topics    
        return topic

    #JGPA Metodo que devuelve el usuario en el archivo de texto     
    def get_userClient(self):
        #JGPA Se abre el archivo
        with open(self.participants, 'r') as user:
            for i in user:
                #JGPA Se separa por comas y se obtiene el carne
                split_v = i.split(',')
                x  = split_v[0]
        user.close()
        return x

    #JGPA Metodo para suscribirse 
    def subscription(self):
        client = self.instance
        #JGPA Obtenemos la lista de topic y nos suscribimos
        list_topics = self.subscribers()
        client.subscribe(list_topics[:])
        client.loop_start()
    
    #JGPA Metodo para publicar mensajes
    def publish_data(self, topic_root, topic_name, value):
        client = self.instance
        #JGPA Unimos el topic
        topics = topic_root + "/" + topic_name
        #JGPA Publicamos 
        client.publish(topics, value, self.Quality, retain=False)
    
    #JGPA Metodo para usar el  server
    def server_tcp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (self.ip, self.portT)
        sock.bind(serverAddress)
        sock.listen(10)
        logging.debug('Iniciando servidor en {}, puerto {}'.format(*serverAddress))
        connection, clientAddress = sock.accept()
        logging.debug('Conexion establecida')
        return sock, connection, clientAddress

    #JGPA Metodo para enviar tcp
    def envio_tcp(self):
        sock, connection, clientAddress = self.server_tcp()
        print(os.stat('audior.wav').st_size)
        size = str(os.stat('audior.wav').st_size).encode()
        connection.sendall(size)
        with open('audior.wav', 'rb') as f:
            connection.sendfile(f, 0)
            f.close()
        print("\n\nArchivo enviado a: ", clientAddress)
        sock.close()
        connection.close()

    #JGPA Metodo para recibir tcp
    def recibido_tcp(self):
        sock, connection, clientAddress = self.server_tcp()
        info = connection.recv(self.Buffer_size).decode()
        print(info)
        with open ('audior.wav', 'wb') as g:
            logging.debug('Arhivo creado y listo para recibir')
            while info:
                sound = connection.recv(self.Buffer_size)
                if not sound:
                    break
                else:
                    g.write(sound)
        print("\n\nArchivo enviado a: ", clientAddress)
        g.close()
        sock.close()
        connection.close()
    
    #JGPA Se definen los banners que se imprimen en el menu
    def banner1(self):
        print('\n')
        print(' ========================================================')
        print(' |                                                      |')
        print(' |               Bienvenido al chat de Voz!             |')
        print(' |                      Examen Final                    |')
        print(' |                       Grupo #09                      |')
        print(' |                                                      |')
        print(' ========================================================')
        print('\n')
    
    def banner2(self):
        print('\n==> 1. Enviar mensaje de texto')
        print('==> 2. Enviar mensaje de voz')
        print('==> 3. Salir')

    def banner3(self):
        print('\n==> 1. Usuario(privado)')
        print('==> 2. Sala')
    
    #JGPA funciones que se ejecutan en el menu principal
    def destinatario(self, destino):
        #JGPA Si se escogio enviar a un usuario se pregunta el carne
        if destino == 1:
            carne = int(input('\nIngrese usuario(carne): '))
            pri = 'usuarios'
            return carne, pri        
        #JGPA Si se escogio salas se pide el numero de sala
        elif destino == 2:
            opc_sala = int(input('Ingrese el numero de sala[max 99](sin ceros a la izquierda): '))
            if len(str(opc_sala)) == 2:
                sala = '09/S'+str(opc_sala)
            elif len(str(opc_sala)) == 1:
                sala = '09/S0'+str(opc_sala)
            else:
                logging.warning('Numero incorrecto. Intente de nuevo')
            pri = 'salas'
            return sala, pri

    #JGPA Metodo que reproduce el audio en un hilo
    def play_audio(self, fileName):
        logging.info('Audio guardado') # JDCR Mensaje en consola.
        cont = 'aplay '+ str(fileName) # JDCR Concatenacion de todos las partes que requiere el comando.
        os.system(cont) # JDCR Ejecicion del comando de reproduccion

#JGPA Hilo para usar tcp
def configurar_hilo(proceso):
    time.sleep(3)
    threading.Thread(name = 'Servidor TCP',target =proceso,args = (()),daemon = True).start()
