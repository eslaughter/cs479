from bpy.props import IntProperty, FloatProperty, EnumProperty
from bpy.types import PropertyGroup

class SeaSpongeProperties(PropertyGroup):
    min_radius: FloatProperty(
        name='Minimum Radius',
        description='Minimum range of radius from Z',
        default=0.5,
        min=0.0,
        max=10.0
    )
    max_radius: FloatProperty(
        name='Maximum Radius',
        description='Maximum range of radius from Z',
        default=0.1,
        min=0.0,
        max=10.0
    )
    rotundness: FloatProperty(
        name='Radial Rotundness',
        description='Degree of radial rotundness',
        default=0.5,
        min=0.25,
        max=0.75
    )
    min_height: FloatProperty(
        name='Minimum Height',
        description='Minimum range of sponge length',
        default=1.0,
        min=0.1,
        max=10.0
    )
    max_height: FloatProperty(
        name='Maximum Height',
        description='Maximum range of sponge length',
        default=2.0,
        min=0.1,
        max=10.0
    )
    x_rot: IntProperty(
        name='X Rotation Range',
        description='Degree of rotation around x axis',
        default=45,
        min=0,
        max=90
    )
    y_rot: IntProperty(
        name='Y Rotation Range',
        description='Degree of rotation around y axis',
        default=45,
        min=0,
        max=90
    )
    z_rot: IntProperty(
        name='Z Rotation Range',
        description='Degree of rotation around z axis',
        default=360,
        min=0,
        max=360
    )
    num_sponges: IntProperty(
        name='Number of Sponges',
        description='Number of sponges to generate',
        default=20,
        min=0,
        max=1000
    )
    shading_scheme: EnumProperty(
        name='Shading Scheme',
        description='Presets for shading schemes',
        items=[
            ('CUSTOM_MATTE', 'Custom Matte', 'Custom color without depth'),
            ('CUSTOM_DEPTH', 'Custom Depth', 'Custom color with depth'),
            ('RUGRATS', 'Rugrats', '90s-style and color scheme'),
            ('GLASS', 'Glass', 'Mimics the texture of a glass sponge')
        ],
        default='RUGRATS'
    )
    texturing_scheme: EnumProperty(
        name='Texturing Scheme',
        description='Method for generating texture',
        items=[
            ('NONE', 'Smooth', 'Generate a smooth surface'),
            ('PERLIN', 'Perlin Noise', 'Use noise to generate bumpiness'),
            ('TURBULENCE', 'Turbulence', 'Use turbulence to generate bumpiness'),
            ('STUCCO', 'Stucco', 'Generate Stucco texture')
            
        ],
        default='TURBULENCE'
    )
    dnoise_dist: FloatProperty(
        name='Dnoise Dist',
        description='DNoise sampling dist',
        default=0.00001,
        min=0.0,
        max=1.0
    )
    bump_scale: IntProperty(
        name='Bump Scale',
        description='Scale of bumpiness 1-10',
        default=10,
        min=1,
        max=10
    )
    turbulence_octaves: IntProperty(
        name='Bump Frequency',
        description='Number of turbulence octaves',
        default=7,
        min=0,
        max=100
    )
    turbulence_amplitude: FloatProperty(
        name='Amplitude',
        description='Amplitude',
        default=0.5,
        min=-100.0,
        max=10.0
    )
    turbulence_frequency: FloatProperty(
        name='Frequency',
        description='Frequency',
        default=0.5,
        min=-100.0,
        max=10.0
    )
    red_channel: FloatProperty(
        name='Amount of Red 0-1',
        description='Amount of red 0-1',
        default=0.8,
        min=0.0,
        max=1.0
    )
    green_channel: FloatProperty(
        name='Amount of Green 0-1',
        description='Amount of green 0-1',
        default=0.8,
        min=0.0,
        max=1.0
    )
    blue_channel: FloatProperty(
        name='Amount of Blue 0-1',
        description='Amount of blue 0-1',
        default=0.8,
        min=0.0,
        max=1.0
    )
    resolution: IntProperty(
        name='Resolution',
        description='Number of subdivisions in generating faces/vertices',
        default=20,
        min=10,
        max=1000
    )
    radius: FloatProperty(
        name='Radius',
        description='Store radius',
        default=0.1,
        min=0.0,
        max=10.0
    )
    max_z: FloatProperty(
        name='maximum z',
        description='Store maximum z',
        default=0.1,
        min=0.0,
        max=100000.0
    )
