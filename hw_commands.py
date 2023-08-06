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
#         byte_array_to_int                                                        #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Returns an integer corresponding the hex number passed into the function #
#       as a byte array. Assumes least significant bytes are first                 #
#                                                                                  #
####################################################################################
def byte_array_to_int( byte_array ):
    int_val   = 0 # Intermediate computation value
    result    = 0 # Final result integer
    num_bytes = len( byte_array )
    for i, byte in enumerate( byte_array ):
        int_val = int.from_bytes( byte, 'big')
        int_val = int_val << 8*i
        result += int_val
    return result
## byte_array_to_int ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         byte_array_to_float                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Returns an floating point number corresponding the hex number passed     # 
#         into the function as a byte array. Assumes least significant bytes are   # 
#         first                                                                    #
#                                                                                  #
####################################################################################
def byte_array_to_float( byte_array ):
    # Check to NaN
    if ( byte_array == [b'\xFF', b'\xFF', b'\xFF', b'\xFF'] ):
        byte_array = [b'\x00', b'\x00', b'\x00', b'\x00']
    byte_array_joined = b''.join( byte_array )
    return struct.unpack( 'f', byte_array_joined )[0]
## byte_array_to_float ##


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


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         sensor                                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Displays sensor data and/or info                                         #
#                                                                                  #
####################################################################################
def sensor( Args, zavDevice, show_readouts = True ):

    ################################################################################
    # Local Variables                                                              #
    ################################################################################

    # Subcommand and Options Dictionary
    sensor_inputs = {
                    'dump' : {
                             },
                    'poll' : {
                             '-n' : 'Specify a sensor number',
                             '-h' : 'Display sensor usage info'
                             },
                    'plot' : {
                             '-n' : 'Specify a sensor number',
                             '-h' : 'Display sensor usage info'
                             },
                    'list' : {
                             },
                    'help' : {
                             }
                    }

    # Maximum number of command arguments 
    max_args = 7

    # Command type -- subcommand function
    command_type = 'subcommand'

    # Command opcode 
    opcode = b'\x05'

    # Subcommand codes
    subcommand_codes = {
                       'dump' : b'\x01',
                       'poll' : b'\x02'
                       }

    # Complete list of sensor names/numbers 
    sensor_numbers = list( controller_sensors[zavDevice.controller].keys() )

    # Sensor poll codes
    sensor_poll_codes = sensor_codes[zavDevice.controller]
    sensor_poll_cmds  = {
                         'START'   : b'\xF3',
                         'REQUEST' : b'\x51',
                         'WAIT'    : b'\x44',
                         'RESUME'  : b'\xEF',
                         'STOP'    : b'\x74'
                        }

    # Timeout for sensor poll
    sensor_poll_timeout = 100

    # Size of sensor readouts
    readout_sizes = sensor_sizes[zavDevice.controller]

    # Lists of sensor data
    sensor_bytes_list = []
    sensor_int_list   = []


    ################################################################################
    # Basic Inputs Parsing                                                         #
    ################################################################################
    parse_check = commands.parseArgs(
                           Args,
                           max_args,
                           sensor_inputs,
                           command_type
                           )

    # Return if user input fails parse checks
    if ( not parse_check ):
        return 

    # Set subcommand, options, and input data
    user_subcommand = Args[0]
    if ( len(Args) != 1 ):
        
        # Extract option
        user_option = Args[1]

        # Extract inputs
        user_sensor_nums = Args[2:]
        num_sensors      = len( user_sensor_nums )


    ################################################################################
    # Command-Specific Checks                                                      #
    ################################################################################

    # Verify sensor nums supplied are valid
    if (  ( user_subcommand == "poll" ) or
          ( user_subcommand == "plot" ) ):
        if ( user_option == "-n" ):

            # Throw error if no sensors were supplied
            if ( len(user_sensor_nums) == 0 ):
                print( "Error: no sensor numbers supplied" )

            # Loop over input sensors and validity of each
            for sensor_num in user_sensor_nums:
                if ( not (sensor_num in 
                          controller_sensors[zavDevice.controller].keys())
                   ):
                    print("Error: \"" + sensor_num + "\" is "  +
                          "is not a valid sensor for "         +
                          zavDevice.controller + ". Run "      +
                          "the \"sensor list\" subcommand to " +
                          "see a list of all available "       +
                          "sensors and their corresponding "   +
                          "codes." )
                    return

            # Sensor numbers are valid, determine number of bytes needed for 
            # selected sensors
            sensor_poll_frame_size = 0 
            for sensor_num in user_sensor_nums:
                sensor_poll_frame_size += readout_sizes[sensor_num] 

    ################################################################################
    # Subcommand: sensor help                                                      #
    ################################################################################
    if   ( user_subcommand == "help" ):
        commands.display_help_info( "sensor" )
        return


    ################################################################################
    # Subcommand: sensor dump                                                      #
    ################################################################################
    elif ( user_subcommand == "dump" ):

        # Send command opcode 
        zavDevice.sendByte( opcode )

        # Send sensor dump subcommand code
        zavDevice.sendByte( subcommand_codes[user_subcommand] )

        # Determine how many bytes are to be recieved
        sensor_dump_size_bytes = zavDevice.readByte()
        sensor_dump_size_bytes = int.from_bytes( 
                                     sensor_dump_size_bytes, 
                                     "big" )

        # Recieve data from controller
        for byteNum in range( sensor_dump_size_bytes ):
            sensor_bytes_list.append( zavDevice.readByte() )

        # Get readouts from byte array
        zavDevice.sensor_readouts = get_sensor_readouts( 
                                                       zavDevice.controller, 
                                                       sensor_numbers      ,
                                                       sensor_bytes_list
                                                       )

        # Display Sensor readouts
        if ( show_readouts ):
            for sensor in zavDevice.sensor_readouts:
                readout_formatted = format_sensor_readout(
                                                        zavDevice.controller,
                                                        sensor               ,
                                                        zavDevice.sensor_readouts[sensor]
                                                        )
                print( readout_formatted )
            
        return

    ################################################################################
    # Subcommand: sensor poll                                                      #
    ################################################################################
    elif ( user_subcommand == "poll" ):

        # Send command opcode
        zavDevice.sendByte( opcode )

        # Send sensor poll subcommand code
        zavDevice.sendByte( subcommand_codes[user_subcommand] )

        # Tell the controller how many sensors to use
        zavDevice.sendByte( num_sensors.to_bytes( 1, 'big' ) )

        # Send the controller the sensor codes
        for sensor_num in user_sensor_nums:
            zavDevice.sendByte( sensor_poll_codes[sensor_num] )
        
        # Start the sensor poll sequence
        zavDevice.sendByte( sensor_poll_cmds['START'] )

        # Receive and display sensor readouts 
        timeout_ctr = 0
        while ( timeout_ctr <= sensor_poll_timeout ):
            zavDevice.sendByte( sensor_poll_cmds['REQUEST'] )
            sensor_bytes_list = zavDevice.readBytes( sensor_poll_frame_size ) 
            sensor_readouts   = get_sensor_readouts(
                                                    zavDevice.controller, 
                                                    user_sensor_nums    ,
                                                    sensor_bytes_list
                                                   )
            for sensor in sensor_readouts:
                readout_formated = format_sensor_readout(
                                                         zavDevice.controller, 
                                                         sensor              ,
                                                         sensor_readouts[sensor] 
                                                         )
                print( readout_formated + '\t', end='' )
            print()

            # Pause for readibility
            zavDevice.sendByte( sensor_poll_cmds['WAIT'] )
            time.sleep(0.2)
            zavDevice.sendByte( sensor_poll_cmds['RESUME'])
            timeout_ctr += 1

        # Stop transmission    
        zavDevice.sendByte( sensor_poll_cmds['STOP'] )

        return

    ################################################################################
    # Subcommand: sensor list                                                      #
    ################################################################################
    elif ( user_subcommand == "list" ):
        # Identify current serial connection
        print("Sensor numbers for " + zavDevice.controller +
               " :" )

        # Loop over all sensors in list and print
        for sensor_num in controller_sensors[zavDevice.controller].keys():
            print( "\t" + sensor_num + " : " +
                    controller_sensors[zavDevice.controller][sensor_num] 
                 ) 
        return
    ## sensor list ##

    ################################################################################
    # Subcommand: sensor plot                                                      #
    ################################################################################
    elif ( user_subcommand == "plot" ):

        # Data Filename 
        filename = sensor_data_filenames[zavDevice.controller]

        # Import Data
        with open( filename, "r" ) as file:
            sensor_data_lines = file.readlines()
        sensor_data_str = []
        for line in sensor_data_lines:
            sensor_data_str.append( line.split('\t') )

        # Convert to floating point format
        sensor_data = []
        for frame in sensor_data_str:
            sensor_frame = []
            for val in frame:
                if ( val != '\n' ):
                    sensor_frame.append( float( val ) )
            sensor_data.append( sensor_frame )
        
        # Filter out garbage flash data
        sensor_data_filtered = sensor_extract_data_filter( sensor_data )
        sensor_data_filtered = np.array( sensor_data_filtered )

        # Select data to plot
        sensor_labels = []
        for sensor in user_sensor_nums:
            sensor_index = sensor_indices[zavDevice.controller][sensor]
            sensor_label = ( sensor + " (" + 
                             sensor_units[zavDevice.controller][sensor] + ")" )
            sensor_labels.append( sensor_label )
            time_data = sensor_data_filtered[:,0]/60.0 # minutes
            plt.plot( time_data, 
                      sensor_data_filtered[:,sensor_index] )

        # Plot parameters
        plt.title( "Data: " + zavDevice.controller )
        plt.xlabel( "Time, min" )
        plt.ylabel( "Measurement Value" )
        plt.grid()
        plt.legend( sensor_labels )

        # Display
        plt.show()
        return

    ################################################################################
    # Unknown subcommand                                                           #
    ################################################################################
    else:
        print( "Error: Unknown subcommand passed to sensor " +
               "function. " )
        commands.error_msg()
        return
## sensor ##


###################################################################################
# END OF FILE                                                                     # 
###################################################################################