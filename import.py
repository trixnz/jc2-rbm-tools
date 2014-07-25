import bpy
import math
import struct
import os
from bpy_extras.io_utils import unpack_list, unpack_face_list

# Shitty hack
currentLoadPath = ''

def readRBM(context, filepath):
    global currentLoadPath
    currentLoadPath = os.path.dirname(filepath)

    print('Loading RBM from %s' % (filepath))   
    
    f = open(filepath, 'rb')
    
    blocks = []
    
    # Read in the RBM magic number
    headerLength = struct.unpack('<i', f.read(4))[0]
    headerStr = '<%ds' % headerLength
    header = struct.unpack(headerStr, f.read(5))[0].decode()
    
    # Read in the version
    versionMajor = struct.unpack('<i', f.read(4))[0]
    versionMinor = struct.unpack('<i', f.read(4))[0]
    versionRevision = struct.unpack('<i', f.read(4))[0]

    print('Version %i.%i.r%i' % (versionMajor, versionMinor, versionRevision))
    
    # Read in the bounding box of the model
    minX = struct.unpack('<f', f.read(4))[0]
    minY = struct.unpack('<f', f.read(4))[0]
    minZ = struct.unpack('<f', f.read(4))[0]
    maxX = struct.unpack('<f', f.read(4))[0]
    maxY = struct.unpack('<f', f.read(4))[0]
    maxZ = struct.unpack('<f', f.read(4))[0]
    
    print("Max X: %f Max Y: %f Max Z: %f\nMin X: %f Min Y: %f Min Z: %f" % (maxX, maxY, maxZ, minX, minY, minZ))
    
    blockCount = struct.unpack('<i', f.read(4))[0]
    
    #Process every render block
    for block in range(blockCount):
        blockType = struct.unpack('<I', f.read(4))[0]
        
        print("BlockType: %d" % blockType)
        if(blockType == CarPaintSimpleBlock.NameHash):
            CarPaintSimpleBlock.read(f, blocks)
        elif(blockType == CarPaintBlock.NameHash):
            CarPaintBlock.read(f, blocks)
        elif(blockType == 112326146):
            processDeformableWindow(f, blocks)
        elif(blockType == 1583709984):
            processSkinnedGeneral(f, blocks)
        elif(blockType == 3587672800):
            processLambert(f, blocks)
        else:
            print('RIP')
        # Read the block footer
        f.read(4)        
    
    f.close()
    
    for block in blocks:
        base = bpy.context.scene.objects.link(block)
        base.select = True

    return {'FINISHED'}

def readLengthString(f):
    length = struct.unpack('<I', f.read(4))[0]
    return f.read(length).decode('utf8')

def readPackedVector(f, format):
    packed = struct.unpack('<f', f.read(4))[0]

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

def readMaterials(f):
    material = {}
    material['undeformedDiffuseTexture'] = readLengthString(f)
    material['undeformedNormalMap'] = readLengthString(f)
    material['undeformedPropertiesMap'] = readLengthString(f)
    material['deformedDiffuseTexture'] = readLengthString(f)
    material['deformedNormalMap'] = readLengthString(f)
    material['deformedPropertiesMap'] = readLengthString(f)
    material['normalMapEx3'] = readLengthString(f)
    material['shadowMapTexture'] = readLengthString(f)
    # Skip unknown value
    f.read(4)

    return material

