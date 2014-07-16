import bpy
import struct
import math

newUvs = []
newVerts = []
newExtra5 = []
newIndex = []

def pack(vec):
    vec = [(x + 1)/2 for x in vec]
    return sum([a*b for a,b in zip(vec, [1, 256, 65536])])

def checkUV(uv, vert, extra5):
    
    for u in range(len(newUvs)):
        if((newUvs[u] == uv) & (newVerts[u] == vert) & (newExtra5[u].z == extra5.z) & (newExtra5[u].y == extra5.y)):
            return u
            
    return -1

def calculateMinMax(mesh):
    
    minX = 10000
    minY = 10000
    minZ = 10000
    maxX = -10000
    maxY = -10000
    maxZ = -10000
    
    for i in range(len(mesh.vertices)):
        vert = mesh.vertices[i].co
       
        #X
        if(vert.x < minX):
           minX = vert.x
        
        if(vert.x > maxX):
           maxX = vert.x
        
        #Y   
        if(vert.y < minY):
           minY = vert.y
        
        if(vert.y > maxY):
           maxY = vert.y
         
        #Z  
        if(vert.z < minZ):
           minZ = vert.z
           
        if(vert.z > maxZ):
           maxZ = vert.z
           
    
    return (minX, minY, minZ, maxX, maxY, maxZ)

def calculateIndices(mesh, object):      
    
    uvs = mesh.uv_layers.active.data[:]
    verts = mesh.vertices
    extras = object.vertex_groups[:]
    
    count = 0
    counter = 0
    
    for polys in mesh.polygons:
        verts_in_face = polys.vertices[:]
    
        for v in verts_in_face:
            
            check = checkUV(uvs[count].uv, verts[v].co, polys.normal)
            
            if(check == -1):
                newUvs.append(uvs[count].uv)
                newVerts.append(verts[v].co)
                newExtra5.append(polys.normal)
                newIndex.append(counter)
                counter += 1
                
            elif(check != -1):
                newIndex.append(check)
            
            count += 1  

def write_some_data(context, filepath, use_some_setting):
    print("running write_some_data...")
    
    #get object
    objs = bpy.context.selected_objects
    
    f = open(filepath, 'wb')
    f2 = open("C:\\Users\\mikec_000\\Desktop\\export.txt", 'w')
    
    f.write(struct.pack("<i", 5))
    
    f.write(struct.pack("<5s", 'RBMDL'.encode()))
    
    #unknown data
    f.write(struct.pack("<I", 1))
    f.write(struct.pack("<I", 13))
    f.write(struct.pack("<I", 0))
    
    f2.write("%i\n"%1)
    f2.write("%i\n"%13)
    f2.write("%i\n"%0)
    
    MinMax = calculateMinMax(objs[0].data)
    
    #Min max values
    f.write(struct.pack("<f", MinMax[0]))
    f.write(struct.pack("<f", MinMax[2]))
    f.write(struct.pack("<f", MinMax[1]))
    f.write(struct.pack("<f", MinMax[3]))
    f.write(struct.pack("<f", MinMax[5]))
    f.write(struct.pack("<f", MinMax[4]))
    
    f2.write("%f\n"%MinMax[0])
    f2.write("%f\n"%MinMax[2])
    f2.write("%f\n"%MinMax[1])
    f2.write("%f\n"%MinMax[3])
    f2.write("%f\n"%MinMax[5])
    f2.write("%f\n"%MinMax[4])
    
    #The number of blocks write carpaintsimple
    f.write(struct.pack("<I", len(objs)))
    
    for obj in range(len(objs)):
        mesh = objs[obj].data
        
        blockType = objs[obj].name.split('_')[1]
        
        if(blockType == "CarPaintSimple"):
            processCarPaintSimple(f, f2, mesh, objs[obj])
        elif(blockType == "CarPaint"):
            processCarPaint(f, mesh)
        elif(blockType == 112326146):
            processDeformableWindow(f, mesh)
        elif(blockType == "SkinnedGeneral"):
            processSkinnedGeneral(f, mesh)

    f.close()

    return {'FINISHED'}

