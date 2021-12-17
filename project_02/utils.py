import bpy
import random
from math import *
from mathutils import *
    
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