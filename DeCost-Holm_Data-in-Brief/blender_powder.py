import bpy

import os
import sys
import json
import numpy as np
    
# Blender python scripts can't take command-line arguments directly
# one solution: pass arguments by setting shell environment variables.
#
# TEXTUREPATH: path to particle surface texture image source
# PARTICLESPATH: path particle sizes and positions (json data)
# RENDERPATH: path to write rendered image

# try to pull arguments from environment variables
# if not set: go with a reasonable default

os.environ['TEXTUREPATH']="C:/Desktop/Diplom/DeCost-Holm_Data-in-Brief/metal_texture.jpg"
try:
    texture_path = os.environ['TEXTUREPATH']
except KeyError:
    texture_path = os.path.expanduser('texture_source.jpg')
    print('using default texture path (set TEXTUREPATH to specify a source image)')

try:
    particles_path = os.environ['PARTICLESPATH']
except KeyError:
    particles_path = 'particles.json'
    print('using default particles path (set PARTICLESPATH)')

try:
    renderpath = os.environ['RENDERPATH']
except KeyError:
    # default: write to current working directory
    renderpath = os.path.expanduser('render.jpg')
    print('writing render to default path ./render.jpg (set RENDERPATH)')

# delete the cube that's loaded by default
# it should already be selected when blender starts
bpy.ops.object.delete()

# change position for the default lamp:
loc = (3,3,5)

light_data = bpy.data.lights.new(name="my-light-data", type='POINT')
light_data.energy = 100

lamp = bpy.data.objects.new(name="my-light", object_data=light_data)
bpy.context.collection.objects.link(lamp)

#lamp = bpy.data.objects['Lamp']
lamp.location = loc

# set up a few more lamps
def newlamp(name, lamptype, loc):
    bpy.ops.object.add(type='LIGHT', location=loc)
    lamp = bpy.context.object
    lamp.name = str(name)
    lamp.data.name = 'Lamp{}'.format(name)
    lamp.data.type = lamptype
    return lamp

locs = [(-3,3,5), (-3,-3,5), (3,-3,5)]
for i, loc in enumerate(locs):
    newlamp(i, 'POINT', loc)
    
scene = bpy.data.scenes["Scene"]

# Set render resolution
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024

# Set camera rotation in euler angles
scene.camera.rotation_mode = 'XYZ'
scene.camera.rotation_euler = (0.0, 0.0, 0.0)

# set the camera position
scene.camera.location.x = 0
scene.camera.location.y = 0
#scene.camera.location.z = 10

scene.camera.location.z = 10

# first choose the cycles rendering engine
bpy.context.scene.render.engine = 'CYCLES'

# set up material for the particles
mat = bpy.data.materials.new('thematerial')
mat.use_nodes = True

texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
texImage.image = bpy.data.images.load(texture_path)
# load texture source image (TEXTUREPATH argument)
# try:
#     texture_source = bpy.data.images.load(texture_path)
# except:
#     raise NameError("can't load {}".format(texture_path))


# Create image texture data from image
# tex = bpy.data.textures.new('ColorTex', type = 'IMAGE')
# tex.image = texture_source

# add image texture to material
# mtex = mat.texture_slots.add()
# mtex.texture = tex 
# mtex.texture_coords = 'UV'
# mtex.use_map_normal = True

# mat.node_tree.links.new(texImage.outputs[0], mat.node_tree.nodes[0].inputs["Base Color"])

# load particle dataset    
with open(particles_path, 'r') as f:
    dataset = json.load(f)

# particle positions are specified on [0,1]
# set the size of the render box:
scale = np.array([11.0, 11.0, 2.0])


# build spherical mesh model for each particle
for particle in dataset['particles']:

    size = particle['size']
    
    # particle positions are specified on [0,1] -- scale this to fill the render volume
    loc = np.array([particle['x'], particle['y'], particle['z']])
    x, y, z = scale * loc - scale/2

    # choose random Euler angles to rotate each particle
    a1, a2, a3 = np.pi / 2 * np.random.random(3)
    import bpy_extras
    from mathutils import Vector
    # create spherical mesh for each particle
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64,
        ring_count=32,
        radius=size,
        location=(x,y,z),
        rotation=(a1,a2,a3))

    # set up for texture unwrapping
    render_scale = scene.render.resolution_percentage / 100
    render_size = (
    int(scene.render.resolution_x * render_scale),
    int(scene.render.resolution_y * render_scale),
    )
    coord_3d = Vector((x, y, z))
    coords_2d = bpy_extras.object_utils.world_to_camera_view(scene, scene.camera, coord_3d)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.context.object.data.materials.append(mat)
    
    bpy.ops.object.shade_smooth()

# switch render engine back
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'

# render the scene and save to RENDERPATH


bpy.context.scene.render.filepath = renderpath
bpy.ops.render.render(write_still=True) 
