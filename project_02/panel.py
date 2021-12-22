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
        col.prop(sea_sponge_props, 'species')
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
        if sea_sponge_props.species in ['TUBE','GROSS']:
            col.label(text='Texturing:')
            col.prop(sea_sponge_props, 'texturing_scheme')
            col.prop(sea_sponge_props, 'bump_scale')
            if sea_sponge_props.texturing_scheme == 'TURBULENCE':
                col.prop(sea_sponge_props, 'turbulence_octaves')
                col.prop(sea_sponge_props, 'turbulence_amplitude')
                col.prop(sea_sponge_props, 'turbulence_frequency')
            if sea_sponge_props.texturing_scheme == 'STUCCO':
                col.prop(sea_sponge_props, 'turbulence_octaves')
                col.prop(sea_sponge_props, 'turbulence_amplitude')
                col.prop(sea_sponge_props, 'turbulence_frequency')
                col.prop(sea_sponge_props, 'dnoise_dist')
                
            col.label(text='Custom Shading:')
            col.prop(sea_sponge_props, 'shading_scheme')
            if 'CUSTOM' in sea_sponge_props.shading_scheme:
                col.prop(sea_sponge_props, 'red_channel')
                col.prop(sea_sponge_props, 'green_channel')
                col.prop(sea_sponge_props, 'blue_channel')
        elif sea_sponge_props.species == 'GLASS':
            col.label(text='Glass cell size:')
            col.prop(sea_sponge_props, 'glass_cell_scale')
            col.label(text='Glass cell smoothness:')
            col.prop(sea_sponge_props, 'glass_cell_smoothness')
        row = layout.row()
        row.operator('sea.gen_sea_sponge', text='Generate')