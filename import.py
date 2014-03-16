import bpy
import struct
from bpy_extras.io_utils import unpack_list, unpack_face_list


def read_some_data(context, filepath, use_some_setting):
    print("running read_some_data...")
    
    
    f = open(filepath, 'rb')
    
    blocks = []
    
    #Read Header
    headerLength = struct.unpack('<i', f.read(4))[0]
    headerStr = '<%ds' % headerLength
    header = struct.unpack(headerStr, f.read(5))[0].decode()
    print(header)
    
    #skip unknown
    unk1 = struct.unpack('<i', f.read(4))[0]
    unk2 = struct.unpack('<i', f.read(4))[0]
    unk3 = struct.unpack('<i', f.read(4))[0]
    
    #Get Min and Max x, y, z
    minX = struct.unpack('<f', f.read(4))[0]
    minY = struct.unpack('<f', f.read(4))[0]
    minZ = struct.unpack('<f', f.read(4))[0]
    maxX = struct.unpack('<f', f.read(4))[0]
    maxY = struct.unpack('<f', f.read(4))[0]
    maxZ = struct.unpack('<f', f.read(4))[0]
    
    print("Max X: %f Max Y: %f Max Z: %f\nMin X: %f Min Y: %f Min Z: %f" % (maxX, maxY, maxZ, minX, minY, minZ))
    
    #get number of render blocks
    blockCount = struct.unpack('<i', f.read(4))[0]
    
    print("Bytes: %d" % int(f.tell()))
    
    #Process every render block
    for block in range(blockCount):
        blockType = struct.unpack('<I', f.read(4))[0]
        
        print("BlockType: %d" % blockType)
        
        if(blockType == 2173928592):
            processCarPaintSimple(f, blocks)
        elif(blockType == 3448970869):
            processCarPaint(f, blocks)
        elif(blockType == 112326146):
            processDeformableWindow(f, blocks)
        elif(blockType == 1583709984):
            processSkinnedGeneral(f, blocks)
        elif(blockType == 3587672800):
            processLambert(f, blocks)
            
    
    f.close()
    
    for block in blocks:
        base = bpy.context.scene.objects.link(block)
        base.select = True

    return {'FINISHED'}

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
        
        

