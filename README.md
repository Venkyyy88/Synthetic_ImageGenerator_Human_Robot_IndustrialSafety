# Synthetic Image Generator

> **Generate richly‑annotated synthetic datasets for industrial safety applications — fully scripted with Blender 3.5 + BlenderProc.**

---

## Table of Contents
1. [Overview](#overview)  
2. [Features](#features)  
3. [Directory Structure](#directory-structure)  
4. [Quick Start](#quick-start)  
5. [Configuration](#configuration)  
6. [Usage](#usage)  
7. [Code Architecture](#code-architecture)  
8. [Extending the Pipeline](#extending-the-pipeline)  
9. [Roadmap](#roadmap)  
10. [Contributing](#contributing)  
11. [License & Acknowledgements](#license--acknowledgements)

---

## Overview
`Image Generator` procedurally assembles 3‑D scenes containing a **Franka‑style Panda robot**, interchangeable **end‑effectors**, a **workpiece**, a **worktable**, and a **human worker**.  
The engine randomises object poses, camera placement, lighting, textures, and materials, then renders:

* High‑resolution **RGB images**
* **COCO‑style instance annotations** (JSON)
* Per‑pixel **HDF5 segmentation masks**

All assets are ready for downstream computer‑vision tasks such as safety‑zone monitoring or grasp‑pose estimation.

---

## Features
| Category | Capability |
|----------|------------|
| **Scene Generation** | Procedural placement of workpiece & robot; human worker pose control (IK) |
| **Robotic Arm** | URDF‑driven or native *.blend* kinematics; per‑axis limit sampling based on Franka Emika datasheet |
| **Safety** | Runtime visual safety sphere (configurable radius) attached to end‑effector |
| **Photorealism** | Randomised HDRI lighting, camera intrinsics/extrinsics, physically‑based materials |
| **Outputs** | RGB (JPEG / PNG), COCO JSON, HDF5 masks & normals |
| **Batch Mode** | One‑click dataset generation via `image_gen.bat` |

---

## Directory Structure
```
BlenderProc/
├── code/
│   ├── image_gen.py              # Main automation script (see Code Architecture)
│   ├── image_gen_config.yaml     # User‑configurable parameters (sample below)
│   ├── image_gen.bat             # Batch rendering helper (Windows)
│   └── output/                   # Auto‑generated images & annotations
│       ├── rgb/
│       ├── hdf5/
│       └── coco_annotations.json
├── resources/
│   └── Dataset/                  # 3‑D asset library
│       ├── scene.blend           # Static scene layout (table, lights, …)
│       ├── panda.blend           # Franka‑style robot arm
│       └── worker.blend          # Human worker mesh + armature
└── README.md                     # You are here 🚀
```

---

## Quick Start
### 1 — Install Dependencies (Windows)
```bash
# Blender 3.5 – required for BlenderProc ≥ 2.4
choco install blender --version 3.5.0   # or download manually

# BlenderProc (pip inside ANY Python ≥3.8)
pip install blenderproc
```

### 2 — Clone & Render
```bash
git clone <YOUR‑FORK‑URL>
cd image‑generator/blenderproc/code

# First render (writes to ./output/test_final)
blenderproc run image_gen.py --pipeline_config image_gen_config.yaml
```
If everything is configured correctly, the script will create one RGB image, its COCO annotation, and an HDF5 segmentation mask.

---

## Configuration
All runtime parameters live in **`code/image_gen_config.yaml`**. A fully‑annotated default file is available in the given path.

### Parameter Reference
| Key | Description |
|-----|-------------|
| `scene_path` / `panda_path` / `worker_path` | Relative or absolute paths to the *.blend* assets |
| `num_images` | Frames per execution |
| `camera_lens`, `img_width`, `img_height` | Camera intrinsics & output resolution |
| `light_energy`, `light_type` | Physically‑based lamp setup |
| `bg_color_rgb` | Background gradient — grey by default |
| `safety_zone_radius` | Radius (m) of translucent red sphere around Axis‑7 |
| `bones_to_randomize*` | Joint limits applied per render (rad) |
| `category_ids` | COCO class mapping written into JSON |  


---

## Usage
### Single Run
```bash
blenderproc run code/image_gen.py --pipeline_config code/image_gen_config.yaml
```

### Batch Rendering
```bash
# Render with different seeds / configs (Windows helper)
code\image_gen.bat
```

### Visualise Outputs
BlenderProc ships with two convenient CLI helpers for inspecting what you rendered:
```bash
# COCO overlay for image index 50
blenderproc vis coco -b code/output/test_final -i 50 -c coco_annotations.json

# Inspect segmentation HDF5
blenderproc vis hdf5 code/output/test_final/hdf5/69.hdf5
```

#### Sample Output Gallery
Below is a quick glance at what a single frame looks like after post‑processing.

<p align="center">
  <!-- RGB -->
  <img src="docs/images/rgb_sample.png" alt="RGB frame"   width="30%" />
  <!-- segmentation -->
  <img src="docs/images/segmap_sample.png" alt="Segmentation mask" width="30%" />
  <!-- bounding‑boxes -->
  <img src="docs/images/bbox_sample.png" alt="Bounding‑box overlay" width="30%" />
</p>

*Left → Right:* **RGB**, **Segmentation**, **Bounding Boxes**

---

## Code Architecture
| File | Responsibility |
|------|----------------|
| **image_gen.py** | End‑to‑end pipeline: load config → set up scene → randomise objects & bones → render → write outputs |
| `load_config()` | Safe YAML loader |
| `randomize_workpiece_on_table()` | Uniform xy pose + z offset based on mesh height |
| `randomize_panda_armature_poses()` | Applies per‑axis limits from `bones_to_randomize` and updates safety sphere |
| `set_random_armature_transform_near_table()` | Places worker mesh and calls `randomize_arm_positions()` |
| `configure_camera_and_lighting()` | Spherical shell sampler around table centroid; attaches area light |
| `render_scene()` | Iterates `num_images`, resets keyframes, triggers COCO + HDF5 writer |
| `assign_category_ids()` | Encodes `category_ids` onto every Blender object for COCO export |

The script is intentionally self‑contained—no add‑ons or external modules beyond BlenderProc.

---

## Extending the Pipeline
| Goal | How to |
|------|--------|
| **Add new end‑effectors** | Import your textured mesh into `panda.blend` or reference via `bproc.loader.load_blend()` and update `category_ids`. |
| **Physics collisions** | Inject collision checks in `utils/collision.py` (TODO) and call inside `randomize_*()` functions. |
| **Advanced worker animation** | Replace Euler sampling with IK constraints or BVH mocap; update `bones_to_randomize_worker`. |
| **Domain randomisation sweeps** | Wrap `blenderproc run` in a shell script to loop over YAML presets & seeds. |

---

## Roadmap
- [ ] IK‑based worker motion with strict joint limits  
- [ ] Real‑time collision avoidance (table ↔ robot ↔ worker)  
- [ ] Expanded material & texture randomisation library  
- [ ] Docker + CLI wrapper for headless cloud rendering  

Contributions and feature requests are welcome!

---

## Contributing
1. Fork 💫  
2. Create feature branch: `git checkout -b feat/awesome`  
3. Commit + push: `git commit -m "feat: add awesome" && git push`  
4. Open a Pull Request & tag a maintainer.

We enforce `pre‑commit`, `black`, and `ruff`—please ensure hooks pass before opening a PR.

---

## License & Acknowledgements

This project is released under the **MIT License**.  
Robotic arm & worker assets © TurboSquid — used with commercial licence.  
Blender® and BlenderProc™ are trademarks of their respective owners and are referenced here solely to describe compatibility.
