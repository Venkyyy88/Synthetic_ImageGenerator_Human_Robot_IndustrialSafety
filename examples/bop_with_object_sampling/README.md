# BOP with object sampling

![](rendering.png)

This example presents some advanced BlenderProc features used for BOP data integration, namely object sampling, material and object manipulation, material randomization, etc.

## Usage

Execute in the Blender-Pipeline main directory:

```
python run.py examples/bop_with_object_sampling/config.yaml <path_to_bop_data> <path_to_bop_toolkit> <path_to_cc_textures> examples/bop_with_object_sampling/output
``` 

* `examples/bop_with_object_sampling/config.yaml`: path to the pipeline configuration file.
* `<path_to_bop_data>`: path to a folder containing BOP datasets.
* `<path_to_bop_toolkit>`: path to a bop_toolkit folder.
* `examples/bop_with_object_sampling/output`: path to an output folder.

## Visualization

Visualize the generated data if it is stored in a container.

```
python scripts/visHdf5Files.py examples/bop_with_object_sampling/output/coco_data/0.hdf5
```

## Steps

* Load T-LESS BOP models: `loader.BopLoader` module.
* Load ITODD BOP models: `loader.BopLoader` module.
* Load LM BOP models: `loader.BopLoader` module.
* Sample color for T-LESS and ITODD models: `materials.MaterialManipulator` module.
* Sample roughness and specular values for LM models: `materials.MaterialManipulator` module.
* Initialize two mesh planes: `constructor.BasicMeshInitializer` module.
* Set custom properties for those planes: `manipulators.EntityManipulator` module.
* Switch to an emission shader for one of those plane: `materials.MaterialManipulator` module.
* Load CCTexture materials: `loader.CCMaterialLoader` module.
* Sample a material for a second plane: `materials.MaterialRandomizer` module.
* Sample objects poses: `object.ObjectPoseSampler` module.
* Perform physics animation: `object.PhysicsPositioning` module.
* Sample light source pose: `lighting.LightSampler` module.
* Sample camera poses: `camera.CameraSampler` module.
* Render RGB: `renderer.RgbRenderer` module.
* Render segmentation: `renderer.SegMapRenderer` module.
* Write COCO annotations: `writer.CocoAnnotationsWriter` module.
* Write object states: `writer.ObjectStateWriter` module.
* Write output to .hdf5 container: `writer.Hdf5Writer` module.
* Write BOP data: `writer.BopWriter` module.

## Config file

### BOP Loader

```yaml
    {
      "module": "loader.BopLoader",
      "config": {
        "bop_dataset_path": "<args:0>/tless",
        "model_type": "cad",
        "mm2m": True,
        "sample_objects": True,
        "amount_to_sample": 2,
        "add_properties": {
          "cp_physics": True
        }
      }
    },
    {
      "module": "loader.BopLoader",
      "config": {
        "bop_dataset_path": "<args:0>/itodd",
        "model_type": "",
        "mm2m": True,
        "sample_objects": True,
        "amount_to_sample": 2,
        "add_properties": {
          "cp_physics": True
        }
      }
    },
    {
      "module": "loader.BopLoader",
      "config": {
        "bop_dataset_path": "<args:0>/lm",
        "split": "val",
        "mm2m": True,
        "model_type": "",
        "sample_objects": True,
        "amount_to_sample": 8,
        "obj_instances_limit": 1,
        "add_properties": {
          "cp_physics": True
        }
      }
    },
```

* Here we are sampling BOP objects from 3 different datasets.
* We load 2 random object for T-LESS and ITODD datasets, and 8 objects from LM dataset.
* Note `"obj_instances_limit": 1` parameter for LM data which dictates that each sampled object from this dataset must be unique in this scene, while this parameter is omitted for T-LESS and ITODD, which means that potentially those objects may have duplicates due to the process of sampling.

### Material Manipulator