def processLambert(f, blocks):
    verts = []
    faces = []
    uvs = []
    texs = []
    
    #Get Version
    version = struct.unpack('<B', f.read(1))[0]
    
    type = struct.unpack('<I', f.read(4))[0]
    
    #skip
    f.read(40)
    
    #Get Textures
    for i in range(8):
        length = struct.unpack('<I', f.read(4))[0]
        texStr = '<%ds' % length
        tex = struct.unpack(texStr, f.read(length))[0].decode()
        texs.append(tex)
        
        print("Texture: %s" % tex)
        
    #skip unknown data
    f.read(4)
    
    print("Type: %d" % (type))
    
    if(type == 1):
        vertCount = struct.unpack('<I', f.read(4))[0]
        print("Vertices: %d" % vertCount)
        
        for vert in range(vertCount):
            extra1 = struct.unpack('<H', f.read(2))[0]
            extra2 = struct.unpack('<H', f.read(2))[0]
            extra3 = struct.unpack('<H', f.read(2))[0]
            extra4 = struct.unpack('<H', f.read(2))[0]
            
            extra5 = struct.unpack('<f', f.read(4))[0]
            extra6 = struct.unpack('<f', f.read(4))[0]
            extra7 = struct.unpack('<f', f.read(4))[0]
            
            
            x = struct.unpack('<H', f.read(2))[0]
            y = struct.unpack('<H', f.read(2))[0]
            z = struct.unpack('<H', f.read(2))[0]
            
            extra8 = struct.unpack('<H', f.read(2))[0]
            
            print("Data: %d %d %d" % (x, y, z))
            
            
            verts.append((x/65550, z/65550, y/65550))
            
            
        faceCount = struct.unpack('<I', f.read(4))[0]
        print("Faces: %d" % faceCount)
         
        for face in range(int(faceCount/3)):
            vert1 = struct.unpack('<H', f.read(2))[0]
            vert2 = struct.unpack('<H', f.read(2))[0]
            vert3 = struct.unpack('<H', f.read(2))[0]
        
            faces.append((vert1, vert2, vert3))
            
    #Read Check
    check = struct.unpack('<I', f.read(4))[0]
        
    #Add object data
    mesh = bpy.data.meshes.new("Mesh")
    mesh.vertices.add(vertCount)
    mesh.tessfaces.add(faceCount/3)
    
    mesh.vertices.foreach_set("co", unpack_list(verts))
    mesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(faces))
    mesh.tessface_uv_textures.new()
    
    for face in range(int(faceCount/3)):
        uv = mesh.tessface_uv_textures[0].data[face]
        
        #uv.uv1 = uvs[faces[face][0]]
        #uv.uv2 = uvs[faces[face][1]]
        #uv.uv3 = uvs[faces[face][2]]
    
    mesh.validate()
    mesh.update()
    
    obj = bpy.data.objects.new("Mesh_Lambert_0", mesh)

    blocks.append(obj)
        

