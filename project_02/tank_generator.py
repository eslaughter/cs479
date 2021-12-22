import bpy
import mathutils
from bpy.types import Operator

# set up for importing python modules
import sys
import os
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)


class GenFishTank(Operator):
    bl_idname = 'sea.gen_fish_tank'
    bl_label = 'Generate Fish Tank'
    bl_options = {'REGISTER', "UNDO"}
    
    def load_raw_objects(self):
        project_dir = os.path.dirname(os.path.realpath(__file__))
        filepath_name = project_dir + '/fish_tank.obj'
        bpy.ops.import_scene.obj(filepath=filepath_name)
        return bpy.context.selected_objects
    
    def scale(self, objs, x, y, z):
        for obj in objs:
            obj.scale = (x,y,z)
    
    def add_sand(self):
        # create a test plane
        # get location, scale from tank
        l_x = -0.687357
        l_y = -0.175115
        l_z = -0.277450
        p_location = (l_x, l_y, l_z)
        p_scale = (0.7, 0.25, 1)
        bpy.ops.mesh.primitive_plane_add(location=(0,0,0), scale=p_scale)
        
        plane = bpy.context.active_object
#        plane.location = p_location
        plane.name = 'Sand'
        plane.scale = p_scale
        
        # add materials to it
        sand_mat = bpy.data.materials.new(name="Sand")
        sand_mat.use_nodes = True

#        # enable transparency
#        glass_mat.blend_method = 'BLEND'

        material_output = sand_mat.node_tree.nodes.get('Material Output')
        bsdf_node = sand_mat.node_tree.nodes.get('Principled BSDF')
        color = bsdf_node.inputs['Base Color'].default_value
        color[0] = 0.1 # R
        color[1] = 0.1 # G
        color[2] = 0 # B
        
        
        
        
        # create smooth F1 voronoi shader node
#        smooth_f1_voronoi_node = material.node_tree.nodes.new('ShaderNodeTexVoronoi')
#        smooth_f1_voronoi_node.feature = 'SMOOTH_F1'
#        smooth_f1_voronoi_node.inputs['Scale'].default_value = 20.0 # larger values -> smaller cells
#        smooth_f1_voronoi_node.inputs['Smoothness'].default_value = 0.775 # smaller values -> thinner bones
#        # randomness (smaller -> square)

#        # create F1 voronoi shader node
#        f1_voronoi_node = material.node_tree.nodes.new('ShaderNodeTexVoronoi')
#        f1_voronoi_node.feature = 'F1'
#        f1_voronoi_node.inputs['Scale'].default_value = 20.0 # this should be in sync with smooth_f1
#        # randomness (smaller -> square)

#        subtract_node = material.node_tree.nodes.new('ShaderNodeMath')
#        subtract_node.operation = 'SUBTRACT'
#        material.node_tree.links.new(subtract_node.inputs[0], f1_voronoi_node.outputs['Distance'])
#        material.node_tree.links.new(subtract_node.inputs[1], smooth_f1_voronoi_node.outputs['Distance'])

#        less_than_node = material.node_tree.nodes.new('ShaderNodeMath')
#        less_than_node.operation = 'LESS_THAN'
#        less_than_node.inputs[1].default_value = 0.06 # threshold
#        material.node_tree.links.new(less_than_node.inputs[0], subtract_node.outputs[0])

#        # create comparison node
#        compare_node = material.node_tree.nodes.new('ShaderNodeMath')
#        compare_node.operation = 'COMPARE'
#        compare_node.inputs[1].default_value = 0.0 # value to compare against
#        compare_node.inputs[2].default_value = 0.3 # epsilon
#        material.node_tree.links.new(compare_node.inputs[0], less_than_node.outputs[0])

#        # link shaders to material
##        sand_mat.node_tree.links.new(bsdf_node.inputs['Base Color'], compare_node.outputs[0])
##        sand_mat.node_tree.links.new(bsdf_node.inputs['Alpha'], compare_node.outputs[0])
##        sand_mat.node_tree.links.new(material_output.inputs['Displacement'], f1_voronoi_node.outputs['Distance'])
#        
#        plane.active_material = sand_mat
        
        
    
    def execute(self, context):
        self.fish_tank_props = context.scene.fish_tank_properties
        
        scale = self.fish_tank_props.scale
        scale_x = scale_y = scale_z = scale
        
        tank_objs = self.load_raw_objects()
        self.scale(tank_objs, scale_x, scale_y, scale_y)
#        self.add_sand()
        
        # Connect all sponges into one object
        ctx = bpy.context.copy()
        ctx['active_object'] = tank_objs[0]
        ctx['selected_editable_objects'] = tank_objs
        bpy.ops.object.join(ctx)
                
        return {'FINISHED'}
