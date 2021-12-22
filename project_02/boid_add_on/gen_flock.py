import bpy
import bmesh
from bpy.props import PointerProperty, IntProperty, FloatProperty
from bpy.types import Operator

import mathutils

import math

# set up for importing python modules
import sys
import os
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import boid_utils as utils
from boid import Boid



bl_info = {
    "name": "Boids",
    "description": "boids",
    "author": "Charlie Orr",
    "version": (1, 0, 0),
    "blender": (2, 93, 4),
    "wiki_url": "my github url here",
    "tracker_url": "my github url here/issues",
    "category": "Animation"
}


    
class GenFlock(Operator):
    bl_idname = 'flock.gen_flock'
    bl_label = 'Generate Sea Sponge'
    bl_options = {'REGISTER', "UNDO"}
    
    def setup(self, context):
#        utils.clear_scene()
        self.flock_props = context.scene.flock_properties
        region_cube = utils.gen_region_cube(
            self.flock_props.x_range,
            self.flock_props.y_range,
            self.flock_props.z_range
        )

        
        bpy.ops.mesh.primitive_cube_add(scale=(5, 5, 5), align='WORLD', location=(0.0, 0.0, 0.0))
        obj = bpy.context.object
        
        scene_objs = [region_cube, obj]
        
        self.flock = []
        projection_points = utils.project_points()
        for x in range(0, self.flock_props.num_boids):

            boid = Boid(self.flock_props, scene_objs, x, projection_points)
            self.flock.append(boid)
            
        
    def generate(self, context):
        
        for frame in range(0, self.flock_props.frames):
            context.scene.frame_set(frame)
            for boid in self.flock:
                boid.flock(self.flock)
                boid.update()
                boid.show()
            print(f"Frame {frame} COMPLETE")
    
    def execute(self, context):
        self.setup(context)
        self.generate(context)
        
        return {'FINISHED'}



