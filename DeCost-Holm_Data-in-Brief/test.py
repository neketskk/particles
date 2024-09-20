import os
import random
import sys

import bpy
import numpy as np

from PIL import Image, ImageEnhance, ImageFilter

C = bpy.context
D = bpy.data
R = C.scene.render

root_dir = os.path.join(os.path.dirname(D.filepath), "..")
if root_dir not in sys.path:
    sys.path.append(root_dir)

import bpy.particles  # isort:skip
import bpy.scene  # isort:skip
from recipe_utilities import generate_gaussian_noise_image

# # Force reload in case you edit the source after you first start the blender session.
# import importlib
#
# importlib.reload(blender.particles)
# importlib.reload(blender.scene)

# Settings
bpy.scene.apply_default_settings()

resolution = (1024, 768)

primitive_path = os.path.join(
    root_dir, "primitives", "sopat_catalyst", "light.blend"
)


def compose_layers(
    background_layer, background_noise_layer, noise_layer, particle_layer
):
    final_image = background_layer
    final_image = Image.blend(final_image, background_noise_layer, 0.2)
    final_image = Image.alpha_composite(final_image, particle_layer)
    final_image = Image.blend(final_image, noise_layer, 0.2)
    return final_image


def create_image_layers(resolution):
    particle_layer = bpy.scene.render_to_variable()
    background_layer = generate_gaussian_noise_image(
        resolution, scale=200, strength=0.1, contrast=0.2, brightness=0.6,
    )
    background_noise_layer = generate_gaussian_noise_image(
        resolution, scale=20, strength=0.1, contrast=0.2, brightness=0.6,
    )
    noise_layer = generate_gaussian_noise_image(resolution, strength=0.075)
    return (
        background_layer,
        background_noise_layer,
        noise_layer,
        particle_layer,
    )

def render_image(resolution):
    (
        background_layer,
        background_noise_layer,
        noise_layer,
        particle_layer,
    ) = create_image_layers(resolution)
    final_image = compose_layers(
        background_layer, background_noise_layer, noise_layer, particle_layer,
    )
    return final_image

n_images = 1

for image_id in range(n_images):
    with bpy.scene.TemporaryState():
        bpy.scene.set_resolution(resolution)
        primitive = bpy.particles.load_primitive(primitive_path)

        # Ensure reproducibility of the psd.
        random.seed(image_id)

        # Create fraction: light particles
        name = "light"
        n = np.random.randint(50, 120)


        d_g = np.random.rand() * 50 + 25
        sigma_g = np.random.rand() * 0.6 + 1
        particles = bpy.particles.generate_lognormal_fraction(
            primitive, name, n, d_g, sigma_g, particle_class="light"
        )

        # Place particles.
        n_frames = 5
        lower_space_boundaries_xyz = (
            -resolution[0] / 2,
            -resolution[1] / 2,
            -10,
        )
        upper_space_boundaries_xyz = (resolution[0] / 2, resolution[1] / 2, 10)
        damping = 1
        collision_shape = "sphere"

        bpy.particles.place_randomly(
            particles,
            lower_space_boundaries_xyz,
            upper_space_boundaries_xyz,
            do_random_rotation=True,
        )

        bpy.particles.relax_collisions(
            particles, damping, collision_shape, n_frames
        )

        image_id_string = "image{:06d}".format(image_id)

        output_folder_path_base = os.path.join(
            root_dir, "output", "white", image_id_string
        )

        # Render and save current image and masks.
        image = render_image(resolution)

        image_file_name = image_id_string + ".png"
        image_folder_path = os.path.join(output_folder_path_base, "images")
        if not os.path.exists(image_folder_path):
            os.makedirs(image_folder_path)
        image_file_path = os.path.join(image_folder_path, image_file_name)
        image = image.convert("L")
        image.save(image_file_path)

        mask_folder_path = os.path.join(output_folder_path_base, "masks")
        bpy.scene.render_occlusion_masks(
            particles, image_id_string, mask_folder_path
        )