def processCarPaint(f, mesh):
    print("CarPaint")
    
    f.write(struct.pack("<I" , 3448970869))
    
    #block version
    f.write(struct.pack("<B", 3))
    
    
    #unknown material settings
    f.write(struct.pack("<f", 0.0020288010127842426))
    f.write(struct.pack("<f", 0.49314092844724655))
    f.write(struct.pack("<f", 0.06030166149139404))
    f.write(struct.pack("<f", 0.00697691785171628))
    f.write(struct.pack("<f", 0.07870697975158691))
    f.write(struct.pack("<f", 0.10956159979104996))
    f.write(struct.pack("<f", 30.0))
    f.write(struct.pack("<f", 0))
    f.write(struct.pack("<f", 0.4000000059604645))
    
    #unknown ints
    f.write(struct.pack("<I", 1045220557))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 1053609165))
    f.write(struct.pack("<I", 1058642330))
    f.write(struct.pack("<I", 1280))
    
   
    
    #textures
    tex1 = "v067_body_dif.dds"
    tex2 = "flattangentspace_nrm.dds"
    tex3 = "v067_body_mpm.dds"
    
    #write textures
    f.write(struct.pack("<I", len(tex1)))
    f.write(struct.pack(("<%ds" % len(tex1)), tex1.encode()))
    
    f.write(struct.pack("<I", len(tex2)))
    f.write(struct.pack(("<%ds" % len(tex2)), tex2.encode()))
    
    f.write(struct.pack("<I", len(tex3)))
    f.write(struct.pack(("<%ds" % len(tex3)), tex3.encode()))
    
    #Empty textures
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    
    #uknown data
    f.write(struct.pack("<I", 3))
    
    
    #write vertex data

    vertexCount = VerticesSize(mesh)
    f.write(struct.pack("<I", vertexCount))
    print("Vertices: %f" % (vertexCount))
        
    #for each vertex
    count = 0;
    
    for polys in mesh.polygons:
        verts_in_face = polys.vertices
        
        print("Normal: %d %d %d" % (polys.normal.x, polys.normal.y, polys.normal.z))

        for v in verts_in_face:
            #vertex positions
            f.write(struct.pack("<f", mesh.vertices[v].co.x))
            f.write(struct.pack("<f", mesh.vertices[v].co.z))
            f.write(struct.pack("<f", mesh.vertices[v].co.y))
            f.write(struct.pack("<f", 0))
            
            # unknown
            f.write(struct.pack("<H", 0))
            f.write(struct.pack("<H", 0))
            f.write(struct.pack("<H", 0))
            f.write(struct.pack("<H", 0))
            
    #Get Extra Data
    f.write(struct.pack("<I", vertexCount))
    print("UVs: %f" % (vertexCount))
    
    for polys in mesh.polygons:
        verts_in_face = polys.vertices
        uvLayer = mesh.uv_layers.active.data[:]
        
        for v in verts_in_face:
            u1 = uvLayer[count].uv.x
            v1 = 1 - uvLayer[count].uv.y
            
            f.write(struct.pack("<f", u1))
            f.write(struct.pack("<f", v1))
            f.write(struct.pack("<f", 0))
            
            
            norm = mesh.vertices[v].normal
            packedNorm = pack([norm.x, norm.z, norm.y])

            #tangent = mesh.vertices[v].tangent
            #packedTangent = pack([norm.z, norm.x, norm.y])

            f.write(struct.pack("<f", packedNorm))
            f.write(struct.pack("<f", 0))
            f.write(struct.pack("<f", packedNorm))
            f.write(struct.pack("<f", 0))

    #write faces
    f.write(struct.pack("<I", vertexCount))
    print("Faces: %f" % (vertexCount))
        
    for i in range(vertexCount):
        f.write(struct.pack("<H", i))
    
    #unknown array
    for i in range(256):
        f.write(struct.pack("<f", 1.0))
    
    f.write(struct.pack("<i", -1985229329))
    
def processDeformableWindow(f, mesh):
    print("Deformable Window")
    
def processSkinnedGeneral(f, mesh):
    print("Skinned General")
    f.write(struct.pack("<I" , 1583709984))
    
    
    #Get Version
    f.write(struct.pack("<B", 1))
    
    #Flag
    f.write(struct.pack("<I", 1048576))
    
    #write unknown
    f.write(struct.pack("<f", 0.363132))
    f.write(struct.pack("<f", 0))
    f.write(struct.pack("<f", 0))
    f.write(struct.pack("<f", 0.363132))
    f.write(struct.pack("<f", 0))
    f.write(struct.pack("<f", 0))
    
    #textures
    tex1 = "v071_wings.dds"
    tex2 = "flattangentspace_nrm.dds"
    tex3 = "v071_mpm.dds"
    
    #write textures
    f.write(struct.pack("<I", len(tex1)))
    f.write(struct.pack(("<%ds" % len(tex1)), tex1.encode()))
    
    f.write(struct.pack("<I", len(tex2)))
    f.write(struct.pack(("<%ds" % len(tex2)), tex2.encode()))
    
    f.write(struct.pack("<I", len(tex3)))
    f.write(struct.pack(("<%ds" % len(tex3)), tex3.encode()))
    
    #Empty textures
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    
    #write unknown data
    f.write(struct.pack("<I", 0))
    
    #store vertices
    vertCount = VerticesSize(mesh)
    f.write(struct.pack("<I", vertCount))
    
    
    
    
