#JGPA Importamos la libreria para binarios
import binascii

#JGPA Clase para el manejo de las tramas
class HandlingInstructions:
    # JGPA Constructor
    def __init__(self, trama=None, code=None, transmitter=None, addressee=None, file_size=None):
        #JGPA Variables de la clase
        self.Code = code
        self.UserID = transmitter
        self.receiver = addressee
        self.Size = file_size
        self.Trama = trama
    
    #JGPA Metodo que separa la trama
    def message_received(self):
        y = self.Trama.decode()
        y = y.split('$')
        return y

    #JGPA Metodo que devuelve el comando en la trama
    def get_Command(self):
        command = ''
        u =  self.message_received()
        #JGPA Se compara la primera parte de la trama para determinar que comando es
        if u[0] == '\x02':
            command = 'FRR'
        elif u[0] == '\x03':
            command = 'FTR'
        elif u[0] == '\x04':
            command = 'ALIVE'
        elif u[0] == '\x05':
            command = 'ACK'
        elif u[0] == '\x06':
            command = 'OK'
        elif u[0]== '\x07':
            command = 'NO'
        return command

    #JGPA Metodo que devuelve el destino de una trama 
    def get_dest(self):
        s = self.message_received()
        return s[1]

    #JGPA Metodo que devuelve el tamano del archivo de audio    
    def get_file(self):
        s = self.message_received()
        return s[2]
    
    #JGPA Metodo para codificar la trama segun el comando
    def get_code(self):
        #JGPA Se compara el valor de la varible para devolverla en bytes hexagesimal
        if self.Code == 'FRR':
            return binascii.unhexlify('02')
        elif self.Code == 'FTR':
            return binascii.unhexlify('03')
        elif self.Code == 'ALIVE':
            return binascii.unhexlify('04')
        elif self.Code == 'ACK':
            return binascii.unhexlify('05')
        elif self.Code == 'OK':
            return binascii.unhexlify('06')
        elif self.Code == 'NO':
            return binascii.unhexlify('07')
        else:
            #JGPA Error por si se pide un comando invalido
            return str('El comando no esta en la lista de comandos del sistema')

    #JGPA Metodo para formar tramas    
    def get_finally_code(self):
        m = ''
        separador = b'$'
        #JGPA Formar trama FRR
        if self.get_code() == binascii.unhexlify('02'):
            x = self.get_code()
            y = self.UserID.encode()
            z = self.Size.encode()
            m = x + separador + y + separador + z
        #JGPA Formar trama FTR
        elif self.get_code() == binascii.unhexlify('03'):
            x = self.get_code()
            y = self.receiver.encode()
            z = self.Size.encode()
            w = self.UserID.encode()
            m = x + separador + y + separador + z + separador + w
        #JGPA Formar trama ALIVE
        elif self.get_code() == binascii.unhexlify('04'):
            x = self.get_code()
            y = self.UserID.encode()
            m = x + separador + y
        #JGPA Formar trama ACK    
        elif self.get_code() == binascii.unhexlify('05'):
            x = self.get_code()
            y = self.UserID.encode()
            m = x + separador + y
        #JGPA Formar trama OK
        elif self.get_code() == binascii.unhexlify('06'):
            x = self.get_code()
            y = self.UserID.encode()
            m = x + separador + y
        #JGPA Formar trama NO
        elif self.get_code() == binascii.unhexlify('07'):
            x = self.get_code()
            y = self.UserID.encode()
            m = x + separador + y
        return m 
'''
chat = HandlingInstructions(trama=b'\x04$201700796')
print(chat.message_received())
print(chat.get_Command())
print (chat.get_dest())
'''
# p = HandlingInstructions(code='FRR', transmitter='201700796', addressee='201700388', file_size='15')
# print (p.get_finally_code())