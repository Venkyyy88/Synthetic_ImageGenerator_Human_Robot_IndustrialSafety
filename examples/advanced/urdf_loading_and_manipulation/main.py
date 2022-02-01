import blenderproc as bproc
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('urdf_file', nargs='?', default="./model.urdf", help="Path to the .urdf file")
parser.add_argument('output_dir', nargs='?', default="examples/advanced/urdf_loading_and_manipulation/output", help="Path to where the final files will be saved")
args = parser.parse_args()

bproc.init()

robot = bproc.loader.load_urdf(urdf_file=args.urdf_file)

robot.hide_irrelevant_objs()
robot.remove_link_by_index(index=0)
robot.set_ascending_category_ids()

# rotate every joint for 0.1 radians relative to the previous position
robot.set_rotation_euler_fk(link=None, rotation_euler=0.2, mode='relative', frame=0)
robot.set_rotation_euler_fk(link=None, rotation_euler=0.2, mode='relative', frame=1)
robot.set_rotation_euler_fk(link=None, rotation_euler=0.2, mode='relative', frame=2)

# rotate the fourth joint to its original position
robot.set_rotation_euler_fk(link=robot.links[4], rotation_euler=0., mode='absolute', frame=3)

# for moving to a specified 6d pose, first set up an inverse kinematic link at the end-effector
# as relative location we put a small offset to the end effector
# this allows us to later make it rotate around a point which could be a gripper
robot.create_ik_bone_controller(link=robot.links[-1], relative_location=[0., 0., 0.2])
robot.set_location_ik(location=[0., 0., 0.8], frame=4)
robot.set_rotation_euler_ik(rotation_euler=[-1.57, 1.57, 0.], mode='absolute', frame=4)

# we can also check if the desired pose is reachable by the robot
if robot.has_reached_ik_pose(location_error=0.01, rotation_error=0.01):
    print("Robot has reached pose!")

# rotate around the pose
for i in range(5, 10):
    robot.set_rotation_euler_ik(rotation_euler=[0., 0., 0.4], mode='relative', frame=i)

# print current joint poses
print("Current joint poses:", robot.get_all_local2world_mats())
print("Current visual poses:", robot.get_all_visual_local2world_mats())

# set a light source
light = bproc.types.Light()
light.set_type(type="POINT")
light.set_location(location=[5, 5, 5])
light.set_energy(energy=1000)

# sample camera pose
bproc.camera.set_intrinsics_from_blender_params(640, 480)
location = [1., 2., 2.]
poi = bproc.object.compute_poi(robot.links[4].get_visuals())
# Compute rotation based on vector going from location towards poi
rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot=3.14)
# Add homog cam pose based on location and rotation
cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
bproc.camera.add_camera_pose(cam2world_matrix)
# render RGB images
data = bproc.renderer.render()

# render segmentation images
data.update(bproc.renderer.render_segmap(use_alpha_channel=True))

# write the data to a .hdf5 container
bproc.writer.write_hdf5(args.output_dir, data)
