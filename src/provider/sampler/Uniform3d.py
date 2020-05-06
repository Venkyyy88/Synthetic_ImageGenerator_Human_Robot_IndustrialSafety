import mathutils
import random

from src.main.Provider import Provider

class Uniform3d(Provider):
    """ Uniformly samples a 3-dimensional vector.

        Example 1: Return a uniform;y sampled 3d vector from a range [min, max].

        {
          "provider": "sampler.Uniform3d",
          "max": [0.5, 0.5, 0.5],
          "min": [-0.5, -0.5, -0.5]
        }

    **Configuration**:

    .. csv-table::
        :header: "Parameter", "Description"

        "min", "A list of three values, describing the minimum values of 1st, 2nd, and 3rd dimensions. Type: list."
        "max", "A list of three values, describing the maximum values of 1st, 2nd, and 3rd dimensions. Type: list."
    """

    def __init__(self, config):
        Provider.__init__(self, config)

    def run(self):
        """
        :return: Sampled value. Type: Mathutils Vector
        """
        # minimum values vector
        min = self.config.get_vector3d("min")
        # maximum values vector
        max = self.config.get_vector3d("max")

        position = mathutils.Vector()
        for i in range(3):
            position[i] = random.uniform(min[i], max[i])

        return position
