__author__ = 'mberger'
import logging
import struct

log = logging

def read_xint16(stream):
    val = struct.unpack('h',stream.read(2))[0]
    if val & int("0x8000",0):
        val = val & int("0x7fff")
        val = val | (struct.unpack('h',stream.read(2))[0] << 16)
    return val

def read_char(stream):
    magic = struct.unpack('!I',stream.read(4))[0]
    #print(hex(magic))
    if magic & int(0xffff0000)!= int(0xffff0000):
        raise UnicodeError("Not a valik skp text magic: {} at {}".format(hex(magic),hex(stream.tell())))

    n = struct.unpack('h',stream.read(2))[0]

    text = stream.read(n).decode('ascii')
    return text

def read_wchar(stream):
    magic = struct.unpack('!I',stream.read(4))[0]
    if (magic & int(0xFFFFFF00)) != int(0xfffeff00):
        stream.seek(-4,1)
        log.debug("Not a valid skp text magic: {} at {}".format(hex(magic), hex(stream.tell())))
        return False
    n= magic & int(0x000000FF)

    text = stream.read(2 * n).decode('utf-16-le')
    return text


def read_int32_be(stream):
    return struct.unpack('>I',stream.read(4))[0]

def read_int32_le(stream):
    return struct.unpack('<I',stream.read(4))[0]

def read_float_le(stream):
    return struct.unpack('<f',stream.read(4))[0]

def read_int16_le(stream):
    return struct.unpack('<H',stream.read(2))[0]

def read_int8(stream):
    return struct.unpack('B',stream.read(1))[0]


def write_png(stream=None, length=0, name='/tmp/t.png', ):
    if stream and length > 0:
        print("Writing ", hex(stream.tell()), " " ,length)
        with open(name, "wb") as outFile:
            outFile.write(stream.read(length))