import bpy
import bmesh
from bpy.props import PointerProperty, IntProperty, FloatProperty
from bpy.types import Operator, PropertyGroup
from functools import reduce

import numpy as np
import random


import sys
from math import *
from mathutils import *


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
        col.prop(sea_sponge_props, 'rotundness')
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
        col.prop(sea_sponge_props, 'resolution')
        row = layout.row()
        row.operator('sea.gen_sea_sponge', text='Generate')


class SeaSpongeProperties(PropertyGroup):
    min_radius: FloatProperty(
        name='Min Radius',
        description='Minimum range of radius from Z',
        default=0.5,
        min=0.0,
        max=10.0
    )
    max_radius: FloatProperty(
        name='Max Radius',
        description='Maximum range of radius from Z',
        default=0.1,
        min=0.0,
        max=10.0
    )
    rotundness: FloatProperty(
        name='Rotundness',
        description='Degree of radial rotundness',
        default=0.5,
        min=0.25,
        max=0.75
    )
    min_height: FloatProperty(
        name='Min Height',
        description='Minimum range of sponge length',
        default=1.0,
        min=0.1,
        max=10.0
    )
    max_height: FloatProperty(
        name='Max Height',
        description='Maximum range of sponge length',
        default=2.0,
        min=0.1,
        max=10.0
    )
    x_rot: IntProperty(
        name='X Rotation Range',
        description='Degree of rotation around x axis',
        default=45,
        min=0,
        max=90
    )
    y_rot: IntProperty(
        name='Y Rotation Range',
        description='Degree of rotation around y axis',
        default=45,
        min=0,
        max=90
    )
    z_rot: IntProperty(
        name='Z Rotation Range',
        description='Degree of rotation around z axis',
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
        description='Minimum degree of bump',
        default=5.0,
        min=0.0,
        max=100.0
    )
    bump_max: FloatProperty(
        name='Bump Max',
        description='Maximum degree of bump',
        default=7.0,
        min=0.0,
        max=100.0
    )
    turbulence_octaves: IntProperty(
        name='Turbulence Octaves',
        description='Number of turbulence octaves',
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
    resolution: IntProperty(
        name='Resolution',
        description='Number of subdivisions in generating faces/vertices',
        default=20,
        min=10,
        max=50
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
            angle = (pi*2) * i / segments
            verts.append((cos(angle) * radius, sin(angle) * radius, z * radius))

        return verts
    
    
    def make_cylinder(self, segments=64, rows=100):
        """" Make a plain cylinder """
        
        data = { 'verts': [], 'edges': [], 'faces': [] }
        rows = random.randrange(self.sea_sponge_props.min_height, self.sea_sponge_props.max_height)
        for z in range(rows):
            data['verts'].extend(self.vertex_circle(segments, z/10))

        for i in range(segments):
            for row in range(0, rows - 1):
                data['faces'].append(self.face(segments, i, row))
                
        return data
    
    
    def make_rotund_cylinder(self):
        """ Make a rotund cylinder """
        
        inner_r = self.sea_sponge_props.radius
        outer_r = self.sea_sponge_props.rotundness
        length = random.randrange(self.sea_sponge_props.min_height, self.sea_sponge_props.max_height)
        res = self.sea_sponge_props.resolution
        
        range_u_min = -pi
        range_u_max = pi
        range_u_step = res
        wrap_u = True
        
        range_v_min = -pi/2
        range_v_max = pi/2
        range_v_step = 4 * res
        wrap_v = False
        
        z_shift = log(3*range_v_max)*length*range_v_max
        
        x_eq = "{}*cos({}*v)*cos(u)".format(inner_r, outer_r)
        y_eq = "{}*cos({}*v)*sin(u)".format(inner_r, outer_r)
        z_eq = "{0}*v*log((-v)+({1}))+{2}".format(length, 2*range_v_max, z_shift)

        a_eq = b_eq = c_eq = d_eq = e_eq = f_eq = g_eq = h_eq = "0"
        n=1
        close_v = False
        
        xyz_surface = xyz_function_surface_faces(x_eq, y_eq, z_eq,
            range_u_min, range_u_max, range_u_step, wrap_u,
            range_v_min, range_v_max, range_v_step, wrap_v,
            a_eq, b_eq, c_eq, f_eq, g_eq, h_eq, n, close_v)
        data = { 'verts': xyz_surface[0], 'edges': [], 'faces': xyz_surface[1] }
        
        return data
    
    
    def make_sponge(self, name):
        """ Make a sponge """

        data = self.make_rotund_cylinder()
        
        bump_reducer = random.uniform(self.sea_sponge_props.bump_min, self.sea_sponge_props.bump_max)
        for index, vert in enumerate(data["verts"]):

            vector_vert = Vector(vert)
#            perlin_noise = noise.noise_vector(vector_vert)
#            data["verts"][index] = (vert[0] + perlin_noise.x/bump_reducer, vert[1] + perlin_noise.y/bump_reducer, vert[2] + perlin_noise.z/bump_reducer)
            turbulence = noise.turbulence_vector(vector_vert, self.sea_sponge_props.turbulence_octaves, True)
            new_x = vert[0] + turbulence.x / bump_reducer
            new_y = vert[1] + turbulence.y / bump_reducer
            new_z = vert[2] + turbulence.z / bump_reducer
            new_point = Vector((new_x, new_y, new_z))
            data["verts"][index] = (new_x, new_y, new_z)
                
        scene = bpy.context.scene
        obj = object_from_data(data, name, scene)
        
        return obj

    def rotate(self, obj):
        obj.rotation_euler[0] = radians(random.randrange(-self.sea_sponge_props.x_rot, self.sea_sponge_props.x_rot))
        obj.rotation_euler[1] = radians(random.randrange(-self.sea_sponge_props.y_rot, self.sea_sponge_props.y_rot))
        obj.rotation_euler[2] = radians(random.randrange(self.sea_sponge_props.z_rot))
        
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
            avg_vert = Vector(avg_vert)
            
            dist_to_z = round(get_dist_from_z_axis(avg_vert), 2) / self.sea_sponge_props.radius
#            print(dist_to_z)
#        print(self.sea_sponge_props.radius)
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
            obj = self.make_sponge(f"sponge_{x}")
            
            self.rotate(obj)
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
    return sqrt((point.x ** 2) + (point.y ** 2))


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


# List of safe functions for eval()
safe_list = ['math', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
    'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot',
    'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians',
    'sin', 'sinh', 'sqrt', 'tan', 'tanh']

# Use the list to filter the local namespace
safe_dict = dict((k, globals().get(k, None)) for k in safe_list)

def xyz_function_surface_faces(x_eq, y_eq, z_eq,
    range_u_min, range_u_max, range_u_step, wrap_u,
    range_v_min, range_v_max, range_v_step, wrap_v,
    a_eq, b_eq, c_eq, f_eq, g_eq, h_eq, n, close_v):
    """ Generate parametrized XYZ surface from built-in Blender extension:
        https://archive.blender.org/wiki/index.php/Extensions:2.6/Py/Scripts/Add_Mesh/Add_3d_Function_Surface/
        Returns pair of vertices and faces
    """

    verts = []
    faces = []

    # Distance of each step in Blender Units
    uStep = (range_u_max - range_u_min) / range_u_step
    vStep = (range_v_max - range_v_min) / range_v_step

    # Number of steps in the vertex creation loops.
    # Number of steps is the number of faces
    #   => Number of points is +1 unless wrapped.
    uRange = range_u_step + 1
    vRange = range_v_step + 1

    if wrap_u:
        uRange = uRange - 1

    if wrap_v:
        vRange = vRange - 1
    
    try:
        expr_args_x = (
            compile(x_eq, __file__.replace(".py", "_x.py"), 'eval'),
            {"__builtins__": None},
            safe_dict)
        expr_args_y = (
            compile(y_eq, __file__.replace(".py", "_y.py"), 'eval'),
            {"__builtins__": None},
            safe_dict)
        expr_args_z = (
            compile(z_eq, __file__.replace(".py", "_z.py"), 'eval'),
            {"__builtins__": None},
            safe_dict)
        expr_args_a = (
            compile(a_eq, __file__.replace(".py", "_a.py"), 'eval'),
            {"__builtins__": None},
            safe_dict)
        expr_args_b = (
            compile(b_eq, __file__.replace(".py", "_b.py"), 'eval'),
            {"__builtins__": None},
            safe_dict)
        expr_args_c = (
            compile(c_eq, __file__.replace(".py", "_c.py"), 'eval'),
            {"__builtins__": None},
            safe_dict)
        expr_args_f = (
            compile(f_eq, __file__.replace(".py", "_f.py"), 'eval'),
            {"__builtins__": None},
            safe_dict)
        expr_args_g = (
            compile(g_eq, __file__.replace(".py", "_g.py"), 'eval'),
            {"__builtins__": None},
            safe_dict)
        expr_args_h = (
            compile(h_eq, __file__.replace(".py", "_h.py"), 'eval'),
            {"__builtins__": None},
            safe_dict)
    except:
        import traceback
        print("Error parsing expression: "
            + traceback.format_exc(limit=1))
        return [], []
    
    for vN in range(vRange):
        v = range_v_min + (vN * vStep)

        for uN in range(uRange):
            u = range_u_min + (uN * uStep)

            safe_dict['u'] = u
            safe_dict['v'] = v

            safe_dict['n'] = n

            # Try to evaluate the equations.
            try:
                a = float(eval(*expr_args_a))
                b = float(eval(*expr_args_b))
                c = float(eval(*expr_args_c))

                safe_dict['a'] = a
                safe_dict['b'] = b
                safe_dict['c'] = c

                f = float(eval(*expr_args_f))
                g = float(eval(*expr_args_g))
                h = float(eval(*expr_args_h))

                safe_dict['f'] = f
                safe_dict['g'] = g
                safe_dict['h'] = h

                verts.append((
                    float(eval(*expr_args_x)),
                    float(eval(*expr_args_y)),
                    float(eval(*expr_args_z))))

            except:
                import traceback
                print("Error evaluating expression: "
                    + traceback.format_exc(limit=1))
                return [], []
    
    for vN in range(range_v_step):
        vNext = vN + 1

        if wrap_v and (vNext >= vRange):
            vNext = 0

        for uN in range(range_u_step):
            uNext = uN + 1

            if wrap_u and (uNext >= uRange):
                uNext = 0

            faces.append([(vNext * uRange) + uNext,
                (vNext * uRange) + uN,
                (vN * uRange) + uN,
                (vN * uRange) + uNext])

    if close_v and wrap_u and (not wrap_v):
        for uN in range(1, range_u_step - 1):
            faces.append([
                range_u_step - 1,
                range_u_step - 1 - uN,
                range_u_step - 2 - uN])
            faces.append([
                range_v_step * uRange,
                range_v_step * uRange + uN,
                range_v_step * uRange + uN + 1])

    return verts, faces


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