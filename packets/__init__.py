# -*- coding: utf-8 -*-
from struct import *

class ByteArray:
    def __init__(self, bytes = ''):
        self.bytes = bytes

    def writeBytes(self, bytes):
        self.bytes += bytes
        return self

    def readBytes(self, length):
        value = self.bytes[:length]
        self.bytes = self.bytes[length:]
        return value

    def writeByte(self, value):
        self.bytes += pack('!b', int(value))
        return self

    def writeUnsignedByte(self, value):
        self.bytes += pack('!B', int(value))
        return self

    def readByte(self):
        value = unpack('!b', self.bytes[:1])[0]
        self.bytes = self.bytes[1:]
        return int(value)

    def readUnsignedByte(self):
        value = unpack('!B', self.bytes[:1])[0]
        self.bytes = self.bytes[1:]
        return int(value)

    def writeShort(self, value):
        self.bytes += pack('!h', int(value))
        return self

    def writeUnsignedShort(self, value):
        self.bytes += pack('!H', int(value))
        return self

    def readShort(self):
        value = unpack('!h', self.bytes[:2])[0]
        self.bytes = self.bytes[2:]
        return int(value)

    def readUnsignedShort(self):
        value = unpack('!H', self.bytes[:2])[0]
        self.bytes = self.bytes[2:]
        return int(value)

    def writeInt(self, value):
        self.bytes += pack('!I', int(value))
        return self

    def readInt(self):
        value = unpack('!i', self.bytes[:4])[0]
        self.bytes = self.bytes[4:]
        return int(value)

    def readUnsignedInt(self):
        value = unpack('!I', self.bytes[:4])[0]
        self.bytes = self.bytes[4:]
        return int(value)

    def writeUTFBytes(self, value):
        self.bytes += value
        return self

    def readUTFBytes(self, length):
        value = self.bytes[:length]
        self.bytes = self.bytes[length:]
        return value

    def writeUTF(self, value):
        self.writeShort(len(value))
        self.writeUTFBytes(value)
        return self

    def readUTF(self):
        value = self.readUTFBytes(self.readShort())
        return value

    def writeFloat(self, value):
        self.bytes += pack('!f', float(value))
        return self

    def readFloat(self):
        value = unpack('!f', self.bytes[:4])[0]
        self.bytes = self.bytes[4:]
        return float(value)

    def writeDouble(self, value):
        self.bytes += pack('!d', value)
        return self

    def readDouble(self):
        value = unpack('!d', self.bytes[:8])[0]
        self.bytes = self.bytes[8:]
        return value

    def writeBoolean(self, value):
        self.bytes += pack('!?', bool(value))
        return self

    def readBoolean(self):
        value = unpack('!?', self.bytes[:1])[0]
        self.bytes = self.bytes[1:]
        return bool(value)

    def toByteArray(self):
        return self.bytes

    def bytesAvailable(self):
        return self.bytes > 0

    def getLength(self):
        return len(self.bytes)

    def clear(self):
        self.bytes = ''
        return self
