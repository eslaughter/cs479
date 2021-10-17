import bpy
import bmesh
from bpy.props import PointerProperty, IntProperty, FloatProperty
from bpy.types import Operator, PropertyGroup
from functools import reduce

import numpy as np
import random


# TEst testing 123

import sys
import math
import mathutils
#from mathutils import noise

class SeaSpongePanel(bpy.types.Panel):
    bl_label = "Sea Sponge Panel"
    bl_idname = "OBJECT_PT_sea_sponge_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sea Sponge"
    
    def draw(self, context):
        layout = self.layout
        sea_sponge_props = context.scene.sea_sponge_properties
        
        row = layout.row()
        col = layout.column(align=True)
        col.prop(sea_sponge_props, 'min_radius')
        col.prop(sea_sponge_props, 'max_radius')
        row = layout.row()
        col.prop(sea_sponge_props, 'min_height')
        col.prop(sea_sponge_props, 'max_height')
        col.prop(sea_sponge_props, 'x_rot')
        col.prop(sea_sponge_props, 'y_rot')
        col.prop(sea_sponge_props, 'z_rot')
        col.prop(sea_sponge_props, 'bump_min')
        col.prop(sea_sponge_props, 'bump_max')
        col.prop(sea_sponge_props, 'turbulence_octaves')
        col.prop(sea_sponge_props, 'num_sponges')

        
        
        row = layout.row()
        row.operator('sea.gen_sea_sponge', text='Generate')

class SeaSpongeProperties(PropertyGroup):
    min_radius: FloatProperty(
        name='Min Radius',
        description='Number of sponges you want',
        default=0.5,
        min=0.0,
        max=10.0
    )
    max_radius: FloatProperty(
        name='Max Radius',
        description='Number of sponges you want',
        default=0.1,
        min=0.0,
        max=10.0
    )
    min_height: IntProperty(
        name='Min Height',
        description='Number of sponges you want',
        default=10,
        min=0,
        max=1000
    )
    max_height: IntProperty(
        name='Max Height',
        description='Number of sponges you want',
        default=20,
        min=0,
        max=1000
    )
    x_rot: IntProperty(
        name='X Rotation Range',
        description='Number of sponges you want',
        default=45,
        min=0,
        max=90
    )
    y_rot: IntProperty(
        name='Y Rotation Range',
        description='Number of sponges you want',
        default=45,
        min=0,
        max=90
    )
    z_rot: IntProperty(
        name='Z Rotation Range',
        description='Number of sponges you want',
        default=360,
        min=0,
        max=360
    )
    
    num_sponges: IntProperty(
        name='Number of Sponges',
        description='Number of sponges you want',
        default=20,
        min=0,
        max=1000
    )
    bump_min: FloatProperty(
        name='Bump Min',
        description='Number of sponges you want',
        default=5.0,
        min=0.0,
        max=100.0
    )
    bump_max: FloatProperty(
        name='Bump Max',
        description='Number of sponges you want',
        default=7.0,
        min=0.0,
        max=100.0
    )
    turbulence_octaves: IntProperty(
        name='Turbulence Octaves',
        description='Number of sponges you want',
        default=7,
        min=0,
        max=100
    )
    radius: FloatProperty(
        name='Radius',
        description='Number of sponges you want',
        default=0.1,
        min=0.0,
        max=10.0
    )

class GenSeaSponge(Operator):
    bl_idname = 'sea.gen_sea_sponge'
    bl_label = 'Generate Sea Sponge'
    bl_options = {'REGISTER', "UNDO"}

    def face(self, segments, i, row):
        """ Return a face on a cylinder """

        if i == segments - 1:
            ring_start = segments * row
            base = segments * (row + 1)

            return (base - 1, ring_start, base, (base + segments) - 1)
        else:
            base = (segments * row) + i
            return (base, base + 1, base + segments + 1, base + segments)

    def vertex_circle(self, segments, z):
        """ Return a ring of vertices """
        verts = []
        radius = self.sea_sponge_props.radius

        for i in range(segments):
            angle = (math.pi*2) * i / segments
            verts.append((math.cos(angle) * radius, math.sin(angle) * radius, z * radius))

        return verts
    
    
    def make_cylinder(self, name, segments=64, rows=100):
        """ Make a cylinder """

        data = { 'verts': [], 'edges': [], 'faces': [] }
        rows = random.randrange(self.sea_sponge_props.min_height, self.sea_sponge_props.max_height)
        for z in range(rows):
            data['verts'].extend(self.vertex_circle(segments, z/10))

        
        
        for i in range(segments):
            for row in range(0, rows - 1):
                data['faces'].append(self.face(segments, i, row))
        
        bump_reducer = random.uniform(self.sea_sponge_props.bump_min, self.sea_sponge_props.bump_max)
        for index, vert in enumerate(data["verts"]):
            vector_vert = mathutils.Vector(vert)
            
