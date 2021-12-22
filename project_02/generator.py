import bpy
import bmesh
from bpy.types import Operator
#from functools import reduce

#import numpy as np
import random

from math import *
from mathutils import *

# set up for importing python modules
import sys
import os
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

# local module
import utils

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
        
        xyz_surface = utils.xyz_function_surface_faces(x_eq, y_eq, z_eq,
            range_u_min, range_u_max, range_u_step, wrap_u,
            range_v_min, range_v_max, range_v_step, wrap_v,
            a_eq, b_eq, c_eq, f_eq, g_eq, h_eq, n, close_v)
        data = { 'verts': xyz_surface[0], 'edges': [], 'faces': xyz_surface[1] }
        
        return data
    
    
    def make_sponge(self, name):
        """ Make a sponge """

        data = self.make_rotund_cylinder()
        texturing_scheme = self.sea_sponge_props.texturing_scheme
        
        bump_reducer = 1.0 if texturing_scheme == 'SMOOTH' else utils.get_bump_reducer(self.sea_sponge_props.bump_scale)

        for index, vert in enumerate(data["verts"]):
            # Construct mathutils.Vector
            vector_vert = Vector(vert)
            # Find bump factor based on texturing scheme
            bump = None
            if texturing_scheme == 'PERLIN':
                bump = noise.noise_vector(vector_vert)
            elif texturing_scheme == 'TURBULENCE':
                bump = noise.turbulence_vector(
                    vector_vert,
                    self.sea_sponge_props.turbulence_octaves,
                    False,
                    amplitude_scale=self.sea_sponge_props.turbulence_amplitude,
                    frequency_scale=self.sea_sponge_props.turbulence_frequency
                )
            elif texturing_scheme == 'STUCCO':
                bump = noise.turbulence_vector(
                    vector_vert,
                    self.sea_sponge_props.turbulence_octaves,
                    False,
                    amplitude_scale=self.sea_sponge_props.turbulence_amplitude,
                    frequency_scale=self.sea_sponge_props.turbulence_frequency
                )
                h = self.sea_sponge_props.dnoise_dist
                x1 = bump.x
                y1 = bump.y
                
                x2 = noise.turbulence_vector(
                    Vector((vector_vert.x + h, vector_vert.y, vector_vert.z)),
                    self.sea_sponge_props.turbulence_octaves,
                    False,
                    amplitude_scale=self.sea_sponge_props.turbulence_amplitude,
                    frequency_scale=self.sea_sponge_props.turbulence_frequency
                ).x
                y2 = noise.turbulence_vector(
                    Vector((vector_vert.x, vector_vert.y + h, vector_vert.z)),
                    self.sea_sponge_props.turbulence_octaves,
                    False,
                    amplitude_scale=self.sea_sponge_props.turbulence_amplitude,
                    frequency_scale=self.sea_sponge_props.turbulence_frequency
                ).y
                
                dx = (x2 - x1) / h
                dy = (y2 - y1) / h
                dnoise = Vector((dx, dy, 0))
                bump = dnoise.normalized()
            else:
                bump = Vector((1.0, 1.0))
            # Apply the bump factor and reducer
            new_x = vert[0] + bump.x / bump_reducer
            new_y = vert[1] + bump.y / bump_reducer
            data["verts"][index] = (new_x, new_y, vert[2])
                
        scene = bpy.context.scene
        obj = utils.object_from_data(data, name, scene)
        
        return obj
    

    def rotate_sponge(self, obj):
        obj.rotation_euler[0] = radians(random.randrange(-self.sea_sponge_props.x_rot, self.sea_sponge_props.x_rot))
        obj.rotation_euler[1] = radians(random.randrange(-self.sea_sponge_props.y_rot, self.sea_sponge_props.y_rot))
        obj.rotation_euler[2] = radians(random.randrange(self.sea_sponge_props.z_rot))
        
        
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
        
        
    def color_faces_by_dist(self, obj):
        mesh = bpy.context.object.data
        
        max_z = 0
        grouped_by_z = {}
        # Construct dictionary of faces' average vertices, keyed on z-value
        for index, face in enumerate(obj.data.polygons):
            avg_vert = utils.find_face_mean_vert(obj, face, False)
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
                dist = utils.get_distance_from_center(vert, z_centers[z])
                if dist > max_dist:
                    max_dist = dist
                if dist < min_dist:
                    min_dist = dist
            z_center_dist_max_mins[z] = (min_dist, max_dist)
            
        # Construct a dictionary of colors, keyed on distance from relative center
        face_color_dict = {}
        mat_count = 0
        for index, face in enumerate(obj.data.polygons):
            avg_vert = utils.find_face_mean_vert(obj, face, False)
            dist_to_center = utils.get_distance_from_center(avg_vert, z_centers[avg_vert.z])
            mapped_dist = round(utils.map_range(dist_to_center, z_center_dist_max_mins[avg_vert.z][0], z_center_dist_max_mins[avg_vert.z][1], 0, 1.0), 2)
            
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
            avg_vert = utils.find_face_mean_vert(obj, bm_face, True)
            dist_to_center =  utils.get_distance_from_center(avg_vert, z_centers[avg_vert.z])
            bm_mapped_dist = round(utils.map_range(dist_to_center, z_center_dist_max_mins[avg_vert.z][0], z_center_dist_max_mins[avg_vert.z][1], 0, 1.0), 2)
            bm_face.material_index = face_color_dict[bm_mapped_dist]
        bm.to_mesh(mesh)
    
    
    def color_faces_glass(self, obj):
        # create a test plane