def processCarPaint(f, blocks):
    verts = []
    faces = []
    uvs = []
    texs = []
    normals = []
    
    print("Bytes: %d" % int(f.tell()))
    
    #Get Version
    version = struct.unpack('<B', f.read(1))[0]
    
    #Skip unknwon data
    f.read(56)
    
    #Get Textures
    for i in range(8):
        length = struct.unpack('<I', f.read(4))[0]
        texStr = '<%ds' % length
        tex = struct.unpack(texStr, f.read(length))[0].decode()
        texs.append(tex)
        
        print("Texture: %s" % tex)
        
    #skip unknown data
    f.read(4)
    
    #Get Vertices
    vertCount = struct.unpack('<I', f.read(4))[0]
    print("Vertices: %d" % vertCount)
    
    for vert in range(vertCount):
        
        x = struct.unpack('<f', f.read(4))[0]
        y = struct.unpack('<f', f.read(4))[0]
        z = struct.unpack('<f', f.read(4))[0]
        w = struct.unpack('<f', f.read(4))[0]
               
        extra1 = (struct.unpack('<H', f.read(2))[0])
        extra2 = (struct.unpack('<H', f.read(2))[0])
        extra3 = (struct.unpack('<H', f.read(2))[0])
        extra4 = (struct.unpack('<H', f.read(2))[0])
        
        print("%d %d %d %d" %(extra1, extra2, extra3, extra4))
        #print("%d %d" %(extra1, extra2))
        
        normals.append(((extra1/65536), (extra2/65536), (extra3/65536), (extra4/65536), w/65536))
        
        #skip data
        #f.read(4)
        
        verts.append((x, z, y))
        
     
    #Get Extra Data
    uvCount = struct.unpack('<I', f.read(4))[0]
    print("Uvs: %d" % uvCount)
        
     
    for uv in range(uvCount):  
        u = struct.unpack('<f', f.read(4))[0]
        v = struct.unpack('<f', f.read(4))[0]
        w = struct.unpack('<f', f.read(4))[0]
        
        extra1 = struct.unpack('<f', f.read(4))[0]
        extra2 = struct.unpack('<f', f.read(4))[0]
        extra3 = struct.unpack('<f', f.read(4))[0]
        extra4 = struct.unpack('<f', f.read(4))[0]
        
        #normals.append(((extra1/65536), (extra2/65536), (extra3/65536), (extra4/65536), w/65536))
        
        uvs.append((u, 1-v))   
        
    #Get Faces
    faceCount = struct.unpack('<I', f.read(4))[0]
    print("Faces: %d" % faceCount)
    
    for face in range(int(faceCount/3)):
        
        vert1 = struct.unpack('<H', f.read(2))[0]
        vert2 = struct.unpack('<H', f.read(2))[0]
        vert3 = struct.unpack('<H', f.read(2))[0]

        faces.append((vert1, vert3, vert2))

    
    
    #Skip unknown array
    f.read(1024)

    #Read Check
    check = struct.unpack('<I', f.read(4))[0]
    
        
    print("Bytes: %d" % int(f.tell()))
    
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
    
    obj = bpy.data.objects.new("Mesh_CarPaint_0", mesh)
    
    normalX = obj.vertex_groups.new("NormalX")
    normalY = obj.vertex_groups.new("NormalY")
    normalZ = obj.vertex_groups.new("NormalZ")
    normalW = obj.vertex_groups.new("NormalW")
    normalA = obj.vertex_groups.new("NormalA")
    
    for n in range(vertCount): 
        vertIndices = []
        
        vertIndices.append(n)
        
        normalX.add(vertIndices, normals[n][0], 'REPLACE')
        normalY.add(vertIndices, normals[n][1], 'REPLACE')
        normalZ.add(vertIndices, normals[n][2], 'REPLACE')
        normalW.add(vertIndices, normals[n][3], 'REPLACE')
        normalA.add(vertIndices, normals[n][4], 'REPLACE')
        
        #print((normals[n][0]-0.5)*131072)

    blocks.append(obj)

def calcTangent(uv1, uv2, uv3, vert1, vert2, vert3):
    x1 = vert2.x - vert1.x;
    x2 = vert3.x - vert1.x;
    
    y1 = vert2.y - vert1.y;
    y2 = vert3.y - vert1.y;
    
    z1 = vert2.z - vert1.z;
    z2 = vert3.z - vert1.z;
    
    s1 = uv2.x - uv1.x;
    s2 = uv3.x - uv1.x;
    
    t1 = uv2.y - uv1.y;
    t2 = uv3.y - uv1.y;
    
    float
    

