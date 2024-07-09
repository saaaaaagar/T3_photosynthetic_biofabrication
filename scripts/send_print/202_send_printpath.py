#standard imports
import os
import json
import sys
#import compas geometry dependencies
from compas.geometry import Frame, Vector, Point, Transformation, Translation
import compas


#import rtde wrapper from current directory
path = os.path.dirname(__file__)
rtde_path = os.path.join(os.path.dirname(path), 'scripts')
sys.path.append(rtde_path)

import rtde_wrapper as rtde

#########################################################
# # Define constant parameters
# MAX_SPEED = 200.00 #mm/s float
# MAX_ACCEL = 100.00 #mm/s2 float

IP_ADDRESS = "192.168.10.10" #string with IP Address
##########################################################

# Define location of print data
# change .json file path and name as required
DATA_OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
PRINT_FILE_NAME = 'non_planar_60x240_3grapghs.json'

# Open print data
with open(os.path.join(DATA_OUTPUT_FOLDER, PRINT_FILE_NAME), 'r') as file:
    data = compas.json_load(file)

print('Print data loaded :', os.path.join(DATA_OUTPUT_FOLDER, PRINT_FILE_NAME))



# def remap(val, old_min, old_max, min, max):
#     #remap a number from a given range to another range
#     return (max - min)*(val - old_min) / (old_max - old_min) + min



####################################################################
# Define print data containers as empty lists
frames = []
velocities = []
radii = []
toggles = []
accelerations = []

# Go through JSON and copy data to lists
for item in data:
    # Read frame data
    # point = item['point']
    # frame = Frame(point, Vector.Xaxis(), Vector.Yaxis())
    frame = item['frame']
    frames.append(frame)
    velocities.append(item['velocity'])

    # Define accelerations
    for v in velocities:
        acceleration = v/4
        accelerations.append(acceleration)

    radii.append(item['blend'])
    toggles.append(item['toggle'])


#######################################################################


# Use the data to execute the printpath
if __name__ == "__main__":
    # Create base frame with measured points
    ORIGIN = Point(522.36, 499.27, -9.73)
    XAXIS_PT = Point(136.35, 519.50, -9.33)
    YAXIS_PT = Point(505.56, -80.00, -10.31)
    #Create a compas Frame
    base_frame = Frame.from_points(ORIGIN, XAXIS_PT, YAXIS_PT)

    # Transform all frames from slicing location to robot coordinate system
    T =  Transformation.from_frame_to_frame(Frame.worldXY(), base_frame)
    frames = [f.transformed(T) for f in frames]

    # Move frames by a Z fine tuning parameter as required
    Z_OFFSET = 0.50
    T =  Translation.from_vector([0,0,Z_OFFSET])
    frames = [f.transformed(T) for f in frames]


    # Send all points using send_printpath function implemented in the RTDE Wrapper
    tcp = [41.47/1000, 50.63/1000, 190.91/1000,0.0,3.1416,0.0]
    rtde.set_tcp_offset(tcp, ip=IP_ADDRESS)
    rtde.send_printpath(frames, velocities, accelerations , radii, toggles, ip=IP_ADDRESS)
