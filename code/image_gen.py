import blenderproc as bproc
import bpy # blender python API
import yaml
import os
import numpy as np

# Constants and Configurations
CONFIG_FILE = 'image_gen_config.yaml'

def load_config(path):
    """
    Load configuration from a YAML file.

    Args:
    path (str): The file path to the YAML configuration file.

    Returns:
    dict: Configuration dictionary.

    """

    with open(path, 'r', encoding='utf-8') as file:
        # Load the YAML file
        config = yaml.safe_load(file)  # Use safe_load to prevent the execution of arbitrary code    
    return config

def randomize_workpiece_on_table(workpiece, table, table_dimensions, workpiece_dimensions):
    """
    Randomly position and rotate a workpiece on a table.

    Args:
    workpiece: The workpiece object to be randomized.
    table: The table object where the workpiece is placed.
    table_dimensions: The dimensions of the table.
    workpiece_dimensions: The dimensions of the workpiece.

    """
    table_loc = table.get_location()
    width, depth, _ = table_dimensions
    _, _, workpiece_height = workpiece_dimensions

    # Generate a new position for the workpiece
    new_x = np.random.uniform(table_loc[0] - width/2, table_loc[0] + width/2)
    new_y = np.random.uniform(table_loc[1] - depth/2, table_loc[1] + depth/2)
    top_surface_z = table_loc[2] + workpiece_height  # Calculate the Z position based on the workpiece height.

    # Update workpiece location and rotation
    workpiece.set_location([new_x, new_y, top_surface_z])
    rnd_rotation = np.random.uniform([0, 0, 0], [0, 0, np.pi])  # Randomize rotation around the Z-axis.
    workpiece.set_rotation_euler(rnd_rotation)

def configure_camera_and_lighting(table, table_dimensions, config):
    """
    Configure the camera and lighting based on the table's location and specified dimensions.

    Args:
    table: The table object to focus the camera on.
    config: Configuration dictionary.

    """
    centroid = table.get_local2world_mat()[:3, 3]  # Using the translation part of the matrix for the centroid
    max_dimension = max(table_dimensions)

    # Define camera position and point of interest
    radius_min = max_dimension * 1.2
    radius_max = max_dimension * 2.0
    location = bproc.sampler.shell(center=centroid, radius_min=radius_min, radius_max=radius_max,
                                    elevation_min=10, elevation_max=40, azimuth_min=-180, azimuth_max=180, uniform_volume=True)
    poi = centroid + np.random.uniform([-0.2, -0.2, 0], [0.2, 0.2, 0.2])  # Define a point of interest with slight randomization.

    # Calculate camera rotation and set up the camera
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location)  # Calculate the rotation matrix to look at the POI.
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)  # Build the transformation matrix for the camera.
    bproc.camera.add_camera_pose(cam2world_matrix) 

    # Set the camera lens to 35mm for a standard field of view.
    bpy.data.cameras['Camera'].lens = config['camera_lens']  

    # Configure lighting
    light = bproc.types.Light()
    light.set_energy(config['light_energy']) 
    light.set_type(config['light_type'])  
    light.set_location(location + np.array([1, -1, 2]))  # Position the light near the camera with some offset.

def set_random_armature_transform_near_table(armature_name, config):
    """
    Randomly sets the armature location near the table(hardcoded).

    Args:
    armature: The worker armature name to be transformed.
    table: The table object used as a reference for setting the armature.
    config: Configuration dictionary.

    """
    armature_obj = bpy.data.objects.get(armature_name) 

    # Hard-coded values for worker position randomization
    rand_x = np.random.uniform(-1, 1)  # x-axis
    rand_y = np.random.uniform(1, 1.75)  # y-axis
    fixed_offset = 0.12
    fixed_rotation = (1.57, 0.0, 0.0)  # Fixed rotation (90° about x-axis)

    new_location = (rand_x, rand_y, fixed_offset)  # Assumes the height of the table plus a fixed offset
    armature_obj.location = new_location  
    armature_obj.rotation_mode = 'XYZ'
    armature_obj.rotation_euler = fixed_rotation  

    print(f"Armature '{armature_name}' updated to location: {new_location} and rotation: {fixed_rotation}")

    randomize_arm_positions(armature_obj, config)  # Randomize the arm positions

