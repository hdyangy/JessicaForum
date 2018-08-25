import struct
class ByteArray:
    def __init__(self, data = ''):
        self.data = data

    def readBoolean(self):
        boolean = struct.unpack('!?', self.data[:1])[0]
        self.data = self.data[1:]
        return boolean

    def readByte(self):
        byte = struct.unpack('!b', self.data[:1])[0]
        self.data = self.data[1:]
        return byte

    def readBytes(self, length):
        bytes = self.data[:length]
        self.data = self.data[length:]
        return bytes

    def readInt(self):
        integer = struct.unpack('!i', self.data[:4])[0]
        self.data = self.data[4:]
        return integer
	
    def readLong(self):
        longdata = struct.unpack('!L', self.data[:4])[0]
        self.data = self.data[4:]
        return longdata

    def readShort(self):
        short = struct.unpack('!h', self.data[:2])[0]
        self.data = self.data[2:]
        return short

    def readUnsignedByte(self):
        byte = struct.unpack('!B', self.data[:1])[0]
        self.data = self.data[1:]
        return byte

    def readUnsignedInt(self):
        integer = struct.unpack('!I', self.data[:4])[0]
        self.data = self.data[4:]
        return integer

    def readUnsignedShort(self):
        short = struct.unpack('!H', self.data[:2])[0]
        self.data = self.data[2:]
        return short

    def readUTF(self):
        length = self.readShort()
        string = self.data[:length]
        self.data = self.data[length:]
        return string

    def readUnsignedUTF(self):
        length = self.readUnsignedShort()
        string = self.data[:length]
        self.data = self.data[length:]
        return string

    def readUTFBytes(self, length):
        utfBytes = self.data[:length]
        self.data = self.data[length:]
        return utfBytes
		
    def readLongString(self):
        size = struct.unpack('!l', self.data[:4])[0]
        string = self.data[4:4 + size]
        self.data = self.data[size + 4:]
        return string.replace("'","")
		
    def toByteArray(self):
        return self.data
		
    def toPack(self):
        return struct.pack('!l', len(self.data)+4)+self.data
		
    def length(self):
        return len(self.data)

    def writeBoolean(self, boolean):
        self.data += struct.pack('!?', boolean)

    def writeByte(self, byte):
        self.data += struct.pack('!b', byte)

    def writeBytes(self, bytes):
        self.data += bytes

    def writeInt(self, integer):
        self.data += struct.pack('!i', integer)
	
    def writeLong(self, longdata):
        self.data += struct.pack('!L', longdata)

    def writeShort(self, short):
        self.data += struct.pack('!h', short)

    def writeUnsignedByte(self, byte):
        self.data += struct.pack('!B', byte)

    def writeUnsignedInt(self, integer):
        self.data += struct.pack('!I', integer)

    def writeUnsignedShort(self, short):
        self.data += struct.pack('!H', short)

    def writeUTF(self, string):
        self.data += struct.pack('!h', len(string)) + string

    def writeUnsignedUTF(self, string):
        self.data += struct.pack('!H', len(string)) + string

    def writeUTFBytes(self, utfBytes):
        self.data += utfBytes
		
	def length(self):
		return len(self.data)
		
    def Available(self):
        return len(self.data) > 0