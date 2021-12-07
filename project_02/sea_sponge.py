import bpy
import bmesh
from bpy.props import PointerProperty, IntProperty, FloatProperty, EnumProperty
from bpy.types import Operator, PropertyGroup
from functools import reduce

import numpy as np
import random

import sys
from math import *
from mathutils import *


# ------------------------------------------------------------------------------
# Sea Sponge Plugin Panel


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
        col.label(text='Geometry:')
        col.prop(sea_sponge_props, 'num_sponges')
        col.prop(sea_sponge_props, 'min_radius')
        col.prop(sea_sponge_props, 'max_radius')
        col.prop(sea_sponge_props, 'rotundness')
        row = layout.row()
        col.prop(sea_sponge_props, 'min_height')
        col.prop(sea_sponge_props, 'max_height')
        col.prop(sea_sponge_props, 'x_rot')
        col.prop(sea_sponge_props, 'y_rot')
        col.prop(sea_sponge_props, 'z_rot')
        col.prop(sea_sponge_props, 'resolution')
        col.label(text='Texturing:')
        col.prop(sea_sponge_props, 'texturing_scheme')
        if sea_sponge_props.texturing_scheme == 'PERLIN' or sea_sponge_props.texturing_scheme == 'TURBULENCE':
            col.prop(sea_sponge_props, 'bump_scale')
        if sea_sponge_props.texturing_scheme == 'TURBULENCE':
            col.prop(sea_sponge_props, 'turbulence_octaves')
        col.label(text='Custom Shading:')
        col.prop(sea_sponge_props, 'shading_scheme')
        if 'CUSTOM' in sea_sponge_props.shading_scheme:
            col.prop(sea_sponge_props, 'red_channel')
            col.prop(sea_sponge_props, 'green_channel')
            col.prop(sea_sponge_props, 'blue_channel')
        row = layout.row()
        row.operator('sea.gen_sea_sponge', text='Generate')


class SeaSpongeProperties(PropertyGroup):
    min_radius: FloatProperty(
        name='Minimum Radius',
        description='Minimum range of radius from Z',
        default=0.5,
        min=0.0,
        max=10.0
    )
    max_radius: FloatProperty(
        name='Maximum Radius',
        description='Maximum range of radius from Z',
        default=0.1,
        min=0.0,
        max=10.0
    )
    rotundness: FloatProperty(
        name='Radial Rotundness',
        description='Degree of radial rotundness',
        default=0.5,
        min=0.25,
        max=0.75
    )
    min_height: FloatProperty(
        name='Minimum Height',
        description='Minimum range of sponge length',
        default=1.0,
        min=0.1,
        max=10.0
    )
    max_height: FloatProperty(
        name='Maximum Height',
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
        description='Number of sponges to generate',
        default=20,
        min=0,
        max=1000
    )
    shading_scheme: EnumProperty(
        name='Shading Scheme',
        description='Presets for shading schemes',
        items=[
            ('CUSTOM_MATTE', 'Custom Matte', 'Custom color without depth'),
            ('CUSTOM_DEPTH', 'Custom Depth', 'Custom color with depth'),
            ('RUGRATS', 'Rugrats', '90s-style and color scheme')
        ],
        default='RUGRATS'
    )
    texturing_scheme: EnumProperty(
        name='Texturing Scheme',
        description='Method for generating texture',
        items=[
            ('NONE', 'Smooth', 'Generate a smooth surface'),
            ('PERLIN', 'Perlin Noise', 'Use noise to generate bumpiness'),
            ('TURBULENCE', 'Turbulence', 'Use turbulence to generate bumpiness')
            
        ],
        default='TURBULENCE'
    )
    bump_scale: IntProperty(
        name='Bump Scale',
        description='Scale of bumpiness 1-10',
        default=10,
        min=1,
        max=10
    )
    turbulence_octaves: IntProperty(
        name='Bump Frequency',
        description='Number of turbulence octaves',
        default=7,
        min=0,
        max=100
    )
    red_channel: FloatProperty(
        name='Amount of Red 0-1',
        description='Amount of red 0-1',
        default=0.8,
        min=0.0,
        max=1.0
    )
    green_channel: FloatProperty(
        name='Amount of Green 0-1',
        description='Amount of green 0-1',
        default=0.8,
        min=0.0,
        max=1.0
    )
    blue_channel: FloatProperty(
        name='Amount of Blue 0-1',
        description='Amount of blue 0-1',
        default=0.8,
        min=0.0,
        max=1.0
    )
    resolution: IntProperty(
        name='Resolution',
        description='Number of subdivisions in generating faces/vertices',
        default=20,
        min=10,
        max=1000
    )
    radius: FloatProperty(
        name='Radius',
        description='Store radius',
        default=0.1,
        min=0.0,
        max=10.0
    )
    max_z: FloatProperty(
        name='maximum z',
        description='Store maximum z',
        default=0.1,
        min=0.0,
        max=100000.0
    )


