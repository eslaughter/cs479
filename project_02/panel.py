import bpy

class SeaSpongePanel(bpy.types.Panel):
    bl_label = "Sea Sponge Panel"
    bl_idname = "OBJECT_PT_sea_sponge_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sea Sponge"
    
    def draw(self, context):
        layout = self.layout
        sea_sponge_props = context.scene.sea_sponge_properties
        row = layout.row()
        col = layout.column(align=True)
        col.label(text='Geometry:')
        col.prop(sea_sponge_props, 'num_sponges')
        col.prop(sea_sponge_props, 'min_radius')
        col.prop(sea_sponge_props, 'max_radius')
        col.prop(sea_sponge_props, 'rotundness')
        row = layout.row()
        col.prop(sea_sponge_props, 'min_height')
        col.prop(sea_sponge_props, 'max_height')
        col.prop(sea_sponge_props, 'x_rot')
        col.prop(sea_sponge_props, 'y_rot')
        col.prop(sea_sponge_props, 'z_rot')
        col.prop(sea_sponge_props, 'resolution')
        col.label(text='Texturing:')
        col.prop(sea_sponge_props, 'texturing_scheme')
        if sea_sponge_props.texturing_scheme == 'PERLIN' or sea_sponge_props.texturing_scheme == 'TURBULENCE':
            col.prop(sea_sponge_props, 'bump_scale')
        if sea_sponge_props.texturing_scheme == 'TURBULENCE':
            col.prop(sea_sponge_props, 'turbulence_octaves')
        col.label(text='Custom Shading:')
        col.prop(sea_sponge_props, 'shading_scheme')
        if 'CUSTOM' in sea_sponge_props.shading_scheme:
            col.prop(sea_sponge_props, 'red_channel')
            col.prop(sea_sponge_props, 'green_channel')
            col.prop(sea_sponge_props, 'blue_channel')
        row = layout.row()
        row.operator('sea.gen_sea_sponge', text='Generate')