def processSkinnedGeneral(f, blocks):
    verts = []
    faces = []
    uvs = []
    texs = []
    
    #Get Version
    version = struct.unpack('<B', f.read(1))[0]
    
    #Get Flag
    flag = struct.unpack('<I', f.read(4))[0]
    print("Flag: %d" % flag)
    
    #skip unknown
    f.read(24)
    
    #Get Textures
    for i in range(8):
        length = struct.unpack('<I', f.read(4))[0]
        texStr = '<%ds' % length
        tex = struct.unpack(texStr, f.read(length))[0].decode()
        texs.append(tex)
        
        print("Texture: %s" % tex)
    
        
    #skip unknown data
    f.read(4)
    
    #Check Vertice Type
    if(version == 0 or flag != 0x80000):
        #Small Vertices
        print("Vertex Type: Small")
        
        #Get Vertex Count
        vertCount = struct.unpack('<I', f.read(4))[0]
        print("Vertices: %d" % vertCount)
        
        for vert in range(vertCount):
            x = struct.unpack('<f', f.read(4))[0]
            y = struct.unpack('<f', f.read(4))[0]
            z = struct.unpack('<f', f.read(4))[0]
       
            extra1 = struct.unpack('<B', f.read(1))[0]
            extra2 = struct.unpack('<B', f.read(1))[0]
            extra3 = struct.unpack('<B', f.read(1))[0]
            extra4 = struct.unpack('<B', f.read(1))[0]
            
            extra5 = struct.unpack('<B', f.read(1))[0]
            extra6 = struct.unpack('<B', f.read(1))[0]
            extra7 = struct.unpack('<B', f.read(1))[0]
            extra8 = struct.unpack('<B', f.read(1))[0]
            
            verts.append((x, z, y))
    elif(version == 3 or flag == 0x80000):
        #Small Vertices
        print("Vertex Type: Big")
        
        #Get Vertex Count
        vertCount = struct.unpack('<I', f.read(4))[0]
        print("Vertices: %d" % vertCount)
        
        for vert in range(vertCount):
            x = struct.unpack('<f', f.read(4))[0]
            y = struct.unpack('<f', f.read(4))[0]
            z = struct.unpack('<f', f.read(4))[0]
       
            extra1 = struct.unpack('<I', f.read(4))[0]
            extra2 = struct.unpack('<I', f.read(4))[0]
            extra3 = struct.unpack('<i', f.read(4))[0]
            extra4 = struct.unpack('<I', f.read(4))[0]
            
            verts.append((x, z, y))
            
    #Process Extra Data
    uvCount = struct.unpack('<I', f.read(4))[0]
    print("UVs: %d" % uvCount)
    
    for uv in range(uvCount):
        r = struct.unpack('<I', f.read(4))[0]
        g = struct.unpack('<I', f.read(4))[0]
        b = struct.unpack('<I', f.read(4))[0]
        
        u = struct.unpack('<f', f.read(4))[0]
        v = struct.unpack('<f', f.read(4))[0]
        
        uvs.append((u, 1-v))
        
    #Process SkinBatch/Weights
    skinCount = struct.unpack('<I', f.read(4))[0]
    print("Skin: %d" % skinCount)
    
    for skin in range(skinCount):
        
        #skip unknown data
        f.read(8)
        
        #weights
        weightCount = struct.unpack('<I', f.read(4))[0]
        print("Weights: %d" % weightCount)
        
        for weight in range(weightCount):
            w = struct.unpack('<H', f.read(2))
            #print("Weight: %d" % w)
            
    #process faces
    faceCount = struct.unpack('<I', f.read(4))[0]
    print("Faces: %d" % faceCount)
     
    for face in range(int(faceCount/3)):
        vert1 = struct.unpack('<H', f.read(2))[0]
        vert2 = struct.unpack('<H', f.read(2))[0]
        vert3 = struct.unpack('<H', f.read(2))[0]
        
        
        
        faces.append((vert1, vert3, vert2))
    
    #Read Check
    check = struct.unpack('<I', f.read(4))[0]
        
    #Add object data
    mesh = bpy.data.meshes.new("Mesh")
    mesh.vertices.add(vertCount)
    mesh.tessfaces.add(faceCount/3)
    
    mesh.vertices.foreach_set("co", unpack_list(verts))
    mesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(faces))
    mesh.tessface_uv_textures.new()
    
    for face in range(int(faceCount/3)):
        uv = mesh.tessface_uv_textures[0].data[face]
        
        uv.uv1 = uvs[faces[face][0]]
        uv.uv2 = uvs[faces[face][1]]
        uv.uv3 = uvs[faces[face][2]]
    
    mesh.validate()
    mesh.update()
    
    obj = bpy.data.objects.new("Mesh_SkinnedGeneral_0", mesh)

    blocks.append(obj)
        
        

