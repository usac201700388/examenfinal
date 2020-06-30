# JDCR Importamos las librerias que se utilizaran en esta clase.
import paho.mqtt.client as mqtt
import socket
import logging
import os
from Clasetramas import HandlingInstructions
import threading
import time

# JDCR funcion para crear una instancia de cliente mqtt
def client_instance():
    client = mqtt.Client(clean_session=True)
    return client

# JDCR Creacion de la Clase que manejara el Cliente
class ServerManagement:
    ''' JDCR Creacion del constructor en donde se le dice cuales sera los atributos del objeto servidor.
      Entre los cuales estan la direcion IP, el Usuario de MQTT con su password
     y los datos de nuestro grupo.''' 

    def __init__(self, ip_address=None, user_mqtt=None, password=None, port_mqtt=None, port_tcp=None,
                 user=None, rooms=None, group=None):
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
        self.users_online = list()
        self.temporal = list()
    # JDCR Funcion para configurar el objeto como un suscriptor/ publicador en el MQTT
    def server_mqtt(self):
        client = self.instance
        # JDCR Configuracion Inicial de logging en los niveles Info y Error
        logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(processName)-10s) %(message)s')
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(processName)-10s) %(message)s')
        # JDCR Callback que se ejecuta cuando nos conectamos al broker.
        def on_connect_sub(client, userdata, rc):
            logging.info("Conectado al broker")
        # JDCR  Callback que se ejecuta cuando llega un mensaje al topic suscrito
        def on_message(client, userdata, msg):
            if 'comandos/09' in str(msg.topic):
                x =  HandlingInstructions(trama=msg.payload)
                if x.get_Command() == 'FTR':
                    for i in self.users_online[-1]:
                        if x.get_dest() == i:
                            logging.info("solicitud de envio de archivos " + str(msg.payload))
                            q = HandlingInstructions(code='OK', transmitter=str(x.get_remitente()))
                            self.publish_data('comandos/09', str(x.get_remitente()), q.get_finally_code())
                            time.sleep(0.5)
                            break
                        else:
                            q = HandlingInstructions(code='NO', transmitter=str(x.get_remitente()))
                            self.publish_data('comandos/09', str(x.get_remitente()), q.get_finally_code())
                elif x.get_Command() == 'ALIVE':
                    k = HandlingInstructions(code='ACK', transmitter=x.get_dest())
                    self.publish_data('comandos/09', str(x.get_dest()), k.get_finally_code())
                    self.usersconectados(str(x.get_dest()))
            else:
                logging.info("El contenido del mensaje es: " + str(msg.payload))
        # JDCR Handler en caso suceda la conexion con el broker MQTT
        def on_connect_pub(client, userdata, flags, rc):
            connection_text = "CONNACK recibido del broker con codigo: " + str(rc)
            logging.info(connection_text)
        # JDCR Handler en caso se publique satisfactoriamente en el broker MQTT 
        def on_publish(client, userdata, mid):
            publish_text = "Publicacion satisfactoria"
            logging.debug(publish_text)
        
        client.on_connect_sub = on_connect_sub # JDCR Se configura la funcion "Handler" cuando suceda la conexion
        client.on_connect_pub = on_connect_pub
        client.on_message = on_message# JDCR Se configura la funcion "Handler" que se activa al llegar un mensaje a un topic subscrito
        client.on_publish = on_publish #JDCR Se configura la funcion "Handler" que se activa al publicar algo
        client.username_pw_set(self.user, self.password) # JDCR Credenciales requeridas por el broker
    
    def connect(self):
        # JDCR se llama al atributo que  hace la instancia del cliente 
        client = self.instance
        # JDCR Conectar al servidor remoto
        client.connect(host=self.ip, port=self.portM)
    
    def disconnect(self):
        # JDCR se llama al atributo que  hace la instancia del cliente 
        client = self.instance
        # JDCR  Se desconecta del broker
        client.disconnect()
    
    def publish_data(self, topic_root, topic_name, value):
        # JDCR Instancia del cliente
        client = self.instance
        # JDCR Concatenacion de los parametro requierido, que seran el topic al que se publique el mensaje.
        topics = topic_root + "/" + topic_name
        # JDCR Funcio de la libreria paho para publicar por medio de MQTT en el topic  deseado por el usuario.
        client.publish(topics, value, self.Quality, retain=False)
    # JDCR funcion que devuelve una lista de tuplas que contiene todos los topics a los que esta suscrito este servidor.
    def subscribers(self):
        topic = []
        with open('usuarios.txt', 'r') as users_online:
            for i in users_online:
                split_users = i.split(',')
                tuple_users = ('usuarios' + '/' + split_users[0], self.Quality)
                topic.append(tuple_users)
            users_online.close()
        with open('salas.txt', 'r') as rooms:
            for i in rooms:
                split_rooms = i.split('\n')
                tuple_rooms = ('salas' + '/' + self.Groups + '/' + split_rooms[0][2:], self.Quality)
                topic.append(tuple_rooms)
            rooms.close()
        topic.append(('comandos/' + self.Groups + '/#', self.Quality))
        return topic # JDCR regresa el valor de la lista de tuplas con todos los topics.
    
    def subscription(self):
        # JDCR Instancia del cliente
        client = self.instance
        # JDCR lista de topics a los cuales esta suscrito el usuario
        # JDCR Estos deben ser en formato de tupla
        list_topics = self.subscribers()
        # JDCR se le asigna la tupla a la funcion de suscrbibirse en la libreria paho
        client.subscribe(list_topics[:])
        # JDCR Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
        client.loop_start()
        # JDCR Funcion para publicar un mensaje de texto o de audio en el Broker 

    # JDCR creacion de una lista temporal de usuarios conectados
    def usersconectados(self, usuario):
        cnt=0
        if len(self.temporal)==0:
            self.temporal.append(usuario)
        else:
            for i in self.temporal:
                if usuario != i:
                    cnt+=1
            if cnt == len(self.temporal):
                self.temporal.append(usuario)
        return self.temporal
    # JDCR Creacion de una lista que se actualiza cada 3 periodos 
    def lista_conectados(self):
        while True:
            if len(self.users_online)==3:
                self.users_online.remove(self.users_online[0])
            self.users_online.append(self.temporal)
            self.temporal = []
            time.sleep(2)
    # JDCR Creacion de la conexion TCP 
    def server_tcp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (self.ip, self.portT)
        sock.bind(serverAddress)
        sock.listen(10)
        logging.debug('Iniciando servidor en {}, puerto {}'.format(*serverAddress))
        connection, clientAddress = sock.accept()
        logging.debug('Conexion establecida')
        return sock, connection, clientAddress
    # JDCR funcion que se encarga de enviar los archivos recibidos por el servidor
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
    # JDCR funcion que se encarga de recibir los archivos que se evian desde el cliente.
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

    

    