# ------------------------------------------------------------------------------
# Sea Sponge Generator Class


class GenSeaSponge(Operator):
    bl_idname = 'sea.gen_sea_sponge'
    bl_label = 'Generate Sea Sponge'
    bl_options = {'REGISTER', "UNDO"}    
    
    def make_rotund_cylinder(self):
        """ Make a rotund cylinder """
        
        inner_r = self.sea_sponge_props.radius
        outer_r = self.sea_sponge_props.rotundness
        length = random.uniform(self.sea_sponge_props.min_height, self.sea_sponge_props.max_height)
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
        texturing_scheme = self.sea_sponge_props.texturing_scheme
        
        bump_reducer = 1.0 if texturing_scheme == 'SMOOTH' else get_bump_reducer(self.sea_sponge_props.bump_scale)

        for index, vert in enumerate(data["verts"]):
            # Construct mathutils.Vector
            vector_vert = Vector(vert)
            # Find bump factor based on texturing scheme
            bump = None
            if texturing_scheme == 'PERLIN':
                bump = noise.noise_vector(vector_vert)
            elif texturing_scheme == 'TURBULENCE':
                bump = noise.turbulence_vector(vector_vert, self.sea_sponge_props.turbulence_octaves, False)
            else:
                bump = Vector((1.0, 1.0))
            # Apply the bump factor and reducer
            new_x = vert[0] + bump.x / bump_reducer
            new_y = vert[1] + bump.y / bump_reducer
            data["verts"][index] = (new_x, new_y, vert[2])
                
        scene = bpy.context.scene
        obj = object_from_data(data, name, scene)
        
        return obj
    

    def rotate(self, obj):
        obj.rotation_euler[0] = radians(random.randrange(-self.sea_sponge_props.x_rot, self.sea_sponge_props.x_rot))
        obj.rotation_euler[1] = radians(random.randrange(-self.sea_sponge_props.y_rot, self.sea_sponge_props.y_rot))
        obj.rotation_euler[2] = radians(random.randrange(self.sea_sponge_props.z_rot))
        
        
    def color_faces_matte(self, obj):
        mesh = bpy.context.object.data
        
        r = self.sea_sponge_props.red_channel
        g = self.sea_sponge_props.green_channel
        b = self.sea_sponge_props.blue_channel
        
        color = bpy.data.materials.new(f"color")
        color.diffuse_color = (r, g, b, 1)
        mesh.materials.append(color)
        print(mesh.materials[0])
            
        # Create the mesh
        # Adapted from this video https://www.youtube.com/watch?v=Mwap1W-6o7k&t=329s
        bm = bmesh.new()
        bm.from_mesh(mesh)
        for bm_face in bm.faces:
            bm_face.material_index = 0
        bm.to_mesh(mesh)
        
        
    def get_color_from_dist(self, dist, z):
        if self.sea_sponge_props.shading_scheme == 'CUSTOM_DEPTH':
            red_scalar = 1-((1-self.sea_sponge_props.red_channel) * (1-dist))
            green_scalar = 1-((1-self.sea_sponge_props.green_channel) * (1-dist))
            blue_scalar = 1-((1-self.sea_sponge_props.blue_channel) * (1-dist))
        elif self.sea_sponge_props.shading_scheme == 'RUGRATS':
            if dist > 0.75:
                red_scalar = dist / 5
                green_scalar = 1.0
                blue_scalar = dist / 5
            elif dist < 0.25:
                red_scalar = 1.0
                green_scalar = dist / 5
                blue_scalar = dist / 5
            else:
                red_scalar = dist / 5
                green_scalar = dist / 5
                blue_scalar = 1.0
        return (red_scalar, green_scalar, blue_scalar, 1)
        
        
    def color_faces_by_dist(self, obj):
        mesh = bpy.context.object.data
        
        max_z = 0
        grouped_by_z = {}
        # Construct dictionary of faces' average vertices, keyed on z-value
        for index, face in enumerate(obj.data.polygons):
            avg_vert = find_face_mean_vert(obj, face, False)
            # Save maximum z seen
            if avg_vert.z > max_z:
                max_z = avg_vert.z
            if avg_vert.z in grouped_by_z:
                grouped_by_z[avg_vert.z].append(avg_vert)
            else:
                grouped_by_z[avg_vert.z] = [avg_vert]
        self.sea_sponge_props.max_z = max_z
        
        # Construct dictionary of local centers of vertices at each z level, keyed on z-value
        z_centers = {}
        for z in grouped_by_z:
            n = len(grouped_by_z[z])
            center = Vector((0, 0, 0))
            for vert in grouped_by_z[z]:
                center = center + vert
            center = Vector((center.x / n, center.y / n, center.z /n))
            z_centers[z] = center
            
        # Construct dictionary of min and max distances from centers at each z level, keyed on z-value
        z_center_dist_max_mins = {}
        for z in grouped_by_z:
            max_dist = 0
            min_dist = 1000000
            for vert in grouped_by_z[z]:
                dist = get_distance_from_center(vert, z_centers[z])
                if dist > max_dist:
                    max_dist = dist
                if dist < min_dist:
                    min_dist = dist
            z_center_dist_max_mins[z] = (min_dist, max_dist)
            
        # Construct a dictionary of colors, keyed on distance from relative center
        face_color_dict = {}
        mat_count = 0
        for index, face in enumerate(obj.data.polygons):
            avg_vert = find_face_mean_vert(obj, face, False)
            dist_to_center = get_distance_from_center(avg_vert, z_centers[avg_vert.z])
            mapped_dist = round(map_range(dist_to_center, z_center_dist_max_mins[avg_vert.z][0], z_center_dist_max_mins[avg_vert.z][1], 0, 1.0), 2)
            
            if mapped_dist not in face_color_dict:
                color = bpy.data.materials.new(f"color_{index}")
                color.diffuse_color = self.get_color_from_dist(mapped_dist, avg_vert.z)
                mesh.materials.append(color)
                face_color_dict[mapped_dist] = mat_count
                mat_count += 1

        # Create the mesh
        # Adapted from this video https://www.youtube.com/watch?v=Mwap1W-6o7k&t=329s
        bm = bmesh.new()
        bm.from_mesh(mesh)
        for bm_face in bm.faces:
            avg_vert = find_face_mean_vert(obj, bm_face, True)
            dist_to_center =  get_distance_from_center(avg_vert, z_centers[avg_vert.z])
            bm_mapped_dist = round(map_range(dist_to_center, z_center_dist_max_mins[avg_vert.z][0], z_center_dist_max_mins[avg_vert.z][1], 0, 1.0), 2)
            bm_face.material_index = face_color_dict[bm_mapped_dist]
        bm.to_mesh(mesh)


    def color_faces(self, obj):
        shading_scheme = self.sea_sponge_props.shading_scheme
        if shading_scheme == 'CUSTOM_MATTE':
            self.color_faces_matte(obj)
        else:
            self.color_faces_by_dist(obj)


    def execute(self, context):
        self.sea_sponge_props = context.scene.sea_sponge_properties
        objs = []
        for x in range(self.sea_sponge_props.num_sponges):
            self.sea_sponge_props.radius = random.uniform(self.sea_sponge_props.min_radius, self.sea_sponge_props.max_radius)
            obj = self.make_sponge(f"sponge_{x}")
            self.color_faces(obj)
            self.rotate(obj)
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

def get_bump_reducer(n):
    min = (10-n)*10+5
    max = (10-n)*10+15
    return random.uniform(min, max)

# Adapted from this code https://stackoverflow.com/questions/4154969/how-to-map-numbers-in-range-099-to-range-1-01-0/33127793
def map_range(value, original_range_min, original_range_max, new_range_min, new_range_max):
    return ((value - original_range_min) / (original_range_max - original_range_min)) * (new_range_max-new_range_min) + new_range_min


def get_dist_from_z_axis(point):
    return sqrt((point.x ** 2) + (point.y ** 2))


def get_distance_from_center(vert, center):
    return sqrt(((center.x - vert.x) ** 2) + ((center.y - vert.y) ** 2))


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
    avg_vert = Vector(avg_vert)
    return avg_vert


def object_from_data(data, name, scene, select=True):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj


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