def processCarPaintSimple(f, f2, mesh, object):
    f.write(struct.pack("<I" , 2173928592))
    
    #block version
    f.write(struct.pack("<B", 1))
    
    
    #unknown material settings
    f.write(struct.pack("<f", 0.0020288010127842426))
    f.write(struct.pack("<f", 0.49314092844724655))
    f.write(struct.pack("<f", 0.06030166149139404))
    f.write(struct.pack("<f", 0.00697691785171628))
    f.write(struct.pack("<f", 0.07870697975158691))
    f.write(struct.pack("<f", 0.10956159979104996))
    f.write(struct.pack("<f", 30.0))
    f.write(struct.pack("<f", 0))
    f.write(struct.pack("<f", 0.4000000059604645))
    
    #unknown ints
    f.write(struct.pack("<I", 1045220557))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 1053609165))
    f.write(struct.pack("<I", 1058642330))
    f.write(struct.pack("<I", 1280))
    
   
    
    #textures
    tex1 = "v067_body_dif.dds"
    tex2 = "flattangentspace_nrm.dds"
    tex3 = "v067_body_mpm.dds"
    
    #write textures
    f.write(struct.pack("<I", len(tex1)))
    f.write(struct.pack(("<%ds" % len(tex1)), tex1.encode()))
    
    f.write(struct.pack("<I", len(tex2)))
    f.write(struct.pack(("<%ds" % len(tex2)), tex2.encode()))
    
    f.write(struct.pack("<I", len(tex3)))
    f.write(struct.pack(("<%ds" % len(tex3)), tex3.encode()))
    
    #Empty textures
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    f.write(struct.pack("<I", 0))
    
    #uknown data
    f.write(struct.pack("<I", 3))
    
    
    #write vertex data

    vertexCount = VerticesSize(mesh)
    f.write(struct.pack("<I", vertexCount))
    print("Vertices: %f" % (vertexCount))
        
    #for each vertex
    count = 0;
    
    for polys in mesh.polygons:
        verts_in_face = polys.vertices
        
        uvLayer = mesh.uv_layers.active.data[:]
    
        for v in verts_in_face:
            
            norm = mesh.vertices[v].normal
            
            normalX = 32000+(norm.y*32000)
            normalZ = ((math.acos(-norm.z/1)/3.14159)*64000)
            normalY = 32000+((math.atan2(norm.z, norm.x)/3.14159)*32000)
            
            
            #print("Norm Y: %f" % normalY)
            
            #vertex positions
            f.write(struct.pack("<f", -mesh.vertices[v].co.x))
            f.write(struct.pack("<f", mesh.vertices[v].co.z))
            f.write(struct.pack("<f", mesh.vertices[v].co.y))
            f.write(struct.pack("<f", normalX))
            
            u1 = uvLayer[count].uv.x
            v1 = 1 - uvLayer[count].uv.y
            
            f.write(struct.pack("<f", u1))
            f.write(struct.pack("<f", v1))
            
            f.write(struct.pack("<H", int(math.floor(normalZ))))
            f.write(struct.pack("<H", 23000))
            f.write(struct.pack("<H", int(math.floor(normalY))))
            f.write(struct.pack("<H", 23000))
            
            count += 1

    #write faces
    f.write(struct.pack("<I", vertexCount))
    print("Faces: %f" % (vertexCount))
        
    for i in range(vertexCount):
        f.write(struct.pack("<H", i))
    
    
    f.write(struct.pack("<i", -1985229329))

def VerticesSize(mesh):
    vertCount = 0
    
    for polys in mesh.polygons:
        verts_in_face = polys.vertices[:]
        
        for v in verts_in_face:
            vertCount += 1
    
    return vertCount

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportSomeData(Operator, ExportHelper):
    '''This appears in the tooltip of the operator and in the generated docs'''
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Some Data"

    # ExportHelper mixin class uses this
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
        return write_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="Text Export Operator")


def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')