class CarPaintBlock:
    class CarPaint0:
        def read(self, f):
            self.x = struct.unpack('<f', f.read(4))[0]
            self.y = struct.unpack('<f', f.read(4))[0]
            self.z = struct.unpack('<f', f.read(4))[0]
            self.w = struct.unpack('<f', f.read(4))[0]
                   
            self.texCoordA = (struct.unpack('<H', f.read(2))[0])
            self.texCoordB = (struct.unpack('<H', f.read(2))[0])
            self.texCoordC = (struct.unpack('<H', f.read(2))[0])
            self.texCoordD = (struct.unpack('<H', f.read(2))[0])   

    class CarPaint1:
        def read(self, f):
            self.u = struct.unpack('<f', f.read(4))[0]
            self.v = struct.unpack('<f', f.read(4))[0]
            self.w = struct.unpack('<f', f.read(4))[0]

            self.normal = readPackedVector(f, 'XZY')
            self.deformedNormal = readPackedVector(f, 'XZY')
            self.tangent = readPackedVector(f, 'ZXY')
            self.deformedTangent = readPackedVector(f, 'ZXY')

    NameHash = 0xCD931E75

    @staticmethod
    def read(f, blocks):
        #Get Version
        version = struct.unpack('<B', f.read(1))[0]
        
        # Skip unknown data
        f.read(56)

        # Read in the materials
        materials = readMaterials(f)
        # Read in the CarPaint0 blocks
        carPaintData0 = []
        carPaintData0Count = struct.unpack('<I', f.read(4))[0]
        for i in range(carPaintData0Count):
            carPaint = CarPaintBlock.CarPaint0()
            carPaint.read(f)

            carPaintData0.append(carPaint)

        # Read in the CarPaint1 blocks
        carPaintData1 = []
        carPaintData1Count = struct.unpack('<I', f.read(4))[0]
        for i in range(carPaintData1Count):
            carPaint = CarPaintBlock.CarPaint1()
            carPaint.read(f)

            carPaintData1.append(carPaint)

        # Read in the faces
        faceCount = struct.unpack('<I', f.read(4))[0]
        
        faces = []
        for face in range(int(faceCount/3)):
            vert1 = struct.unpack('<H', f.read(2))[0]
            vert2 = struct.unpack('<H', f.read(2))[0]
            vert3 = struct.unpack('<H', f.read(2))[0]

            faces.append((vert1, vert3, vert2))

        deformTable = []
        for i in range(256):
            deformTable.append(struct.unpack('<I', f.read(4))[0])

        # Create Mesh
        mesh = bpy.data.meshes.new('Mesh')

        mesh.vertices.add(len(carPaintData0))
        mesh.tessfaces.add(int(len(faces)))

        # Build the vertices
        for i in range(len(carPaintData0)):
            data0 = carPaintData0[i]
            data1 = carPaintData1[i]

            vert = mesh.vertices[i]
            # Blender uses a right handed coordinate system, so Z is up.
            vert.co = [data0.x, data0.z, data0.y]
            vert.normal = data1.normal

        # Build the faces
        for i in range(len(faces)):
            tessFace = mesh.tessfaces[i]
            tessFace.vertices = faces[i]
            tessFace.use_smooth = True

        # Build the textures        
        uvTexture = mesh.tessface_uv_textures.new()

        for face in range(len(faces)):
            uv = uvTexture.data[face]

            tmp = faces[face][0]
            uv.uv1 = [carPaintData1[tmp].u, 1-carPaintData1[tmp].v]

            tmp = faces[face][1]
            uv.uv2 = [carPaintData1[tmp].u, 1-carPaintData1[tmp].v]

            tmp = faces[face][2]
            uv.uv3 = [carPaintData1[tmp].u, 1-carPaintData1[tmp].v]

        material = bpy.data.materials.new('DiffuseMaterial')
        mesh.materials.append(material)

        # Load up the diffuse texture
        diffTex = bpy.data.textures.new('DiffuseTexture', 'IMAGE')
        diffTex.image = bpy.data.images.load(filepath=os.path.join(currentLoadPath, materials['undeformedDiffuseTexture']))

        # Set the texture parameters
        diffTexSlot = material.texture_slots.create(0)
        diffTexSlot.texture_coords = 'UV'
        diffTexSlot.texture = diffTex

        # Load up the normal mapping texture
        bumpMapTex = bpy.data.textures.new('NormalTexture', 'IMAGE')
        bumpMapTex.image = bpy.data.images.load(filepath=os.path.join(currentLoadPath, materials['undeformedNormalMap']))

        # Set the texture parameters
        bumpMapTexSlot = material.texture_slots.create(1)
        bumpMapTexSlot.texture_coords = 'UV'
        bumpMapTexSlot.texture = bumpMapTex
        # This is a normal mapping, so we don't want colours
        bumpMapTexSlot.use_map_color_diffuse = False
        # But we do want to flag it as a normal map..
        bumpMapTexSlot.use_map_normal = True

        mesh.validate()
        mesh.update()

        obj = bpy.data.objects.new('Mesh_CarPaint', mesh)
        blocks.append(obj)

