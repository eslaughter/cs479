from bpy.props import IntProperty, FloatProperty
from bpy.types import PropertyGroup


class FlockProperties(PropertyGroup):
    num_boids: IntProperty(
        name='Number of Boids',
        description='',
        default=100,
        min=0,
        max=1000
    )
    x_range: IntProperty(
        name='X Range',
        description='',
        default=20,
        min=0,
        max=100
    )
    y_range: IntProperty(
        name='Y Range',
        description='',
        default=20,
        min=0,
        max=100
    )
    z_range: IntProperty(
        name='Z Range',
        description='',
        default=20,
        min=0,
        max=100
    )
    perception_radius: IntProperty(
        name='Perception Radius',
        description='',
        default=5,
        min=0,
        max=100
    )
    perception_angle: IntProperty(
        name='Perception Angle',
        description='',
        default=75,
        min=0,
        max=180
    )
    alignment_strength: FloatProperty(
        name='Alignment Strength',
        description='Number of sponges you want',
        default=0.7,
        min=0.0,
        max=1.0
    )
    cohesion_strength: FloatProperty(
        name='Cohesion Strength',
        description='Number of sponges you want',
        default=0.6,
        min=0.0,
        max=1.0
    )
    separation_strength: FloatProperty(
        name='Separation Strength',
        description='Number of sponges you want',
        default=0.8,
        min=0.0,
        max=1.0
    )
    max_velocity: FloatProperty(
        name='Max Velocity',
        description='Number of sponges you want',
        default=2.0,
        min=0.0,
        max=100.0
    )
    max_acceleration: FloatProperty(
        name='Max Acceleration',
        description='Number of sponges you want',
        default=0.4,
        min=0.0,
        max=10.0
    )
    frames: IntProperty(
        name='Frames',
        description='',
        default=250,
        min=0,
        max=10000
    )
    num_groups: IntProperty(
        name='Number of Groups',
        description='',
        default=3,
        min=0,
        max=100
    )