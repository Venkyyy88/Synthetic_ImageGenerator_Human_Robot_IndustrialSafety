
# Planned Features

- Add support for YCB objects (not just Bob)
- Add support for more object datasets (ideas are welcomed, just open an issue with a dataset you want to see integrated)
- Improve the documentation 

# Version History

## Version 1.4.0: 15th May 2020

- added the NormalRenderer functions to the RGBRenderer saves a render call, when generating normal images
- added a script to automatically download all PBR assest from [https://cc0textures.com/](https://cc0textures.com/)
- add CCMaterialLoader can load all downloaded materials from cc0textures, to randomly replace them later
- add support for ShapeNet
- add support for SceneNet, including the lighting, which is modeled after the SUNCG lighting module.
- massive docu improvements, added a type to all config values and a default value if one is there
- added examples for: 
  - bop_object_physics_positioning
  - bop_object_pose_sampling
  - bop_scene_replication
  - on_surface_object_sampling
  - scenenet
  - scenenet_with_cctextures
  - shapenet
  - shapenet_with_scenenet
  - shapenet_with_suncg
  - suncg_with_improved_mat
- added object OnSurfaceSampler (similiar to the phyiscs but faster and places object only on the bb)
- added WorldManipulator (can change custom properties of the world, like the category_id)
- switched to config version 3.0 
  - global initialized values are now in the main.Initializer
  - added a GlobalStorage to save variables over module boundaries
- add VisNormalImage for debugging mode, which visualizes a depth & normal image in blender 
- material selectors now also support AND and OR conditions
- add automatic detection of optix graphics cards
- added a min interest score for the CameraSampler
- added a novelty pose checker for the CameraSampler, to avoid clustering of camera poses
- global config values are now not longer added to the modules config, only in the event that there is no module found the global config is checked
- rename SUNCG materials to the textures they load, makes selecting them easier
- SUNCG materials are now shared over objects, if they share the same properties, also true for lights
- rewrite of MaterialRandomizer to make use of the new cc0textures
- added a Bop Writer to write out the current scene config in the BOP format
- add the solidify modifier to the options of the EntityManipulator
- add a PartSphere sampler to e.g. only sample in the upper half of a sphere
- add a script to download scenenet to make the use of it even easier
- add easy option to change specular values for materials with the MaterialManipulator
- added the option to make runs deterministic by introducing a env variable: `BLENDER_PROC_RANDOM_SEED`
- added a Basic Color Sampler
- improved the capabilities of the DiscSampler
- now all custom properties should be accessed in the config via: "cp_..." for custom functions: "cf_"
- add texture support for ycbv objects in the BopLoader

## Version 1.3.0: 25th March 2020
- added Optical Flow Renderer 
- added Stereo Global Matching Renderer (SGM) -> which takes two color images and produces "non-perfect" depth images
- added option for SGM to also write disparities
- added a new material manipulator 
- added a material getter to select materials based on certain conditions
- combined BOP with this repo -> now the only difference is the readme
- added contribution guidelines -> which include commit message guidelines and branch name guidelines and much more
- matrices can now be read via the config file
- added a cached options to the import objects
- added request custom property for the entity getter (to ensure that a custom property is changed)
- added ReplaceObject
- added option that in debugging the RgbRenderer get executed except for the actual rendering part all others are executed and then undon
- added collision mesh source to the physics module
- added option to coco annotations to append the output to an existing coco file
- added bounding box selection to getter.Entity and also just axis aligned hyper plane checks
- added a 1D sampler for float/int/bool
- added postprocessing to the example to reduce the amount of channels in the depth image
- added visualization for stereo and optical flow
- added an oil filter for the SGM result
- added a path sampler
- added a blender collection loader
- added the RockEssentialLoader based on the RockEssential dataset
- added index to getter.Entity to request only a certain element of the selection
- fix three bugs in the physics module, where the mass_scaling was always used and the location not properly updated
- fixed a bug where color images where wrongly saved in float now back to uint8
- fixed a bug in the coco annotations writer + adapting of the example
- fixed bug in load_image, where the dimensions where switched
- fixed a bug when "home_local" is not available than "home" is used
- fixed bug where run.py can only be run from the main folder
- fixed pypng version in bop example
- fixed bug where the volume calculation for bounding boxes did not work as expected
- refactored the disc sampler 
- cleaned up all readmes


## Version 1.2.0: 31th January 2020

- added more detailed examples to most of the important modules
- adapt CoCo annotation tools to newer Version of SegMapRenderer
- background class is now zero when doing instance segmentation
- renamed getter.Object to getter.Entity, same for ObjectManipulator is now named EntityManipulator
- entity conditions do now work with AND and OR connections
- strings are now matched with fullmatch instead of search in entity conditions
- conditions now support bool custom properties
- material randomizer now supports getter.entity providers
- added UpperRegionSampler, which can sample on the up surface of the bounding box of an object
- scripts now support execution with python3.x
- physics are now saved with bool instead of active and passive
- physics options for simulator added
- remove version number -> only blender version 2.81 supported
- the ObjectLoader can now load several objects at once and set their properties with `"add_properties"`
- moved more functionality in the camera sampler instead of having in specific sampler to make writing a new one easier
- added a SO3 Sampler for rotation sampling
- change the "name" of modules in the config to "module" and "provider" depending on the case
- added MacOS support (but only for CPUs, GPU support on MacOS is not available)
- added this changelog
- fixes:
  - fixed a problem that the check_bb_intersection did not work right in all cases (Bounding box check)
  - fixed a problem with the check_intersection fct., where the reference coordinate system was not always right.
  - fixed a bug with the SUNCG lighting in RGB images

## Version 1.1.0: 16th January 2020

- Added provider, which can be executed inside of different modules, examples:
    - Samplers of values
    - Getters of objects, specified on one condition (for example the name)
- Added object manipulators, these can change selected objects attributes and custom properties
- Added physics positioning, objects can be either "active" or "passive" and then interact with each other
- Added ObjectPoseSampler sampled collision free poses of all objects
- Added one ObjectLoader, which deals with all kinds of objects
- Added a camera object sampler to sample cameras and objects at the same time
- Redone the SegMapRenderer to fix bug in instance and class segmentation
- Added coco annotations writer
- Added version number to config files
- Added more documentation 
- Added more examples

## Version 1.0.0: 25th October 2019

- Added Pipeline, Modules and Config
- Added CameraModules, with different sampler for SUNCG and replica 
- Added LightModules, with different samplers also for SUNCG
- Added Loader for objects
- Added Loader for replica and SUNCG
- Added Hdf5 Writer
- Added camera-, light-, object state writer
- Added MaterialRandomizer
- Added Shell-, Sphere- and Uniform3DSampler
- Added debug script