class CarPaintSimpleBlock:
    class CarPaint0:
        def read(self, f):
            self.x = struct.unpack('<f', f.read(4))[0]
            self.y = struct.unpack('<f', f.read(4))[0]
            self.z = struct.unpack('<f', f.read(4))[0]

            self.packed1 = readPackedVector(f, 'XZY')
            self.u = struct.unpack('<f', f.read(4))[0]
            self.v = struct.unpack('<f', f.read(4))[0]
            self.packed2 = readPackedVector(f, 'XYZ')
            self.packed3 = readPackedVector(f, 'XYZ')

    NameHash = 0x81938490

    def read(f, blocks):
        version = struct.unpack('<B', f.read(1))[0]

        # Skip unknown data
        f.read(56)

        # Read in the materials
        materials = readMaterials(f)

        # Read in the CarPaint0 blocks
        carPaintData0 = []
        carPaintData0Count = struct.unpack('<I', f.read(4))[0]
        for i in range(carPaintData0Count):
            carPaint = CarPaintSimpleBlock.CarPaint0()
            carPaint.read(f)

            carPaintData0.append(carPaint) 

        # Read in the faces
        faceCount = struct.unpack('<I', f.read(4))[0]

        faces = []
        for face in range(int(faceCount/3)):
            vert1 = struct.unpack('<H', f.read(2))[0]
            vert2 = struct.unpack('<H', f.read(2))[0]
            vert3 = struct.unpack('<H', f.read(2))[0]

            faces.append((vert1, vert3, vert2))

        # Create Mesh
        mesh = bpy.data.meshes.new('Mesh')

        mesh.vertices.add(len(carPaintData0))
        mesh.tessfaces.add(int(len(faces)))

        for i in range(len(carPaintData0)):
            data0 = carPaintData0[i]

            vert = mesh.vertices[i]
            # Blender uses a right handed coordinate system, so Z is up.
            vert.co = [data0.x, data0.z, data0.y]
            #vert.normal = data1.normal

        for i in range(len(faces)):
            tessFace = mesh.tessfaces[i]
            tessFace.vertices = faces[i]
            tessFace.use_smooth = True
        
        uvTexture = mesh.tessface_uv_textures.new()

        for face in range(len(faces)):
            uv = uvTexture.data[face]

            tmp = faces[face][0]
            uv.uv1 = [carPaintData0[tmp].u, 1-carPaintData0[tmp].v]

            tmp = faces[face][1]
            uv.uv2 = [carPaintData0[tmp].u, 1-carPaintData0[tmp].v]

            tmp = faces[face][2]
            uv.uv3 = [carPaintData0[tmp].u, 1-carPaintData0[tmp].v]

        material = bpy.data.materials.new('DiffuseMaterial')
        mesh.materials.append(material)

        # Load up the diffuse texture
        diffTex = bpy.data.textures.new('DiffuseTexture', 'IMAGE')
        diffTex.image = bpy.data.images.load(filepath=os.path.join(currentLoadPath, materials['undeformedDiffuseTexture']))

        # Set the texture parameters
        diffTexSlot = material.texture_slots.create(0)
        diffTexSlot.texture_coords = 'UV'
        diffTexSlot.texture = diffTex

        # Load up the normal mapping texture
        bumpMapTex = bpy.data.textures.new('NormalTexture', 'IMAGE')
        bumpMapTex.image = bpy.data.images.load(filepath=os.path.join(currentLoadPath, materials['undeformedNormalMap']))

        # Set the texture parameters
        bumpMapTexSlot = material.texture_slots.create(1)
        bumpMapTexSlot.texture_coords = 'UV'
        bumpMapTexSlot.texture = bumpMapTex
        # This is a normal mapping, so we don't want colours
        bumpMapTexSlot.use_map_color_diffuse = False
        # But we do want to flag it as a normal map..
        bumpMapTexSlot.use_map_normal = True

        mesh.validate()
        mesh.update()

        obj = bpy.data.objects.new('Mesh_CarPaintSimple', mesh)
        blocks.append(obj)

