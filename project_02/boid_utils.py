import bpy
import mathutils
import math

def generate_cylinder(point1, point2, r):
    dx = point2.x - point1.x
    dy = point2.y - point1.y
    dz = point2.z - point1.z    
    dist = math.sqrt(dx**2 + dy**2 + dz**2)

    bpy.ops.mesh.primitive_cylinder_add(
        radius = r, 
        depth = dist,
        location = (dx/2 + point1.x, dy/2 + point1.y, dz/2 + point1.z)   
    ) 

    phi = math.atan2(dy, dx) 
    theta = math.acos(dz/dist) 

    bpy.context.object.rotation_euler[1] = theta
    bpy.context.object.rotation_euler[2] = phi
    return bpy.context.object, bpy.ops.object

def generate_boid_cone(mat, loc, vel):
    bpy.ops.mesh.primitive_cone_add(radius1=0.025, depth=0.1)
    cone = bpy.context.object
    cone.location = loc
    
    cone.data.materials.append(mat)
    
    return cone

def gen_region_cube(x_scale, y_scale, z_scale):
    bpy.ops.mesh.primitive_cube_add(scale=(x_scale, y_scale, z_scale), align='WORLD', location=(0.0, 0.0, 0.0))
    obj = bpy.context.object
    if "transparent" in bpy.data.materials:
        mat = bpy.data.materials["transparent"]
    else:
        mat = bpy.data.materials.new("transparent")
    mat.diffuse_color = (1, 1, 1, 0.05)
    mat.blend_method = 'OPAQUE'
    obj.data.materials.append(mat)
    obj.show_transparent = True 
    obj.name = "REGION_CUBE"
    return obj

def clear_scene():
    for object in bpy.data.objects:
        bpy.data.objects.remove(object, do_unlink=True)

def angle_between_vectors(vector1, vector2):
    term1 = vector1.x * vector2.x + vector1.y * vector2.y + vector1.z * vector2.z
    term2 = math.sqrt((vector1.x ** 2) + (vector1.y ** 2) + (vector1.z ** 2))
    term3 = math.sqrt((vector2.x ** 2) + (vector2.y ** 2) + (vector2.z ** 2))
    return math.acos(term1 / (term2 * term3))

def dist(point1: mathutils.Vector, point2: mathutils.Vector) -> float:
    """Calculate distance between two points in 3D."""
    return (point2 - point1).length

def set_mag(vector, mag):
    if vector.length == 0:
        return mathutils.Vector((0, 0, 0))
    return vector * (mag / vector.length) 

def limit(vector, mag):
    
    if vector.length > mag:
        vector = set_mag(vector, mag)
    return vector

def project_points():
    num_points = 200
    angle_step = (1 + math.sqrt(5)) / 2
    pow = 0.5
    start_color = (0, 0, 0, 1)
    points = []
    for i in range(0, num_points):
        t = i / (num_points - 1)
        inc = math.acos(1 - 2 * t)
        a = 2 * math.pi * angle_step * i
        
        x = math.sin(inc) * math.cos(a)
        y = math.sin(inc) * math.sin(a)
        z = math.cos(inc)
        bpy.ops.mesh.primitive_ico_sphere_add(align='WORLD', location=(x, y, z), radius=.01)
        
        obj = bpy.context.object
        if i == 0:
            point_mat = bpy.data.materials.new("point_mat")
            point_mat.diffuse_color = (1, 0, .28, 1)
            obj.data.materials.append(point_mat)
        points.append(obj)
    return points
