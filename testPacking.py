import math
import struct
import os
from mathutils import Vector

def readPackedVector(f, format):
    packed = f

    output = Vector()
    if format == 'XZY':
        output.x = packed
        output.y = packed / 65536.0
        output.z = packed / 256.0
    elif format == 'ZXY':
        output.x = packed / 256.0
        output.y = packed / 65536.0
        output.z = packed
    elif format == 'XYZ':
        output.x = packed
        output.y = packed / 256.0
        output.z = packed / 65536.0

    output.x -= math.floor(output.x)
    output.y -= math.floor(output.y)
    output.z -= math.floor(output.z)

    output.x = output.x*2 - 1
    output.y = output.y*2 - 1
    output.z = output.z*2 - 1

    return output

def pack(vec, format):
    scalar = []
    if format == 'XZY':
        scalar = [1.0, 65536.0, 256.0]
    elif format == 'ZXY':
        scalar = [256.0, 65536.0, 1.0]
    elif format == 'XYZ':
        scalar = [1.0, 256.0, 65536.0]

    vec = [(x + 1.0)/2.0 for x in vec]
    return sum([a*b for a,b in zip(vec, scalar)])

vec = [-0.6712, 0.2233, 0.7068]

print(str(vec)+"\n")

packed = pack(vec, 'XYZ')

print(str(packed)+"\n")

unpack = readPackedVector(packed, 'XYZ')

print(str(unpack)+"\n")
