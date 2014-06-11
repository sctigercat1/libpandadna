import struct


# Byte orders...
LITTLE_ENDIAN = '<'
BIG_ENDIAN = '>'

# Data types...

# Signed integers...
INT8 = 'b'
INT16 = 'h'
INT32 = 'i'
INT64 = 'q'

# Unsigned integers...
UINT8 = 'B'
UINT16 = 'H'
UINT32 = 'I'
UINT64 = 'Q'

# Strings...
SHORT_STRING = 's'
LONG_STRING = 'S'

# Booleans...
BOOLEAN = '?'

# Floats... (signed)
FLOAT32 = 'f'
FLOAT64 = 'd' # double

class DNAPacker:
    def __init__(self, name='DNAPacker', packer=None, verbose=False):
        self.name = name
        self.__data = ''
        self.verbose = verbose

        # If we've been given either a DNAPacker object, or a string as an
        # argument for packer, let's use this as the starting point for our
        # data:
        if isinstance(packer, DNAPacker) or isinstance(packer, str):
            self.__data = str(packer)

    def __str__(self):
        return self.__data

    def __repr__(self):
        return repr(self.__data)

    def __len__(self):
        return len(self.__data)

    def __add__(self, other):
        return DNAPacker(name=self.name, packer=(self.__data + str(other)),
                         verbose=self.verbose)

    def __radd__(self, other):
        return DNAPacker(name=self.name, packer=(str(other) + self.__data),
                         verbose=self.verbose)

    def __iadd__(self, other):
        self.__data += str(other)
        return self

    def debug(self, message):
        if self.verbose:
            print '{name}: {message}'.format(name=self.name, message=message)

    def pack(self, fieldName, value, dataType, byteOrder=LITTLE_ENDIAN):
        self.debug('packing... {fieldName}: {value}'.format(
                    fieldName=fieldName, value=repr(value)))

        # If we're packing a string, add the length header:
        if dataType == SHORT_STRING:
            self += struct.pack(byteOrder + UINT8, len(value))
        elif dataType == LONG_STRING:
            self += struct.pack(byteOrder + UINT16, len(value))

        if dataType in (SHORT_STRING, LONG_STRING):

            # Pack the data raw:
            self += value

        else:

            # Pack the value using struct.pack():
            self += struct.pack(byteOrder + dataType, value)

    def unpack(self, dataType, byteOrder=LITTLE_ENDIAN):
        # If we're unpacking a string, read the length header:
        if dataType == SHORT_STRING:
            length = struct.unpack_from(byteOrder + UINT8, self.__data)[0]
            self.__data = self.__data[1:]
        elif dataType == LONG_STRING:
            length = struct.unpack_from(byteOrder + UINT16, self.__data)[0]
            self.__data = self.__data[2:]

        if dataType in (SHORT_STRING, LONG_STRING):

            # Unpack the data raw:
            data = self.__data[:length]
            self.__data = self.__data[length:]
            return data

        else:

            # Unpack the value using struct.unpack():
            dataType = byteOrder + dataType
            data = struct.unpack_from(dataType, self.__data)[0]
            self.__data = self.__data[struct.calcsize(dataType):]
            return data

    def packColor(self, fieldName, r, g, b, a, byteOrder=LITTLE_ENDIAN):
        self.debug('packing... {fieldName}: ({r}, {g}, {b}, {a})'.format(
                    fieldName=fieldName, r=r, g=g, b=b, a=a))

        for component in (r, g, b, a):
            self += struct.pack(byteOrder + UINT8, int(component * 255))

    def unpackColor(self, byteOrder=LITTLE_ENDIAN):
        color = []
        for _ in xrange(4):
            component = struct.unpack_from(byteOrder + UINT8, self.__data)[0]
            component /= 255.0
            color.append(component)
        return tuple(color)

    def packPosition(self, x, y, z, byteOrder=LITTLE_ENDIAN):
        self.debug('packing... position: ({x}, {y}, {z})'.format(x=x, y=y, z=z))

        for component in (x, y, z):
            self += struct.pack(byteOrder + INT32, int(component * 100.0))

    def unpackPosition(self, byteOrder=LITTLE_ENDIAN):
        position = []
        for _ in xrange(3):
            component = struct.unpack_from(byteOrder + INT32, self.__data)[0]
            component /= 100.0
            position.append(component)
        return tuple(position)

    def packRotation(self, h, p, r, byteOrder=LITTLE_ENDIAN):
        self.debug('packing... rotation: ({h}, {p}, {r})'.format(h=h, p=p, r=r))

        for component in (h, p, r):
            self += struct.pack(byteOrder + INT32, int(component * 100.0))

    def unpackRotation(self, byteOrder=LITTLE_ENDIAN):
        rotation = []
        for _ in xrange(3):
            component = struct.unpack_from(byteOrder + INT32, self.__data)[0]
            component /= 100.0
            rotation.append(component)
        return tuple(rotation)

    def packScale(self, x, y, z, byteOrder=LITTLE_ENDIAN):
        self.debug('packing... scale: ({x}, {y}, {z})'.format(x=x, y=y, z=z))

        for component in (x, y, z):
            self += struct.pack(byteOrder + UINT16, int(component * 100.0))

    def unpackScale(self, byteOrder=LITTLE_ENDIAN):
        scale = []
        for _ in xrange(3):
            component = struct.unpack_from(byteOrder + UINT16, self.__data)[0]
            component /= 100.0
            scale.append(component)
        return tuple(scale)