def create_sphere_at_location(location, diameter=0.4):
    """
    Create a transparent sphere at a specified location.

    Args:
    location (tuple): The location to create the sphere at.
    diameter (float): Diameter of the sphere.

    Returns:
    Created sphere object.

    """
    # create a sphere at the specified location with the given diameter
    bpy.ops.mesh.primitive_uv_sphere_add(radius=diameter/2, location=location)  
    sphere = bpy.context.object
    sphere.name = 'SafetyZone' 

    # configure the sphere material
    if sphere.data.materials:
        mat = bproc.python.types.MaterialUtility.Material(sphere.data.materials[0])
    else:
        bpy_mat = bpy.data.materials.new(name="TransparentMaterial")
        bpy_mat.use_nodes = True
        mat = bproc.python.types.MaterialUtility.Material(bpy_mat)
        sphere.data.materials.append(bpy_mat)

    transparency_level = 0.65
    mat.set_principled_shader_value('Base Color', (1, 0, 0, 1))  # Set the base color - red.
    mat.set_principled_shader_value('Alpha', transparency_level)  # Set transparency.
    mat.set_principled_shader_value('Transmission', 1.0)  # Enable transmission for glass-like appearance.
    return sphere

def update_sphere_position(sphere, armature, bone_name="Axis-7"):
    """
    Update the position of a sphere to match the position of a specified bone in an armature.

    Args:
    sphere: The sphere object to be updated.
    armature: The armature containing the bone.
    bone_name (str): The name of the bone whose position to follow.

    """
    bone = armature.pose.bones.get(bone_name) 
    if bone:
        sphere.location = armature.matrix_world @ bone.head  # Calculate the global position of the bone and set the sphere's location.
        bpy.context.view_layer.update()  
        print(f"Updated sphere location to: {sphere.location}")

def load_and_manipulate_objects_from_blend(file_path, object_type=None, link=False):
    """
    Load objects from a .blend file and optionally filter them by type.

    Args:
    file_path (str): Path to the .blend file.
    object_type (str, optional): Type of the objects to load. Defaults to None.('OBJECT', 'MESH', 'ARMATURE', etc.)
    link (bool, optional): Whether to link the objects. Defaults to False.
    Returns:
    dict: Loaded objects with names as the key.

    """
    with bpy.data.libraries.load(file_path, link=link) as (data_from, data_to):
        if object_type:
            filtered_objects = [obj for obj in data_from.objects if bpy.data.objects[obj].type == object_type] 
            data_to.objects = filtered_objects
        else:
            data_to.objects = data_from.objects  # Load all objects if no specific type is required.

    loaded_objects = {}
    for obj in data_to.objects:
        if not link:
            bpy.context.collection.objects.link(obj)  # Link object to the current scene if not linking.
        loaded_objects[obj.name] = obj
        print(f"Loaded object: {obj.name}")
    return loaded_objects

def print_armature_bones(armature_name):
    """
    Print details of all bones in an armature.

    Args:
    armature_name (str): The name of the armature whose bones to print.

    """
    armature = bpy.data.objects.get(armature_name)
    if not armature or armature.type != 'ARMATURE':
        print(f"Error: No armature found with the name {armature_name}")
        return

    print("Listing all pose bones in armature:")
    for bone in armature.pose.bones:
        parent_name = bone.parent.name if bone.parent else 'None'
        print(f"Bone Name: {bone.name}, Parent: {parent_name}, Location: {bone.head}, Rotation: {bone.rotation_euler}")
    

