"""
Copyright 2017 NREL

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

from .Coordinate import Coordinate
import numpy as np
import pytest


def test_instantiation_with_xy():
    """
    object should be instatiated with x and y
    """
    assert Coordinate(1, 1) != None

def test_rotation():
    """
    Coordinate at 1,0 rotated 90 degrees should result in 0,1
    """
    coordinate = Coordinate(1, 0)
    coordinate.rotate_z(np.pi/2.0)
    assert pytest.approx(coordinate.xprime) == 0.0 and pytest.approx(coordinate.yprime) == 1.0
