import bpy

from src.main.Module import Module


class Loader(Module):
    """
    **Configuration**:

    .. csv-table::
       :header: "Parameter", "Description"
       "add_properties", "Custom properties to set for loaded objects. Use 'cp_' prefix for keys. Type: dict."
       "cf_set_shading", "Custom function to set the shading of the loaded objects."
                         "Type: str. Available: ["FLAT", "SMOOTH"]"
    """
    def __init__(self, config):
        Module.__init__(self, config)

    def _set_properties(self, objects: [bpy.types.Object]):
        """ Sets all custom properties of all given objects according to the configuration.

        Also runs all custom property functions.

        :parameter objects: A list of objects which should receive the custom properties. Type: [bpy.types.Object]
        """

        properties = self.config.get_raw_dict("add_properties", {})

        for obj in objects:
            for key, value in properties.items():
                if key.startswith("cp_"):
                    key = key[3:]
                    obj[key] = value
                else:
                    raise RuntimeError("Loader modules support setting only custom properties. Use 'cp_' prefix for keys. "
                                       "Use manipulators.Entity for setting object's attribute values.")
        if self.config.has_param("cf_set_shading"):
            mode = self.config.get_string("cf_set_shading")
            Loader.change_shading_mode(objects, mode)

    @staticmethod
    def change_shading_mode(objects: [bpy.types.Object], mode: str):
        """
        Changes the shading mode of all objects to either flat or smooth. All surfaces of that object are changed.

        :parameter objects: A list of objects which should receive the custom properties. Type: [bpy.types.Object]
        :param mode: Desired mode of the shading. Available: ["FLAT", "SMOOTH"]. Type: str
        """
        if mode.lower() == "flat":
            is_smooth = False
        elif mode.lower() == "smooth":
            is_smooth = True
        else:
            raise Exception("This shading mode is unknown: {}".format(mode))

        for obj in objects:
            for face in obj.data.polygons:
                face.use_smooth = is_smooth