def randomize_panda_armature_poses(armature_name, table, table_dimensions, config, sphere=None):

    """
    Randomly adjusts the pose of a Panda robot armature based on the table dimensions.

    Args:
    armature_name (str): The name of the robot.
    table: The table object where the robot is placed.
    table_dimensions: The dimensions of the table.
    config: Configuration dictionary.

    """
    armature = bpy.data.objects.get(armature_name) 
    width, depth, _ = table_dimensions  
    table_loc = table.get_location() 

    # Generate a new position for the armature
    new_x = np.random.uniform(table_loc[0] - width/2, table_loc[0] + width/2) 
    new_y = np.random.uniform(table_loc[1] - depth/2, table_loc[1] + depth/2)  
    top_surface_z = table_loc[2] + 0.05 # Set a slight offset for the Z position.

    # Update the armature location and rotation
    armature.location = (new_x, new_y, top_surface_z)
    armature.rotation_mode = 'XYZ'
    armature.rotation_euler = (0, 0, np.random.uniform(-np.pi/4, np.pi/4))  # Randomize z-axis +/-45°.

    # Switch to pose mode to manipulate the armature bones.
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    # Apply random rotations to each bone within specified limits
    for bone_name, limits in config['bones_to_randomize'].items():
        bone = armature.pose.bones.get(bone_name)
        if bone:
            random_angle = np.random.uniform(*limits)
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler = (0, 0, random_angle) 

            if bone_name == "Axis-7":
                update_sphere_position(sphere, armature, bone_name)  # Update sphere's position to Axis 7 bone during randomization

    # Return to object mode after manipulating the armature            
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Random rotations applied to Panda armature with realistic limits.")


def randomize_arm_positions(armature_obj, config):
    """
    Randomize the rotations of specified arm bones in an armature object.
    
    Args:
    armature_obj: The worker object whose arm positions will be randomized.

    """ 
    # Switch to pose mode to manipulate the armature bones.
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')   
    for bone_name in config['bones_to_randomize_worker']:
        bone = armature_obj.pose.bones.get(bone_name)  
        if bone:
            bone.rotation_mode = 'XYZ'

            # Generate random rotation angles with different ranges for realism
            x_angle = np.random.uniform(-0.52, 1.57)  # forward positioning
            y_angle = np.random.uniform(-0.26, 1.57)  # side-to-side movement
            z_angle = np.random.uniform(0, 0.3)  # twist

            if 'Forearm' in bone_name:
                # More restricted movement for forearms
                rotation = (x_angle * 0.5, y_angle * 0.3, z_angle * 0.2)
            else:
                rotation = (x_angle, y_angle, z_angle)  

            bone.rotation_euler = rotation  # Apply the calculated rotation to the bone
            print(f"{bone_name} rotation set to: {bone.rotation_euler}")  

    bpy.ops.object.mode_set(mode='OBJECT')  # Return to object mode after modifying the armature
    print("Armature location and rotation updated with random arm positions.")

