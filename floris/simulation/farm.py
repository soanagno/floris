# Copyright 2019 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from ..utilities import Vec3
from .wake_combination import WakeCombination
from .flow_field import FlowField
from .turbine_map import TurbineMap
import copy
import numpy as np


class Farm():
    """
    Farm is the container class of the FLORIS package. It brings together all
    of the component objects after input (i.e., Turbine, Wake, FlowField) and
    packages everything into the appropriate data type. Farm should also be used
    as an entry point to probe objects for generating output.

    Parameters:
        instance_dictionary: A dictionary as generated from the input_reader;
            it should have the following key-value pairs:
                {
                    **description**: A string containing a description of the wind farm.

                    **properties**: A dictionary containing the following key-value pairs:
                        {
                            **wind_speed**: A float that is the wind speed at hub height (m/s).

                            **wind_direction**: A float that is the wind direction (deg).

                            **turbulence_intensity**: A float that is the turbulence intensity (expressed as a decimal fraction).

                            **wind_shear**: A float that is the power law wind shear exponent.

                            **wind_veer**: A float that is the vertical change in wind direction across the rotor.

                            **air_density**: A float that is the air density (kg/m^3).

                            **layout_x**: A list that contains the x coordinates of the turbines.

                            **layout_y**: A list that contains the y coordinates of the turbines.
                        }
                }
        turbine: The Turbine object used in Farm.
        wake: The Wake object used in Farm.

    Returns:
        An instantiated Farm object.
    """

    def __init__(self, instance_dictionary, turbine, wake):
        self.description = instance_dictionary["description"]
        properties = instance_dictionary["properties"]
        layout_x = properties["layout_x"]
        layout_y = properties["layout_y"]
        self.wake = wake

        self.flow_field = FlowField(
            wind_speed=properties["wind_speed"],
            wind_direction=properties["wind_direction"],
            wind_shear=properties["wind_shear"],
            wind_veer=properties["wind_veer"],
            turbulence_intensity=properties["turbulence_intensity"],
            air_density=properties["air_density"],
            turbine_map=TurbineMap(
                layout_x,
                layout_y,
                [copy.deepcopy(turbine) for ii in range(len(layout_x))]),
            wake=wake
        )

    def __str__(self):
        return \
            "Description: {}\n".format(self.description) + \
            "Wake Model: {}\n".format(self.flow_field.wake.velocity_model) + \
            "Deflection Model: {}\n".format(self.flow_field.wake.deflection_model)

    def set_wake_model(self, wake_model):
        """
        This method sets the wake model used.

        Parameters:
            wake_model: A string containing the wake model used to calculate the wake; Valid wake model 
                options are: "curl", "gauss", "jensen", and "floris".

        Returns:
            *None* -- The wake model and flow field are updated in the :py:obj:`floris.simulation.flow_field` object.
        """

        valid_wake_models = ['curl', 'gauss', 'jensen', 'floris']
        if wake_model not in valid_wake_models:
            raise Exception("Invalid wake model. Valid options include: {}.".format(", ".join(valid_wake_models)))

        if wake_model == 'jensen':
            self.flow_field.wake.velocity_model = 'jensen'
            self.flow_field.wake.deflection_model = 'jimenez'
        elif wake_model == 'floris':
            self.flow_field.wake.velocity_model = 'floris'
            self.flow_field.wake.deflection_model = 'floris'
        elif wake_model == 'gauss':
            self.flow_field.wake.velocity_model = 'gauss'
            self.flow_field.wake.deflection_model = 'gauss_deflection'
        elif wake_model == 'curl':
            self.flow_field.wake.velocity_model = 'curl'
            self.flow_field.wake.deflection_model = 'curl'

        self.flow_field.reinitialize_flow_field(with_resolution=self.flow_field.wake.velocity_model.model_grid_resolution)


    def set_yaw_angles(self, yaw_angles):
        """
        This method sets yaw angles for all turbines and optionally calculates the new wake velocities 
        and updates them in the flow field.

        Parameters:
            yaw_angles: A list of floats containing a constant yaw angle for all turbines or list of unique yaw angles 
                for each turbine in degrees.
            
        Returns:
            *None* -- The turbines are updated directly and the flow field is updated in the 
            :py:obj:`floris.simulation.flow_field` object.
        """
        if isinstance(yaw_angles, float) or isinstance(yaw_angles, int):
            yaw_angles = [yaw_angles] * len(self.turbines)

        for yaw_angle, turbine in zip(yaw_angles, self.turbines):
            turbine.yaw_angle = yaw_angle


    # Getters & Setters
    @property
    def wind_speed(self):
        """
        This method returns the wind speed for the wind farm.

        Returns:
            A float that is the current wind speed in the wind farm in m/s.
        """
        return self.flow_field.wind_speed


    @property
    def wind_direction(self):
        """
        This method returns the wind direction for the wind farm.

        Returns:
            A float that is the current wind direction in the wind farm in degrees.
        """
        return self.flow_field.wind_direction


    @property
    def wind_shear(self):
        """
        This method returns the wind shear power law exponent for the wind farm.

        Returns:
            A float that is the current wind shear power law exponent in the wind farm.
        """
        return self.flow_field.wind_shear


    @property
    def wind_veer(self):
        """
        This method returns the wind veer -- the vertical change in wind direction across the rotor.

        Returns:
            A float that is the current vertical change in wind direction across the rotor in degrees.
        """
        return self.flow_field.wind_veer


    @property
    def turbulence_intensity(self):
        """
        This method returns the turbulence intensity for the wind farm.

        Returns:
            A float that is the current turbulence intensity expressed as a decimal fraction.
        """
        return self.flow_field.turbulence_intensity


    @property
    def air_density(self):
        """
        This method returns the air density for the wind farm.

        Returns:
            A float that is the current air density in kg/m^3.
        """
        return self.flow_field.air_density


    @property
    def turbine_map(self):
        """
        This method returns the turbine map property of the :py:obj:`floris.simulation.flow_field` object associated with the wind farm.

        Returns:
            A :py:obj:`floris.simulation.turbine_map` object that holds turbine information for the farm.
        """
        return self.flow_field.turbine_map
    

    @property
    def turbines(self):
        """
        This method returns the list of :py:obj:`floris.simulation.turbine` objects contained in 
        the :py:obj:`floris.simulation.turbine_map` object.

        Returns:
            A list of :py:obj:`floris.simulation.turbine` objects that hold the turbine information for the wind farm.
        """
        return self.turbine_map.turbines
