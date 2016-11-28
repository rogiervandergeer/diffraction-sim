from collections import namedtuple
from pandas import read_csv

DEFINITION_KEYS = {
    'block_id': int, 
    'plate_dimension': int, 'plate_diameter': float,
    'plate_x': float, 'plate_y': float, 'plate_z': float,
    'sensor_dimension': int, 'sensor_diameter': float,
    'sensor_x': float, 'sensor_y': float, 'sensor_z': float,
    'wavelength': float,
    'inner_radius': float, 'outer_radius': float
}

definition = namedtuple('def', DEFINITION_KEYS.keys())

def read_definitions(file_name):
    df = read_csv(file_name, 
                  names=DEFINITION_KEYS.values(), 
                  dtypes=DEFINITION_KEYS)

class Definition():

    def __init__(self, 
                 block_id,
                 plate,
                 sensor,
                 wavelength,
                 plate_def):
        self.block_id = block_id
        self.plate = plate
        self.sensor = sensor
        self.wavelength = wavelength
        self.plate_def = plate_def