```yaml
    {
      "module": "materials.MaterialManipulator",
      "config": {
        "selector": {
          "provider": "getter.Material",
          "conditions": [
          {
            "name": "bop_itodd_vertex_col_material.*"
          },
          {
            "name": "bop_tless_vertex_col_material.*"
          }
          ]
        },
        "cf_set_base_color": {
          "provider": "sampler.Color",
          "grey": True,
          "min": [0.25, 0.25, 0.25, 1],
          "max": [1, 1, 1, 1]
        }
      }
    },
    {
      "module": "materials.MaterialManipulator",
      "config": {
        "selector": {
          "provider": "getter.Material",
          "conditions": [
          {
            "name": "bop_itodd_vertex_col_material.*"
          },
          {
            "name": "bop_tless_vertex_col_material.*"
          },
          {
            "name": "bop_lm_vertex_col_material.*"
          }
          ]
        },
        "cf_set_specular": {
          "provider": "sampler.Value",
          "type": "float",
          "min": 0.1,
          "max": 1
        },
        "cf_set_roughness": {
          "provider": "sampler.Value",
          "type": "float",
          "min": 0.1,
          "max": 1
        }
      }
    },
```

* Sample RGBA color for T-LESS and ITODD object's materials using `sampler.Color` Provider.
* Sample `specular` and `roughness` values for object's materials from all datasets using `sampler.Value` Provider.

```yaml
    {
      "module": "materials.MaterialManipulator",
      "config": {
        "selector": {
          "provider": "getter.Material",
          "conditions": {
            "name": "light_plane_material"
          }
        },
        "cf_switch_to_emission_shader": {
          "color": {
            "provider": "sampler.Color",
            "min": [0, 0, 0, 1],
            "max": [1, 1, 1, 1]
          },
          "strength": {
            "provider": "sampler.Value",
            "type": "float",
            "min": 5,
            "max": 10
          }
        }
      }
    },
```

### CC Textures

```yaml
    {
      "module": "loader.CCMaterialLoader",
      "config": {
        "folder_path": "<args:2>"
      }
    }
```
* Use the [script](../../scripts/download_cc_textures.py) to download the textures. Default [path](../../resources), pass it to the Loader.

### Material Randomizer
* For a default material of a light plane which was created during object's initialization, switch to a Emission shader and sample `color` and `strength` values of the emitted light.

```yaml
    {
      "module": "materials.MaterialRandomizer",
      "config": {
        "randomization_level": 1,
        "manipulated_objects": {
          "provider": "getter.Entity",
          "conditions": {
            "name": "ground_plane"
          }
        },
        "materials_to_replace_with": {
          "provider": "getter.Material",
          "conditions": {
            "cp_is_cc_texture": True
          }
        }
      }
    },
```

* For a default material of a ground plane which was created during object's initialization, sample a material from loaded previously CCTextures materials.

### Camera Sampler

```yaml
    {
      "module": "camera.CameraSampler",
      "config": {
        "cam_poses": [
        {
          "number_of_samples": 3,
          "location": {
            "provider": "sampler.Shell",
            "center": [0, 0, 0],
            "radius_min": 0.7,
            "radius_max": 1.3,
            "elevation_min": 25,
            "elevation_max": 89.9
          },
          "rotation": {
            "format": "look_at",
            "value": {
              "provider": "getter.Attribute",
              "entities": {
                "provider": "getter.Entity",
                "conditions": {
                  "cp_model_path": ".*/lm/.*"
                }
              },
              "index": 0,
              "get": "location"
            }
          }
        }
        ]
      }
    },
```

* Sample 3 camera poses, where camera's location is sampled using `sampler.Shell` Provider, and camera's rotation is based on the output of the `getter.Attribute` Provider.
* `getter.Attribute` Provider returns a `location` (`"get": "location"`) of the first (`"index": 0`) LM dataset (`"cp_model_path": ".*/lm/.*"`) object that has Z-axis location coordinate bigger than 0 (`"cf_inside": {"z_min": 0}`), which ensures, that it did not fall off the ground plane during physics animation.

## More examples

* [bop_sampling](../bop_sampling): Sample BOP object and camera poses.
* [bop_scene_replication](../bop_scene_replication): Replicate the scenes and cameras from BOP datasets in simulation.