def processCarPaintSimple(f, blocks):
    verts = []
    faces = []
    uvs = []
    normals = []
    texs = []
    
    #Get Version
    version = struct.unpack('<B', f.read(1))[0]
    
    #skip unknown
    #f.read(56)
    
    print("Bytes: %d" % int(f.tell()))
    
    print( struct.unpack('<f', f.read(4))[0] )
    print( struct.unpack('<f', f.read(4))[0] )
    print( struct.unpack('<f', f.read(4))[0] )
    print( struct.unpack('<f', f.read(4))[0] )
    print( struct.unpack('<f', f.read(4))[0] )
    print( struct.unpack('<f', f.read(4))[0] )
    print( struct.unpack('<f', f.read(4))[0] )
    print( struct.unpack('<f', f.read(4))[0] )
    print( struct.unpack('<f', f.read(4))[0] )

    print("Bytes: %d" % int(f.tell()))
    
    print( struct.unpack('<I', f.read(4))[0] )
    print( struct.unpack('<I', f.read(4))[0] )
    print( struct.unpack('<I', f.read(4))[0] )
    print( struct.unpack('<I', f.read(4))[0] )
    print( struct.unpack('<I', f.read(4))[0] )
   
    print("Bytes: %d" % int(f.tell()))
   
    #Get Textures
    for i in range(8):
        length = struct.unpack('<I', f.read(4))[0]
        texStr = '<%ds' % length
        tex = struct.unpack(texStr, f.read(length))[0].decode()
        texs.append(tex)
        
        print("Texture: %s" % tex)
        
    #skip unknown data
    print(struct.unpack('<I', f.read(4))[0])


    #Get Vertic
    vertCount = struct.unpack('<I', f.read(4))[0]
    print("Vertices: %d" % vertCount)
    
    for vert in range(vertCount):
        
        x = -struct.unpack('<f', f.read(4))[0]
        y = struct.unpack('<f', f.read(4))[0]
        z = struct.unpack('<f', f.read(4))[0]
        w = struct.unpack('<f', f.read(4))[0]
        
        u = struct.unpack('<f', f.read(4))[0]
        v = struct.unpack('<f', f.read(4))[0]
        
        extra1 = (struct.unpack('<H', f.read(2))[0])
        extra2 = (struct.unpack('<H', f.read(2))[0])
        extra3 = (struct.unpack('<H', f.read(2))[0])
        extra4 = (struct.unpack('<H', f.read(2))[0])
        
        
        
        
        verts.append((x, z, y))
        uvs.append((u, 1-v))
        normals.append(((extra1/65536), (extra2/65536), (extra3/65536), (extra4/65536), w/65536))
        
    #Get Faces
    faceCount = struct.unpack('<I', f.read(4))[0]/3
    print("Faces: %d" % faceCount)
    
    for face in range(int(faceCount)):
        vert1 = struct.unpack('<H', f.read(2))[0]
        vert2 = struct.unpack('<H', f.read(2))[0]
        vert3 = struct.unpack('<H', f.read(2))[0]
        
        faces.append((vert1, vert2, vert3))


    #Read Check
    check = struct.unpack('<I', f.read(4))[0]
    
    print("Bytes: %d" % int(f.tell()))
    
    #Add object data
    mesh = bpy.data.meshes.new("Mesh")
    mesh.vertices.add(vertCount)
    mesh.tessfaces.add(faceCount)
    
    mesh.vertices.foreach_set("co", unpack_list(verts))
    mesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(faces))
    mesh.tessface_uv_textures.new()
    
    for face in range(int(faceCount)):
        uv = mesh.tessface_uv_textures[0].data[face]

        uv.uv1 = uvs[faces[face][0]]
        uv.uv2 = uvs[faces[face][1]]
        uv.uv3 = uvs[faces[face][2]]
    
    mesh.validate()
    mesh.update()
    
    obj = bpy.data.objects.new("Mesh_CarPaintSimple_0", mesh)
    
    normalX = obj.vertex_groups.new("NormalX")
    normalY = obj.vertex_groups.new("NormalY")
    normalZ = obj.vertex_groups.new("NormalZ")
    normalW = obj.vertex_groups.new("NormalW")
    normalA = obj.vertex_groups.new("NormalA")
    
    for n in range(vertCount): 
        vertIndices = []
        mesh.vertices[n].normal
        vertIndices.append(n)
        
        normalX.add(vertIndices, normals[n][0], 'REPLACE')
        normalY.add(vertIndices, normals[n][1], 'REPLACE')
        normalZ.add(vertIndices, normals[n][2], 'REPLACE')
        normalW.add(vertIndices, normals[n][3], 'REPLACE')
        normalA.add(vertIndices, normals[n][4], 'REPLACE')

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

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )

    type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
            )

    def execute(self, context):
        return read_some_data(context, self.filepath, self.use_setting)


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