def processDeformableWindow(f, blocks):
    verts = []
    faces = []
    uvs = []
    texs = []
    
    print("44 Bytes")
    
    #Get Version
    version = struct.unpack('<B', f.read(1))[0]
    
    #Get Textures
    for i in range(8):
        length = struct.unpack('<I', f.read(4))[0]
        texStr = '<%ds' % length
        tex = struct.unpack(texStr, f.read(length))[0].decode()
        texs.append(tex)
        
        print("Texture: %s" % tex)
        
    #skip unknown data
    f.read(4)
    
    #skip unknown data
    if(version == 2):
        f.read(1024)
    

    #Get Vertices
    vertCount = struct.unpack('<I', f.read(4))[0]
    print("Vertices: %d" % vertCount)
    
    for vert in range(vertCount):
        
        x = struct.unpack('<f', f.read(4))[0]
        y = struct.unpack('<f', f.read(4))[0]
        z = struct.unpack('<f', f.read(4))[0]
        w = struct.unpack('<f', f.read(4))[0]
        
        extra1 = struct.unpack('<f', f.read(4))[0]
        extra2 = struct.unpack('<f', f.read(4))[0]
        extra3 = struct.unpack('<f', f.read(4))[0]
        extra4 = struct.unpack('<f', f.read(4))[0]
        extra5 = struct.unpack('<f', f.read(4))[0]
        extra6 = struct.unpack('<f', f.read(4))[0]
        
        u = struct.unpack('<f', f.read(4))[0]
        v = struct.unpack('<f', f.read(4))[0]
        
        verts.append((x, z, y))
        uvs.append((u, 1-v))
        
    #Get Faces
    faceCount = struct.unpack('<I', f.read(4))[0]
    print("Faces: %d" % faceCount)
    
    for face in range(int(faceCount/3)):
        
        vert1 = struct.unpack('<H', f.read(2))[0]
        vert2 = struct.unpack('<H', f.read(2))[0]
        vert3 = struct.unpack('<H', f.read(2))[0]

        faces.append((vert1, vert3, vert2))

    #skip unknown data
    if(version == 1):
        f.read(1024)

    #Read Check
    check = struct.unpack('<I', f.read(4))[0]
    
    #Add object data
    mesh = bpy.data.meshes.new("Mesh")
    mesh.vertices.add(vertCount)
    mesh.tessfaces.add(faceCount/3)
    
    mesh.vertices.foreach_set("co", unpack_list(verts))
    mesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(faces))
    mesh.tessface_uv_textures.new()
    
    for face in range(int(faceCount/3)):
        uv = mesh.tessface_uv_textures[0].data[face]
        
        uv.uv1 = uvs[faces[face][0]]
        uv.uv2 = uvs[faces[face][1]]
        uv.uv3 = uvs[faces[face][2]]
    
    mesh.validate()
    mesh.update()
    
    obj = bpy.data.objects.new("Mesh_DeformableWindow_0", mesh)

    blocks.append(obj)
    
# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportSomeData(Operator, ImportHelper):
    '''This appears in the tooltip of the operator and in the generated docs'''
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import .RBM"

    # ImportHelper mixin class uses this
    filename_ext = ".rbm"

    filter_glob = StringProperty(
            default="*.rbm",
            options={'HIDDEN'},
            )

    def execute(self, context):
        print('opening rbm')
        return readRBM(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Render Block Model (.rbm)")


def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')

# exec(open('D:\Just Cause 2 RE\jc2-rbm-tools\import.py').read())
#if __name__ == "__main__":
    #readRBM(C, r'D:\Just Cause 2 RE\Extracted Archives\pc1\exported\vehicles\lave\lave.v045_firetruck_unpack\v045-body_m_lod1.rbm')