import binascii

class HandlingInstructions:
    def __init__(self, trama=None, code=None, transmitter=None, addressee=None, file_size=None):
        self.Code = code
        self.UserID = transmitter
        self.receiver = addressee
        self.Size = file_size
        self.Trama = trama
    

    def message_received(self):
        y = self.Trama.decode()
        y = y.split('$')
        return y

    def get_Command(self):
        command = ''
        u =  self.message_received()
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

    def get_dest(self):
        s = self.message_received()
        return s[1]
    def get_file(self):
        s = self.message_received()
        return s[2]
    
    def get_code(self):
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
            return str('El comando no esta en la lista de comandos del sistema')
        
    def get_finally_code(self):
        m = ''
        separador = b'$'
        if self.get_code() == binascii.unhexlify('02'):
            x = self.get_code()
            y = self.UserID.encode()
            z = self.Size.encode()
            m = x + separador + y + separador + z
        
        elif self.get_code() == binascii.unhexlify('03'):
            x = self.get_code()
            y = self.receiver.encode()
            z = self.Size.encode()
            w = self.UserID.encode()
            m = x + separador + y + separador + z + separador + w
        elif self.get_code() == binascii.unhexlify('04'):
            x = self.get_code()
            y = self.UserID.encode()
            m = x + separador + y
        elif self.get_code() == binascii.unhexlify('05'):
            x = self.get_code()
            y = self.UserID.encode()
            m = x + separador + y
        elif self.get_code() == binascii.unhexlify('06'):
            x = self.get_code()
            y = self.UserID.encode()
            m = x + separador + y
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

