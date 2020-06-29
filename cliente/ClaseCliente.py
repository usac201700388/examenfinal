import paho.mqtt.client as mqtt
import logging
import time
import os 
import threading
from datetime import datetime
import socket
from Clasetramas import HandlingInstructions
#ackactivado = False
mainchat = True 



def client_instance():
    client = mqtt.Client(clean_session=True)
    return client

class ClientManagement:
    def __init__(self, ip_address, user_mqtt, password, port_mqtt, port_tcp=None, user=None, rooms=None, group=None):
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
    
    def server_mqtt(self):

        client = self.instance
        logging.basicConfig(level=logging.INFO, format='\n[%(levelname)s] (%(threadName)-10s) %(message)s')
        logging.basicConfig(level=logging.ERROR, format='\n[%(levelname)s] (%(threadName)-10s) %(message)s')
        def on_connect_sub(client, userdata, rc):
            logging.info("Conectado al broker")

        def on_message(client, userdata, msg):
            # self.flags = False
            #global ackactivado
            # logging.info("Ha llegado el mensaje al topic: " + str(msg.topic))
            if 'comandos/09' in str(msg.topic):
                x = HandlingInstructions(trama=msg.payload)
                if x.get_Command() == 'OK':
                    logging.info("El contenido del mensaje es: " + str(msg.payload))
                    logging.info('El archivo empezara a enviarse...')
                    self.configurar_hilo()
                if x.get_Command() == 'ACK':
                    # logging.info("El contenido del mensaje es: " + str(msg.payload))
                    self.ackactivado = True
                if x.get_Command() == 'NO':
                    logging.warning('El destinatario no esta conectado...')
            else:
                logging.info("El contenido del mensaje es: " + str(msg.payload))

        def on_connect_pub(client, userdata, flags, rc):
            connection_text = "CONNACK recibido del broker con codigo: " + str(rc)
            logging.info(connection_text) 

        def on_publish(client, userdata, mid):
            # self.flags = True
            publish_text = "Publicacion satisfactoria"
            logging.debug(publish_text)

        client.on_connect_sub = on_connect_sub
        client.on_message = on_message 
        client.on_connect_pub = on_connect_pub 
        client.on_publish = on_publish 
        client.username_pw_set(self.user, self.password) 
    
    
    def connect(self):
        client = self.instance
        client.connect(host=self.ip, port=self.portM) 

    def disconnect(self):
        client = self.instance
        client.disconnect()
    def subscribers(self):
        topic = []
        with open(self.participants, 'r') as users:
            for i in users:
                split_users = i.split(',')
                tuple_users = ('usuarios' + '/' + split_users[0], self.Quality)
                tuple_comandos = ('comandos/' + self.Groups + '/' + split_users[0], self.Quality)
                topic.append(tuple_users)
                topic.append(tuple_comandos)
            users.close()
        with open(self.Room, 'r') as rooms:
            for i in rooms:
                split_rooms = i.split('\n')
                tuple_rooms = ('salas' + '/' + self.Groups + '/' + split_rooms[0][2:], self.Quality)
                tuple_commands = ('comandos' + '/' + self.Groups + '/' + split_rooms[0][2:], self.Quality)
                topic.append(tuple_rooms)
                topic.append(tuple_commands)
            rooms.close()
        return topic

    
    def subscription(self):
        client = self.instance
        list_topics = self.subscribers()
        client.subscribe(list_topics[:])
        client.loop_start()
    
    def publish_data(self, topic_root, topic_name, value):
        client = self.instance
        topics = topic_root + "/" + topic_name
        client.publish(topics, value, self.Quality, retain=False)
    
    def server_tcp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (self.ip, self.portT)
        sock.bind(serverAddress)
        sock.listen(10)
        logging.debug('Iniciando servidor en {}, puerto {}'.format(*serverAddress))
        connection, clientAddress = sock.accept()
        logging.debug('Conexion establecida')
        return sock, connection, clientAddress

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
    
    def configurar_hilo(self):
        time.sleep(3)
        threading.Thread(name = 'Servidor TCP',target = self.envio_tcp(),args = (()),daemon = False).start()

    def banner1(self):
        print('\n')
        print(' ========================================================')
        print(' |                                                      |')
        print(' |               Bienvenido al chat de Voz!             |')
        print(' |                       Parcial 2                      |')
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
    
    def destinatario(self, destino):
        if destino == 1:
            carne = int(input('\nIngrese usuario(carne): '))
            pri = 'usuarios'
            return carne, pri        
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
