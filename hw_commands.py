####################################################################################
#                                                                                  #
# hw_commands.py -- module with general command line functions with hardware       #
#                   oriented functionality                                         #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 12/18/2022                                                                 #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################

# Standard imports
import sys
import os
import time
import datetime
import numpy                    as np
from   matplotlib import pyplot as plt
import struct

# Project imports
import sensor_conv
import commands
from   config      import *
from   controller  import *


####################################################################################
# Global Variables                                                                 #
####################################################################################

# Run config
if ( zav_debug ):
    default_timeout = 100 # 100 second timeout
else:
    default_timeout = 1   # 1 second timeout


####################################################################################
# Shared Procedures                                                                #
####################################################################################




####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_raw_sensor_readouts                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Converts an array of bytes into a dictionary containing the raw sensor   #
#       readouts in integer format                                                 #
#                                                                                  #
####################################################################################
def get_raw_sensor_readouts( controller, sensors, sensor_bytes ):

    # Sensor readout sizes
    sensor_size_dict = sensor_sizes[controller]

    # Starting index of bytes corresponding to individual 
    # sensor readout in sensor_bytes array
    index = 0

    # Result
    readouts = {}
    
    # Convert each sensor readout 
    for sensor in sensors:
        size             = sensor_size_dict[sensor]
        readout_bytes    = sensor_bytes[index:index+size]
        if ( sensor_formats[controller][sensor] == float ):
            sensor_val = byte_array_to_float( readout_bytes )
        else:
            sensor_val = byte_array_to_int(   readout_bytes )
        readouts[sensor] = sensor_val
        index           += size 

    return readouts
# get_raw_sensor_readouts #


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         conv_raw_sensor_readouts                                                 #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Converts raw sensor readouts in integer format into the appropriate      # 
#         format                                                                   #
#                                                                                  #
####################################################################################
def conv_raw_sensor_readouts( controller, raw_readouts ):

    # Conversion functions
    conv_funcs = sensor_conv_funcs[controller]

    # Result
    readouts = {}

    # Convert each readout
    for sensor in raw_readouts:
        if ( conv_funcs[sensor] != None ):
            readouts[sensor] = conv_funcs[sensor]( raw_readouts[sensor] )
        else:
            readouts[sensor] = raw_readouts[sensor]
    
    return readouts
## conv_raw_sensor_readouts ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_sensor_readouts                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Converts a byte array into sensor readouts and converts digital readout  #
#                                                                                  #
####################################################################################
def get_sensor_readouts( controller, sensors, sensor_bytes ):

    # Convert to integer form
    int_readouts = get_raw_sensor_readouts( controller, sensors, sensor_bytes )

    # Make conversions
    readouts     = conv_raw_sensor_readouts( controller, int_readouts )
    return readouts
## get_sensor_readouts ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_sensor_frame_bytes                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
#        Obtains a frame of sensor data from a controller's flash in byte format   #
#                                                                                  #
####################################################################################
def get_sensor_frame_bytes( zavDevice ):

    # Determine the size of the frame
    frame_size = sensor_frame_sizes[zavDevice.controller]

    # Get bytes
    rx_bytes = zavDevice.readBytes( frame_size )
    return rx_bytes
## get_sensor_frame_bytes ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_sensor_frame                                                         #
#                                                                                  #
# DESCRIPTION:                                                                     #
#        Converts a list of sensor frames into measurements                        #
#                                                                                  #
####################################################################################
def get_sensor_frames( controller, sensor_frames_bytes, format = 'converted' ):

    # Convert to integer format
    sensor_frames_int = []
    for frame in sensor_frames_bytes:
        sensor_frame_int = []
        for sensor_byte in frame:
            sensor_frame_int.append( ord( sensor_byte ) )
        sensor_frames_int.append( sensor_frame_int )

    # Combine bytes from integer data and convert
    if ( format == 'converted'):
        sensor_frames = []
        for int_frame in sensor_frames_int:
            sensor_frame = []
            # Time of frame measurement
            time = ( ( int_frame[0]       ) + 
                     ( int_frame[1] << 8  ) + 
                     ( int_frame[2] << 16 ) +
                     ( int_frame[3] << 24 ) )
            # Conversion to seconds
            sensor_frame.append( sensor_conv.time_millis_to_sec( time ) )

            # Sensor readouts
            sensor_frame_dict = {}
            index = 4
            for i, sensor in enumerate( sensor_sizes[ controller ] ):
                measurement = 0
                float_bytes = []
                for byte_num in range( sensor_sizes[controller][sensor] ):
                    if ( sensor_formats[controller][sensor] != float ):
                        measurement += ( int_frame[index + byte_num] << 8*byte_num )
                    else:
                        float_bytes.append( ( int_frame[index + byte_num] ).to_bytes(1, 'big' ) ) 
                if ( sensor_formats[controller][sensor] == float ):
                    measurement = byte_array_to_float( float_bytes )
                sensor_frame_dict[sensor] = measurement
                index += sensor_sizes[controller][sensor]
            sensor_vals_list = list( conv_raw_sensor_readouts( controller, sensor_frame_dict ).values() )
            for val in sensor_vals_list:
                sensor_frame.append( val )
            sensor_frames.append( sensor_frame )
        return sensor_frames
    elif ( format == 'bytes' ):
        return sensor_frames_int 
## get_sensor_frame ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         format_sensor_readout                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
#        Formats a sensor readout into a label, rounded readout, and units         #
#                                                                                  #
####################################################################################
def format_sensor_readout( controller, sensor, readout ):

    # Readout units
    units = sensor_units[controller][sensor] 

    # Rounded readout
    if ( units != None ):
        readout_str = "{:.3f}".format( readout )
    else:
        readout_str = str( readout )

    # Concatentate label, readout, and units
    if ( units != None ):
        output = sensor + ": " + readout_str + " " + units
    else:
        output = sensor + ": " + readout_str
    return output
## format_sensor_readout ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         sensor_extract_data_filter                                               #
#                                                                                  #
# DESCRIPTION:                                                                     #
#       Finds the end of valid data extracted from flash extract and return a list #
#       containing only good data                                                  #
#                                                                                  #
####################################################################################
def sensor_extract_data_filter( data ):

    # Indices of beginning and end of good data 
    start_index = 0
    end_index   = len( data ) - 1

    # Search exit condition
    exit = False

    # Search index
    search_index = 0
    
    # Begin binary search
    while( not exit ):
        # Set search index
        search_index = ( (end_index - start_index)//2 ) + start_index

        # Check if two consecutive rows are identically equal
        rows_equal = ( data[search_index] == data[search_index+1] )

        # Check for exit condition
        if   (   search_index       == start_index ):
            if ( rows_equal ):
                return None
            else:
                return data[0:search_index-1]
        elif ( ( search_index + 1 ) == end_index   ):
            if ( rows_equal ):
                return data[0:start_index-1]
            else:
                return data[0:end_index-1]
        else: # No exit condfition
            # Update search range
            if ( rows_equal ):
                end_index = search_index
            else:
                start_index = search_index
## sensor_extract_data_filter ## 


####################################################################################
# Commands                                                                         #
####################################################################################


###################################################################################
# END OF FILE                                                                     #
###################################################################################