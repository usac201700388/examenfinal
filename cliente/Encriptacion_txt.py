#EMVB librerias necesarias para la ejecucion del programa
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Random import get_random_bytes
import base64
import hashlib

#EMVB en caso de que salga un error al ejecutar el programa, revise hasta abajo

#EMVB Se abre la clase encriptacion
class Encriptacion(object):

    #EMVB se deja que el valor a ingresar es la palabra de encriptacion
    def __init__(self, clave):
        #EMVB esta funcion permite que la palabra clave posea una cantidad distinta a 16 bytes sin dar error.
        self.clave = hashlib.sha256(clave.encode("utf-8")).digest() 
        #EMVB esta constante se utiliza como el tamaño del bloque para encriptar y desencriptar el texto.
        self.bs = 16

    #EMVB se abre la funcion de encriptacion
    def encriptacion(self, mensaje):
        #EMVB ajusta el largo del mensaje
        mensaje = self.pad(mensaje)
        #EMVB genera un vector aleatorio de 16 bytes
        vector = Random.new().read(AES.block_size)
        #vector = Random.get_random_bytes(AES.block_size)
        #EMVB genera el cifrador de mensajes
        cifrado = AES.new(self.clave, AES.MODE_CBC, vector)
        #EMVB regresa un vector de bytes del mensaje encriptado con base 64
        return base64.b64encode(vector + cifrado.encrypt(mensaje))

    #EMVB se abre la funcion de desencriptacion 
    def desencriptacion(self, encrip):
        #EMVB recibe el mensaje encriptado en base 64
        encrip = base64.b64decode(encrip)
        #EMVB revice el vector de codificacion del mensaje encriptado
        vector = encrip[:AES.block_size]
        #EMVB  genera el decifrador del mensaje
        cifrado = AES.new(self.clave, AES.MODE_CBC, vector)
        #EMVB regresa el mensaje decifrado 
        return self.unpad(cifrado.decrypt(encrip[AES.block_size:])).decode('utf-8')

    #EMVB funcion que ajusta el largo del mensaje para encriptacion cuando el largo del mensaje no es multiplo de block_size
    def pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    #EMVB funcion que ajusta el largo del mensaje para desencriptacion cuando el largo del mensaje no es multiplo de block_size
    def unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


'''
#EMVB

En caso de que surja el error: 

"AttributeError: module 'time' has no attribute 'clock'"

Es necesario cambiar a un python inferior, o cambiar en la libreria:

 File "/usr/local/lib/python3.8/dist-packages/Crypto/Random/_UserFriendlyRNG.py", line 77, in collect
   
hacer la modificacion de:  

    t = time.clock()   ->    t = time.perf_counter()

Esto es devido que en Python 3.8 se descontinuo este modulo, el cual es la razon por la cual hay que hacer este cambio en la libreria.

De no ser posible el arreglo al programa, se tienen que hacer unos simples cambios de a los programas.

1) En ClaseCliente.py se debe desabilitar la linea 81 y hacer el cambio de variable para que ingrese directo el mensaje.

2) En mainClient.py se debe desabilitar la linea 96. 

#EMVB

Para comprobar de que si funciona el programa, se puede ejecutar el codigo de abajo.


seguridad = Encriptacion('Esta es la clave')
men ='el examen final si sale'
encriptado = seguridad.encriptacion(men)
desencriptado = seguridad.desencriptacion(encriptado)

print (encriptado)
print (desencriptado)
'''