#            perlin_noise = mathutils.noise.noise_vector(vector_vert)
            turbulence = mathutils.noise.turbulence_vector(vector_vert, self.sea_sponge_props.turbulence_octaves, True)
            
            new_x = vert[0] + turbulence.x / bump_reducer
            new_y = vert[1] + turbulence.y / bump_reducer
            new_z = vert[2] + turbulence.z / bump_reducer
            new_point = mathutils.Vector((new_x, new_y, new_z))
            
            data["verts"][index] = (new_x, new_y, new_z)
                
        scene = bpy.context.scene
        obj = object_from_data(data, name, scene)
        
        return obj

    def rotate(self, obj):
        obj.rotation_euler[0] = math.radians(random.randrange(-self.sea_sponge_props.x_rot, self.sea_sponge_props.x_rot))
        obj.rotation_euler[1] = math.radians(random.randrange(-self.sea_sponge_props.y_rot, self.sea_sponge_props.y_rot))
        obj.rotation_euler[2] = math.radians(random.randrange(self.sea_sponge_props.z_rot))
        
    def color_faces(self, obj):
        mesh = bpy.context.object.data
        face_color_dict = {}
        for index, face in enumerate(obj.data.polygons):
            green = bpy.data.materials.new(f"color_{index}")
            
            avg_vert = [0, 0, 0]
            for vert in face.vertices:
                avg_vert[0] += obj.data.vertices[vert].co.x
                avg_vert[1] += obj.data.vertices[vert].co.y
                avg_vert[2] += obj.data.vertices[vert].co.z
            
            avg_vert[0] /= len(face.vertices)
            avg_vert[1] /= len(face.vertices)
            avg_vert[2] /= len(face.vertices)
            avg_vert = mathutils.Vector(avg_vert)
            
            dist_to_z = round(get_dist_from_z_axis(avg_vert), 2) / self.sea_sponge_props.radius
            print(dist_to_z)
        print(self.sea_sponge_props.radius)
    #        green.diffuse_color = (0.0, dist_to_z, 0.0, 1)
    #    
    #        mesh.materials.append(green)
    #        face_color_dict[dist_to_z]

            
    #    bm = bmesh.new()
    #    bm.from_mesh(mesh)
    #    for face in bm.faces:
    ##        for vert in face.verts:
    ##            print(vert.co)
    ##        print(face.verts)
    #        face.material_index = fa
    #    bm.to_mesh(mesh)

    def execute(self, context):
        self.sea_sponge_props = context.scene.sea_sponge_properties
        objs = []
        for x in range(self.sea_sponge_props.num_sponges):
            self.sea_sponge_props.radius = random.uniform(self.sea_sponge_props.min_radius, self.sea_sponge_props.max_radius)
            obj = self.make_cylinder(f"sponge_{x}")
            
            
#            self.rotate(obj)
            self.color_faces(obj)
            objs.append(obj)

        
        scene = bpy.context.scene


        # Connect all sponges into one object
        ctx = bpy.context.copy()
        ctx['active_object'] = objs[0]
        ctx['selected_editable_objects'] = objs
        bpy.ops.object.join(ctx)
                
        return {'FINISHED'}





# ------------------------------------------------------------------------------
# Utility Functions

def get_dist_from_z_axis(point):
    return math.sqrt((point.x ** 2) + (point.y ** 2))

def set_smooth(obj):
    """ Enable smooth shading on an mesh object """

    for face in obj.data.polygons:
        face.use_smooth = True


def object_from_data(data, name, scene, select=True):
    """ Create a mesh object and link it to a scene """

    mesh = bpy.data.meshes.new(name)
    

    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.color = (random.random(), random.random(), random.random(), 1)


    mesh.from_pydata(data['verts'], data['edges'], data['faces'])
    mesh.validate(verbose=True)
    
    mesh.update()

    return obj


# ------------------------------------------------------------------------------


CLASSES = [GenSeaSponge, SeaSpongeProperties]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.sea_sponge_properties = PointerProperty(type=SeaSpongeProperties)
    bpy.utils.register_class(SeaSpongePanel)
   
    
    
def unregister():
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.sea_sponge_properties
    bpy.utils.unregister_class(SeaSpongePanel)
    
    
if __name__ == "__main__":
    register()