import bpy
from bpy.props import PointerProperty

# set up for importing python modules
import sys
import os
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

# local modules
from panel import SeaSpongePanel
from properties import SeaSpongeProperties
from generator import GenSeaSponge

# ---------------------------------------------------------

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
