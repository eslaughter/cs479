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
        col.prop(sea_sponge_props, 'red_channel')
        col.prop(sea_sponge_props, 'green_channel')
        col.prop(sea_sponge_props, 'blue_channel')
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
    red_channel: FloatProperty(
        name='Amount of red 0-1',
        description='Number of sponges you want',
        default=0.8,
        min=0.0,
        max=1.0
    )
    green_channel: FloatProperty(
        name='Amount of green 0-1',
        description='Number of sponges you want',
        default=0.8,
        min=0.0,
        max=1.0
    )
    blue_channel: FloatProperty(
        name='Amount of blue 0-1',
        description='Number of sponges you want',
        default=0.8,
        min=0.0,
        max=1.0
    )
    radius: FloatProperty(
        name='Radius',
        description='Number of sponges you want',
        default=0.1,
        min=0.0,
        max=10.0
    )
    dist_to_z_axis: FloatProperty(
        name='Distance to z-axis',
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
        
        
        
        self.sea_sponge_props.dist_to_z_axis = get_dist_from_z_axis(mathutils.Vector(data["verts"][0]))
        return obj

    def rotate(self, obj):
        obj.rotation_euler[0] = math.radians(random.randrange(-self.sea_sponge_props.x_rot, self.sea_sponge_props.x_rot))
        obj.rotation_euler[1] = math.radians(random.randrange(-self.sea_sponge_props.y_rot, self.sea_sponge_props.y_rot))
        obj.rotation_euler[2] = math.radians(random.randrange(self.sea_sponge_props.z_rot))
        
        
    def get_color_from_dist(self, dist):
        if dist > 0.75:
            red_scaler = self.sea_sponge_props.red_channel
            green_scaler = self.sea_sponge_props.green_channel
            blue_scaler = self.sea_sponge_props.blue_channel
        elif dist < 0.25:
            red_scaler = dist / 5
            green_scaler = self.sea_sponge_props.green_channel
            blue_scaler = self.sea_sponge_props.blue_channel
        else:
            red_scaler = dist / 5
            green_scaler = self.sea_sponge_props.blue_channel
            blue_scaler = dist /5
            
#        green_scaler = 1 - green_scaler * dist
        
        return (red_scaler, green_scaler, blue_scaler, 1)
        
    def color_faces(self, obj):
        mesh = bpy.context.object.data
        max_dist = 0
        min_dist = 1000000
        for index, face in enumerate(obj.data.polygons):
            avg_vert = find_face_mean_vert(obj, face, False)
            dist_to_z = get_dist_from_z_axis(avg_vert)
            if dist_to_z > max_dist:
                max_dist = dist_to_z
            elif dist_to_z < min_dist:
                min_dist = dist_to_z
        
        print(max_dist)
        print(min_dist)
        face_color_dict = {}
        mat_count = 0
        
        
        for face in obj.data.polygons:
            
            avg_vert = find_face_mean_vert(obj, face, False)
            dist_to_z = get_dist_from_z_axis(avg_vert)
            mapped_dist = round(map_range(dist_to_z, min_dist, max_dist, 0, 1.0), 2)
            
            if mapped_dist not in face_color_dict:
                green = bpy.data.materials.new(f"color_{index}")
                green.diffuse_color = self.get_color_from_dist(mapped_dist)
                mesh.materials.append(green)
                face_color_dict[mapped_dist] = mat_count
                mat_count += 1
            
        bm = bmesh.new()
        bm.from_mesh(mesh)
        for bm_face in bm.faces:
            avg_vert = find_face_mean_vert(obj, bm_face, True)
            dist_to_z_axis = get_dist_from_z_axis(avg_vert)
            bm_mapped_dist = round(map_range(dist_to_z_axis, min_dist, max_dist, 0, 1.0), 2)
            bm_face.material_index = face_color_dict[bm_mapped_dist]
        bm.to_mesh(mesh)

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


def map_range(value, original_range_min, original_range_max, new_range_min, new_range_max):
    return ((value - original_range_min) / (original_range_max - original_range_min)) * (new_range_max-new_range_min) + new_range_min

def get_dist_from_z_axis(point):
    return math.sqrt((point.x ** 2) + (point.y ** 2))

def find_face_mean_vert(obj, face, is_bm):
    avg_vert = [0, 0, 0]
    if not is_bm:
        for vert in face.vertices:
            avg_vert[0] += obj.data.vertices[vert].co.x
            avg_vert[1] += obj.data.vertices[vert].co.y
            avg_vert[2] += obj.data.vertices[vert].co.z
                
        avg_vert[0] /= len(face.vertices)
        avg_vert[1] /= len(face.vertices)
        avg_vert[2] /= len(face.vertices)
    else:
        for vert in face.verts:
            avg_vert[0] += vert.co.x
            avg_vert[1] += vert.co.y
            avg_vert[2] += vert.co.z
                
        avg_vert[0] /= len(face.verts)
        avg_vert[1] /= len(face.verts)
        avg_vert[2] /= len(face.verts)
    avg_vert = mathutils.Vector(avg_vert)
    return avg_vert


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