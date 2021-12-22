import bpy
from bpy.props import PointerProperty

# set up for importing python modules
import sys
import os
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

# local modules
from boid_panel import FlockPanel
from boid_properties import FlockProperties
from gen_flock import GenFlock

CLASSES = [FlockProperties, GenFlock]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.flock_properties = PointerProperty(type=FlockProperties)
    bpy.utils.register_class(FlockPanel)
   
    
    
def unregister():
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.flock_properties
    bpy.utils.unregister_class(FlockPanel)
    
    
if __name__ == "__main__":
    register()