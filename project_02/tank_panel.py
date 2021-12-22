import bpy

class FishTankPanel(bpy.types.Panel):
    bl_label = "Fish Tank Panel"
    bl_idname = "OBJECT_PT_fish_tank_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Fish Tank"
    
    def draw(self, context):
        fish_tank_props = context.scene.fish_tank_properties
        layout = self.layout
        row = layout.row()
        col = layout.column(align=True)
        col.label(text='Fish Tank:')
        col.prop(fish_tank_props, 'scale')
        row = layout.row()
        row.operator('sea.gen_fish_tank', text='Generate')
