import bpy

class FlockPanel(bpy.types.Panel):
    bl_label = "Flock Panel"
    bl_idname = "OBJECT_PT_flock_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Flock"
    
    def draw(self, context):
        layout = self.layout
        flock_props = context.scene.flock_properties
        
        row = layout.row()
        col = layout.column(align=True)
        col.prop(flock_props, 'num_boids')
        col.prop(flock_props, 'x_range')
        col.prop(flock_props, 'y_range')
        col.prop(flock_props, 'z_range')
        col.prop(flock_props, 'perception_radius')
        col.prop(flock_props, 'perception_angle')
        col.prop(flock_props, 'alignment_strength')
        col.prop(flock_props, 'cohesion_strength')
        col.prop(flock_props, 'separation_strength')
        col.prop(flock_props, 'max_velocity')
        col.prop(flock_props, 'max_acceleration')
        col.prop(flock_props, 'frames')
        col.prop(flock_props, 'num_groups')
        row = layout.row()
        row.operator('flock.gen_flock', text='Generate')