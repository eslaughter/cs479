from bpy.props import IntProperty
from bpy.types import PropertyGroup

class FishTankProperties(PropertyGroup):
    scale: IntProperty(
        name='Scale',
        description='Scale of tank to generate',
        default=1,
        min=1,
        max=40
    )
    