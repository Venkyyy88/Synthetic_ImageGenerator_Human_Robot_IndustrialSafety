
import numpy as np

from src.main.Module import Module
from src.utility.BlenderUtility import get_all_mesh_objects, get_all_materials


class MaterialRandomizer(Module):
    """
    Randomizes the materials for the selected objects, the default is all.
    The amount of randomization depends on the randomization level (0 - 1).
    Randomization level => Expected fraction of objects for which the texture should be randomized.

    The selected objects will get materials, which can be selected by the materials_to_replace_with selector.
    The default is all materials. If this selection is empty an exception is thrown.

    **Configuration**:

    .. csv-table::
        :header: "Parameter", "Description"

        "randomization_level", "Level of randomization, greater the value greater the number of objects for which the
                               materials are randomized. Allowed values are [0-1], default: 0.2, Type: Float"
        "manipulated_objects", "Selector (getter.Object), to select all objects which materials should be changed,
                               by default: all"
        "materials_to_replace_with", "Selector (getter.Materials) a list of materials to use for the replacement
                                  by default: all"
        "mode", "Mode of operation. Available values: 'once_for_each' (sampling the material for each selected object "
              "anew), 'once_for_all' (sampling once for all of the selected objects). Optional. Default value: "
              "'once_for_each'. Type: string."
    """

    def __init__(self, config):
        Module.__init__(self, config)
        self.randomization_level = 0
        self._objects_to_manipulate = []
        self._materials_to_replace_with = []

    def run(self):
        """
            Walks over all objects and randomly switches the materials with the materials_to_replace_with
        """
        self.randomization_level = self.config.get_float("randomization_level", 0.2)
        self._objects_to_manipulate = self.config.get_list('manipulated_objects', get_all_mesh_objects())
        self._materials_to_replace_with = self.config.get_list("materials_to_replace_with", get_all_materials())
        op_mode = self.config.get_string("mode", "once_for_each")

        # if there were no materials selected throw an exception
        if not self._materials_to_replace_with:
            raise Exception("There were no materials selected!")

        if op_mode == "once_for_all":
            random_material = np.random.choice(self._materials_to_replace_with)

        # walk over all objects
        for obj in self._objects_to_manipulate:
            if hasattr(obj, 'material_slots'):
                # walk over all materials
                for material in obj.material_slots:
                    if np.random.uniform(0, 1) <= self.randomization_level:
                        if op_mode == "once_for_each":
                            random_material = np.random.choice(self._materials_to_replace_with)
                        # select a random material to replace the old one with
                        material.material = random_material