def render_scene(config, table, workpiece, robot_armature_name, worker_armature_name, table_dimensions, workpiece_dimensions, output_dir, sphere=None):
    """
    Render the scene multiple times with different randomizations and save the outputs.

    Args:
    config: Configuration dictionary,
    workpiece: The workpiece object to be randomized.
    table: The table object where the workpiece is placed.
    table_dimensions: The dimensions of the table.
    workpiece_dimensions: The dimensions of the workpiece.
    sphere: The sphere object to visualize the robot's reach.
    robot_armature_name: Name of the robot object to be rendered.
    worker_armature_name: Name of the worker object to be rendered.

    """

    for i in range(config['num_images']):
        bproc.utility.reset_keyframes()  # Reset keyframes for each render to ensure a clean start.

        # Configure camera and lighting for each render iteration.
        configure_camera_and_lighting(table, table_dimensions, config)

        # Create a safety zone sphere to visualize the robot's reach
        if config['safetyzone']:
            # Remove existing spheres before creating a new one
            for obj in bpy.data.objects:
                if obj.name.startswith('SafetyZone'):
                    bpy.data.objects.remove(obj, do_unlink=True)
            sphere = create_sphere_at_location([0, 0, 0], diameter= config['safety_zone_radius'])
            sphere['category_id'] = config['category_ids']['SafetyZone']

        # Randomize object positions and updates for each render.
        randomize_workpiece_on_table(workpiece, table, table_dimensions, workpiece_dimensions)
        randomize_panda_armature_poses(robot_armature_name, table, table_dimensions, config, sphere)
        set_random_armature_transform_near_table(worker_armature_name, config)

        # Perform the rendering
        bproc.renderer.set_max_amount_of_samples(128)  # Set the number of samples for rendering: default:1024.

        data = bproc.renderer.render() 
        seg_data = bproc.renderer.render_segmap(map_by=["instance", "class", "name"], default_values={"category_id": 0, "class_label": 'background'}) # Render segmentation map

        # Save rendered images and segmentation maps
        bproc.writer.write_coco_annotations(
            output_dir= output_dir,
            instance_segmaps=seg_data["instance_segmaps"],
            instance_attribute_maps=seg_data["instance_attribute_maps"],
            colors=data["colors"],
            color_file_format="JPEG",
            jpg_quality=100,
            append_to_existing_output=True,
            file_prefix='image_',
            indent=2
        )

        if config['hdf5']:
            # Enable segmentation map and normals output for the HDF5 container
            bproc.renderer.enable_normals_output()
            # write the data to a .hdf5 container
            bproc.writer.write_hdf5(output_dir + "/hdf5", data, append_to_existing_output=True)

        print(f"Rendered and saved image {i+1}/{config['num_images']}") 

def assign_category_ids(category_dict):
    """
    Assigns category IDs to objects based on a dictionary mapping of object names to category IDs.

    Args:
        category_dict: Dictionary mapping object names to category IDs.
    """
    # Loop through all objects in the current Blender scene
    for obj in bpy.data.objects:
        if obj.name in category_dict:
            # Assign the category ID from the dictionary
            obj['category_id'] = category_dict[obj.name]
            print(f"Assigned category ID {obj['category_id']} to {obj.name}")

def main():
    """
    Main function to load configurations, scene, objects, and managing the rendering process.

    """

    # Get the base directory (where your script or config file is located)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(base_dir, CONFIG_FILE)

    # Load configuration settings from file.
    config = load_config(config_path)

    # Initialize BlenderProc.
    bproc.init()

    # set the camera resolution
    bproc.camera.set_resolution(config['img_width'], config['img_height'])

    # set the background color to grey
    bproc.renderer.set_world_background(config['bg_color_rgb'], 1)

    # Load paths from config and convert them to absolute paths
    scene_path = os.path.join(base_dir, config['scene_path'])
    panda_path = os.path.join(base_dir, config['panda_path'])
    worker_path = os.path.join(base_dir, config['worker_path'])
    output_dir = os.path.join(base_dir, config['output_dir'])

    # Load scene and objects from specified file paths.
    scene = bproc.loader.load_blend(path=scene_path)
    table = [obj for obj in scene if obj.get_name() == "Table"][0]
    workpiece = [obj for obj in scene if obj.get_name() == "workpiece"][0]
    robot = load_and_manipulate_objects_from_blend(panda_path)
    worker = load_and_manipulate_objects_from_blend(worker_path)

    # Extract armature names
    robot_armature_name = next((name for name, obj in robot.items() if obj.type == 'ARMATURE'), None)
    worker_armature_name = next((name for name, obj in worker.items() if obj.type == 'ARMATURE'), None)

    # Print details of all bones in the armature
    print_armature_bones(robot_armature_name)
    print_armature_bones(worker_armature_name)

    # Extract dimensions of the table and workpiece for randomization.
    table_obj = bpy.data.objects.get("Table")
    table_dimensions = tuple(table_obj.dimensions)
    workpiece_obj = bpy.data.objects.get("workpiece")
    workpiece_dimensions = tuple(workpiece_obj.dimensions)

    assign_category_ids(config['category_ids'])

    # Execute the rendering process.
    render_scene(config, table, workpiece, robot_armature_name, worker_armature_name, table_dimensions, workpiece_dimensions, output_dir)

if __name__ == "__main__":
    main()
