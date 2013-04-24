#!/usr/bin/python3
__author__ = 'mberger'


import struct
import logging
from datetime import datetime
from .util import *

log = logging
logging.basicConfig(format='%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s', level=logging.DEBUG, file=open('/tmp/sim.log','wb'))


def skp_find_section(stream):
    '''Find all the sections in the sketchup file and their length'''
    pName, pVer, pOffset = None, None, None
    while True:
        try:
            while struct.unpack('B',stream.read(1))[0] != int(0xff):
                pass

            offset = stream.tell()
            if struct.unpack('B',stream.read(1))[0] != int(0xff):
                stream.seek(offset)

            ver = read_int16_le(stream)

            nlen = read_int16_le(stream)
            if nlen == 0:
                stream.seek(offset)
                continue

            name = stream.read(nlen).decode('ascii')
            if len(name) > 0 and name[0] != 'C':
                stream.seek(offset)
                continue

            yield pName, pVer, pOffset, offset
            pName, pVer, pOffset = name, ver, offset
        except UnicodeDecodeError as e:
            stream.seek(offset + 2)
        except struct.error as e:
            yield pName, pVer, pOffset, stream.tell()
            return


def read_CDib(stream):
    unknown = struct.unpack('i',stream.read(4))[0]
    length = read_int32_le(stream)
    print("Length: {} {}".format(length, hex(length)))
    print(hex(stream.tell()))

    write_png(stream=stream, name='/tmp/test-{number}.png'.format(number=0), length=length)


def read_CAttributeNamed(stream):

    #w1 = read_int16_le(stream)
    #w2 = read_int16_le(stream)
    #w3 = read_int16_le(stream)
    stream.read(6)

    name = read_wchar(stream)
    log.debug(name)
    while name:
        try:
            tmp = read_wchar(stream)
            name = tmp
        except Exception as e:
            log.debug("NAME: {}".format(name))
        u1 = read_int8(stream)

        log.debug("type: ".format(hex(u1)))

        if u1 == int(0x0A):
            val = read_wchar(stream)
            log.debug("{} -> {}".format(name, val))
        elif u1 == int(0x07):
            val = read_int8(stream)
            log.debug("{} -> {}".format(name, val))
        elif u1 == int(0x00):
            log.debug("OFFEST {}".format(hex(stream.tell())))
            stream.seek(11,1)

            length = read_int32_le(stream)
            print("Length: {} {}".format(length, hex(length)))
            print(hex(stream.tell()))

            write_png(stream=stream, name='/tmp/test-{number}.png'.format(number='a'), length=length)

            return

        else:
            log.error("UNKNOWN type: {}".format(hex(u1)))


def read_CCamera(stream):
    return
    '''
    for i in range(int(0x12)):
        log.debug("float: {}".format( read_float_le(stream) / 254 ))

    #stream.seek(int(0xFF),1)
    #pass
    '''


def read_material(stream):
    read_int16_le(stream)
    log.debug("OFFEST {}".format(hex(stream.tell())))
    unknown = read_int16_le(stream) # seems to be 0
    name = read_wchar(stream)
    type = read_int8(stream)


    if type == int(0x0000):
        # Material is a color:
        read_int8(stream) # unknown
        r = read_int8(stream)
        g = read_int8(stream)
        b = read_int8(stream)
        a = read_int8(stream)

        log.debug("Material {} color : ({} {} {} {})".format(name, r,g,b,a))
        log.debug("OFFEST {}".format(hex(stream.tell())))
        tmp = read_wchar(stream)
        stream.seek(8,1)
    elif type == int(0x0001):
        log.debug("type: {}".format(type))
        u0 = read_int8(stream)
        u1 = read_int8(stream)
        u2 = read_int8(stream)
        u3 = read_int8(stream)

        log.debug("u1: {} u2: {} u3: {}".format(hex(u1),hex(u2),hex(u3)))

        if u3 == int(0x80):
            x1 = read_int32_le(stream)
            if x1 > 0:
                size = read_int32_le(stream)
                log.debug("Skipping texture data {} ({})".format(size, hex(size)))
                log.debug("OFFEST {}".format(hex(stream.tell())))
                stream.seek(size,1)
        else:
            log.debug('else')
            x1 = 4

        if x1 == 0:
            stream.seek(12,1)
        elif x1 == 1:
            stream.seek(20,1)
        elif x1 == 2 or x1 == 4:
            stream.seek(16,1)
        else:
            stream.seek(16+8,1)

        log.debug("Filename {}".format(read_wchar(stream)))
        stream.seek(8,1)
        stream.seek(13,1)

    else:
        log.error("type: {} Cant make sense of this".format(type))
        import sys
        sys.exit(0)


def read_CMaterial(stream):



    while True:
        read_material(stream)




        x1 = read_int32_be(stream)

        x2 = read_int32_be(stream)
        log.debug("x1 {} , x2 {}".format(x1, x2 ))
        #if x2 != 57407:
        #    break
        x3 = read_int32_be(stream)



        stream.seek(-2,1)
        b = read_int8(stream)
        log.debug("x1 {} , x2 {} , x3 {} , b {}".format(x1, x2, x3,b ))
        if b != 128:
            log.debug("done reading materials OFFEST {}".format(hex(stream.tell())))
            break
        #stream.seek(int(0x09),1)




def read_CLayer(stream):
    layers = []
    w1 = 0
    while w1 != 36:
        log.debug("OFFEST {}".format(hex(stream.tell())))
        w1 = read_int16_le(stream)
        log.debug("w1: {}".format(w1))
        #if w1==0:
        #    #raise Exception("w1 cannot be 0")
        #    pass

        s1 = read_wchar(stream)
        log.debug("LAYER: {}".format(s1))
        u1 = read_int8(stream)
        read_material(stream)
        stream.seek(13,1)
        w2 = read_int16_le(stream)
        log.debug("w2: {}".format(w2))
        w1 = w2

    print(layers)


def read_CComponentDefinition(stream):
    w1 = read_int16_le(stream)



import sys

with open(sys.argv[1],'rb') as f:
    # Sketchup
    print(read_wchar(f))

    #READ vERSION

    print(read_wchar(f))
    f.seek(16,1) #These can be 00'ed without breaking the model ???
    read_wchar(f)

    creation_date = datetime.fromtimestamp(read_int32_le(f))
    log.debug(creation_date)

    read_char(f)

    version_map = {}
    s = read_wchar(f)
    while s != "End-Of-Version-Map":
        v = struct.unpack('<I',f.read(4))[0]
        version_map[s] = v


        s = read_wchar(f)
    print(version_map)

    sections = []

    for n , v, offset, end_offset in skp_find_section(f):
        print("SECTION:", end=" ")
        print(n, v, offset, end_offset)
        sections.append((n , v, offset, end_offset))
        """

        if n == 'CDib':
            print('handle DIB')
            read_CDib(f)

        elif n == 'CAttributeNamed':
            print('handle CAttributeName')
            read_CAttributeNamed(f)
        elif n == 'CCamera':
            print('handle CCamera')
            read_CCamera(f)
        elif n == 'CMaterial':
            print('handle CMaterial')
            read_CMaterial(f)
        elif n == 'CArcCurve':
            pass #f.seek(2000,1)
        elif n == 'CSkFont':
            pass
        elif n == 'CLayer':
            pass
        elif n == 'CAttributeContainer':
            pass
            #read_CLayer(f)
        elif n == 'CComponentDefinition':
            read_CComponentDefinition(f)
        else:
            log.debug("Not handled {}".format(n))
            f.seek(int(0xf),1)
        """

    sys.exit(0)

