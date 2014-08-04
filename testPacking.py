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
        vec = [vec[0], vec[2], vec[1]]
    elif format == 'ZXY':
        vec = [vec[2], vec[0], vec[1]]
    elif format == 'XYZ':
        scalar = [1.0, 256.0, 65536.0]

    #vec = [(x + 1.0)/2.0 for x in vec]
    
    vec[0] = (vec[0] + 1.0) / 2.0 * 255
    vec[1] = (vec[1] + 1.0) / 2.0 * 255
    vec[2] = (vec[2] + 1.0) / 2.0 * 255
    
    #newVec = Vector()
    
    #newVec.x = vec[0] * scalar[0]
    #newVec.y = vec[1] * scalar[1]
    #newVec.z = vec[2] * scalar[2]
    
    packedInt = (int(vec[2]) << 16) | (int(vec[1]) << 8) | int(vec[0])
    packedFloat = ((float(packedInt)) / (float((1 << 24))) ) * 65536.0
    
    total = packedFloat
    #return sum([a*b for a,b in zip(vec, scalar)])
    
    return (total)

vec = [-0.2, -0.3, -0.4]

print(str(vec)+"\n")

packed = pack(vec, 'XYZ')

print(str(packed)+"\n")

unpack = readPackedVector(packed, 'XYZ')

print(str(unpack)+"\n")