#        bpy.ops.mesh.primitive_plane_add(location=(15, -5, 5))
        active_obj = bpy.context.active_object
#        plane.name = 'Voronoi Plane'
#        plane.scale = mathutils.Vector((4, 4, 4))
#        # tilt
#        plane.rotation_euler.rotate_axis('Y', math.radians(40))

        # Create a new material
        material = bpy.data.materials.new(name="Voronoi Shader")
        material.use_nodes = True

        # enable transparency
        material.blend_method = 'BLEND'

        material_output = material.node_tree.nodes.get('Material Output')
        bsdf_node = material.node_tree.nodes.get('Principled BSDF')

        # create smooth F1 voronoi shader node
        smooth_f1_voronoi_node = material.node_tree.nodes.new('ShaderNodeTexVoronoi')
        smooth_f1_voronoi_node.feature = 'SMOOTH_F1'
        smooth_f1_voronoi_node.inputs['Scale'].default_value = 20.0 # larger values -> smaller cells
        smooth_f1_voronoi_node.inputs['Smoothness'].default_value = 0.775 # smaller values -> thinner bones
        # randomness (smaller -> square)

        # create F1 voronoi shader node
        f1_voronoi_node = material.node_tree.nodes.new('ShaderNodeTexVoronoi')
        f1_voronoi_node.feature = 'F1'
        f1_voronoi_node.inputs['Scale'].default_value = 20.0 # this should be in sync with smooth_f1
        # randomness (smaller -> square)

        subtract_node = material.node_tree.nodes.new('ShaderNodeMath')
        subtract_node.operation = 'SUBTRACT'
        material.node_tree.links.new(subtract_node.inputs[0], f1_voronoi_node.outputs['Distance'])
        material.node_tree.links.new(subtract_node.inputs[1], smooth_f1_voronoi_node.outputs['Distance'])

        less_than_node = material.node_tree.nodes.new('ShaderNodeMath')
        less_than_node.operation = 'LESS_THAN'
        less_than_node.inputs[1].default_value = 0.06 # threshold
        material.node_tree.links.new(less_than_node.inputs[0], subtract_node.outputs[0])

        # create comparison node
        compare_node = material.node_tree.nodes.new('ShaderNodeMath')
        compare_node.operation = 'COMPARE'
        compare_node.inputs[1].default_value = 0.0 # value to compare against
        compare_node.inputs[2].default_value = 0.3 # epsilon
        material.node_tree.links.new(compare_node.inputs[0], less_than_node.outputs[0])

        # link shaders to material
        material.node_tree.links.new(bsdf_node.inputs['Base Color'], compare_node.outputs[0])
        material.node_tree.links.new(bsdf_node.inputs['Alpha'], compare_node.outputs[0])
        material.node_tree.links.new(material_output.inputs['Displacement'], f1_voronoi_node.outputs['Distance'])

        # set active material to new material
#        plane.active_material = material
        active_obj.active_material = material

    def color_faces(self, obj):
        shading_scheme = self.sea_sponge_props.shading_scheme
        if shading_scheme == 'CUSTOM_MATTE':
            self.color_faces_matte(obj)
        elif shading_scheme == 'GLASS':
            self.color_faces_glass(obj)
        else:
            self.color_faces_by_dist(obj)


    def execute(self, context):
        self.sea_sponge_props = context.scene.sea_sponge_properties
        
        # create sponges
        objs = []
        for x in range(self.sea_sponge_props.num_sponges):
            # set the radius based on props
            self.sea_sponge_props.radius = random.uniform(self.sea_sponge_props.min_radius, self.sea_sponge_props.max_radius)
            # create, color, and rotate the sponge
            obj = self.make_sponge(f"sponge_{x}")
            self.color_faces(obj)
            self.rotate_sponge(obj)
            objs.append(obj)
        
        scene = bpy.context.scene
        
        # Connect all sponges into one object
        ctx = bpy.context.copy()
        ctx['active_object'] = objs[0]
        ctx['selected_editable_objects'] = objs
        bpy.ops.object.join(ctx)
                
        return {'FINISHED'}
