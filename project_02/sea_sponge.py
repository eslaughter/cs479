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

from tank_panel import FishTankPanel
from tank_properties import FishTankProperties
from tank_generator import GenFishTank

# ---------------------------------------------------------

CLASSES = [GenSeaSponge, SeaSpongeProperties, GenFishTank, FishTankProperties]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.sea_sponge_properties = PointerProperty(type=SeaSpongeProperties)
    bpy.types.Scene.fish_tank_properties = PointerProperty(type=FishTankProperties)
    
    bpy.utils.register_class(SeaSpongePanel)
    bpy.utils.register_class(FishTankPanel)

def unregister():
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.sea_sponge_properties
    del bpy.types.Scene.fish_tank_properties
    bpy.utils.unregister_class(SeaSpongePanel)
    bpy.utils.unregister_class(FishTankPanel)

    
if __name__ == "__main__":
    register()
