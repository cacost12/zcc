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

# Ignition return codes
IGN_SUCCESS_CODE     = b'\x01'
IGN_SWITCH_FAIL      = b'\x02'
IGN_CONT_FAIL        = b'\x03'
IGN_FAILED_TO_IGNITE = b'\x04'
IGN_UNRECOGNIZED_CMD = b'\x05'

# Error messages
ign_messages = {
    b''     : "Ignition unsuccessful. No response code received from flight computer",
    IGN_SUCCESS_CODE :   "Ignition successful",
    IGN_SWITCH_FAIL  : ( "Ignition unsuccessful. Device is not armed. Ensure the " + 
                        "switch terminals are shorted." ),
    IGN_CONT_FAIL    : ( "Ignition unsuccessful. No ematch continuity. Ensure an " +
                        "ematch is connected." ), 
    IGN_FAILED_TO_IGNITE : ( "Ignition unsuccessful. Ematch failed to ignite." ),
    IGN_UNRECOGNIZED_CMD : ( "Error: unrecognized ignition response code" )
}


####################################################################################
# Shared Procedures                                                                #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_bit                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         extracts a specific bit from an integer                                  #
#                                                                                  #
####################################################################################
def get_bit( num, bit_index ):
    if ( num & ( 1 << bit_index ) ):
        return 1
    else:    
        return 0
## get_bit ##


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
    opcode = b'\x03'

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

    # Verify connection to board with sensors
    if ( not (zavDevice.controller in controller_sensors.keys()) ):
        print( "Error: The sensor command requires a valid " +
               "serial connection to a controller with "     +
               "sensors. Run the \"connect\" command to "    +
               "establish a valid connection" )
        return 

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


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         flash                                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         read and write data to a controller's extenral flash                     #
#                                                                                  #
####################################################################################
def flash(Args, zavDevice):

    ################################################################################
    # Local Variables                                                              #
    ################################################################################

    # Subcommand and Options Dictionary
    flash_inputs= { 
    'enable'  : {
                },
    'disable' : {
                },
    'status'  : {
                },
    'write'   : {
            '-b' : 'Specify a byte to write to flash memory'  ,
            '-s' : 'Specify a string to write to flash memory',
            '-a' : 'Specify a memory address to write to'     ,
            '-f' : 'Specify a file to use for input data'     ,
            '-h' : 'Display help info'
                },
    'read'    : {
            '-a' : 'Specify a memory address to read from',
            '-n' : 'Specify a number of bytes to read from flash memory',
            '-f' : 'Specify a file to use for output data',
            '-h' : 'Display help info'
                }, 
    'erase'   : {
                },
    'help'    : {
                },
    'extract' : {
                },
                  }
    
    # Maximum number of arguments
    max_args = 5

    # Command type -- subcommand function
    command_type = 'subcommand'

    # Command opcode
    opcode = b'\x04' 

    max_num_bytes = 31

    # Subcommand codes
    flash_read_code    = b'\x01'  
    flash_enable_code  = b'\x02'  
    flash_disable_code = b'\x03'  
    flash_write_code   = b'\x04'  
    flash_erase_code   = b'\x05'  
    flash_status_code  = b'\x06'  
    flash_extract_code = b'\x07'  

    # flash IO data
    byte            = None
    string          = None
    file            = None
    num_bytes       = None

    # Flash status register contents 
    status_register = None

    # Extract blocks
    extract_frame_size       = sensor_frame_sizes[zavDevice.controller]
    extract_num_frames       = 524288 // extract_frame_size
    extract_num_unused_bytes = 524288 %  extract_frame_size


    ################################################################################
    # Basic Inputs Parsing                                                         #
    ################################################################################
    parse_check = commands.parseArgs(
                            Args        ,
                            max_args    ,
                            flash_inputs,
                            command_type 
                            )

    # Return if user input fails parse checks
    if ( not parse_check ):
        return 

    # Set subcommand, options, and input data
    user_subcommand = Args[0]
    if ( len(Args) != 1 ):

        # Pull options from args
        Args_options = Args[1:]

        # Check that two options with input data were supplied
        if ( Args_options[0] == '-h'):
            user_options = [Args_options[0]]
            options_command = False
        elif ( len(Args_options) < 4):
            print("Error: Not enough options/inputs")
            return
        else:
            user_options = [Args_options[0], Args_options[2]]
            user_inputs  = {
                           user_options[0] : Args_options[1],
                           user_options[1] : Args_options[3]
                           }
            options_command = True
    else:
        options_command = False

    ################################################################################
    # Command-Specific Checks                                                      #
    ################################################################################

    # Check input data for each option
    if (options_command):

        # Check for duplicate options
        if (user_options[0] == user_options[1]):
            print('Error: Duplicate option supplied')
            return

        # Perform option specific checks
        for user_option in user_options:

            ################# -b option #######################
            if (user_option == '-b'):
                # Check byte is formatted correctly
                # Format: 0xXX --> XX is a hex number

                # Check length
                if(len(user_inputs[user_option]) != 4):
                    print('Error: Invalid byte format.')
                    return
                
                # Check for 0x prefix
                if(user_inputs[user_option][0:2] != '0x'):
                    print("Error: Invalid byte format. " +
                          " Missing 0x prefix")

                # Convert to integer
                try:
                    byte_int = int(user_inputs[user_option], 0)
                except ValueError:
                    print('Error: Invalid byte.')
                    return

                # Convert to byte
                byte = byte_int.to_bytes(1, 'big')
                

            ################# -s option #######################
            elif (user_option == '-s'):
                # Currently no parse checks needed
                pass

            ################# -n option #######################
            elif (user_option == '-n'):
                # Verify number of bytes is an integer
                try:
                    num_bytes = int(user_inputs[user_option], 0)
                except ValueError:
                    print('Error: Invalid number of bytes.')
                    return

                # Verify numbers of bytes is in range
                if ( num_bytes <= 0 or num_bytes > max_num_bytes ): 
                    print( "Error: Invalid number of bytes." )
                    return

            ################# -a option #######################
            elif (user_option == '-a'):
                # Check address is formatted correctly
                # Format: 0xXXXXXX

                # Check length
                if(len(user_inputs[user_option]) != 8):
                    print('Error: Invalid Address format.')
                    return
                
                # Check for 0x prefix
                if(user_inputs[user_option][0:2] != '0x'):
                    print("Error: Invalid byte format. " +
                          " Missing 0x prefix")

                # Convert to integer
                try:
                    address_int = int(user_inputs[user_option], 0)
                except ValueError:
                    print('Error: Invalid Address.')
                    return

                # Convert to bytes
                address_bytes = address_int.to_bytes(
                                                    3, 
                                                    byteorder='big',
                                                    signed=False
                                                    )

            ################# -f option #######################
            elif (user_option == '-f'):
                # Verify output file doesn't already exist 
                # Verify input file exists
                pass

        # Verify read and write subcommands have an address supplied    
        if (   user_subcommand == 'write' 
            or user_subcommand == 'read'):
            if ('-a' not in user_options):
                print('Error: The write and read operations ' +
                      'require an address supplied by the '   +
                      '-a option')
                return


    ################################################################################
    # Subcommand: flash help                                                       #
    ################################################################################
    if (user_subcommand == "help"):
        commands.display_help_info('flash')
        return

    ################################################################################
    # Subcommand: flash enable                                                     #
    ################################################################################
    elif (user_subcommand == "enable"):

        # Send Opcode/Subcommand
        zavDevice.sendByte(opcode)
        zavDevice.sendByte(flash_enable_code)

        # Reconfigure Controller
        zavDevice.flashWriteEnable()
        return

    ################################################################################
    # Subcommand: flash disable                                                    #
    ################################################################################
    elif (user_subcommand == "disable"):

        # Send the Opcode/Subcommand
        zavDevice.sendByte(opcode)
        zavDevice.sendByte(flash_disable_code)

        zavDevice.flashWriteDisable()
        return

    ################################################################################
    # Subcommand: flash status                                                     #
    ################################################################################
    elif (user_subcommand == "status"):

        # Send the flash opcode
        zavDevice.sendByte(opcode)

        # Send the subcommand opcode
        zavDevice.sendByte(flash_status_code)

        # Recieve the contents of the flash status register 
        status_register     = zavDevice.readByte()
        status_register_int = ord( status_register     )

        # Get the status code of the flash operation
        flash_status_code = zavDevice.readByte()

        # Parse return code
        if (status_register == b''):
            print("Error: No response recieved from " +
                  "controller")
        else:
            print("Status register contents: \n") 
            print( "BUSY: ", get_bit( status_register_int, 0 ) )
            print( "WEL : ", get_bit( status_register_int, 1 ) )
            print( "BP0 : ", get_bit( status_register_int, 2 ) )
            print( "BP1 : ", get_bit( status_register_int, 3 ) )
            print( "BP2 : ", get_bit( status_register_int, 4 ) )
            print( "BP3 : ", get_bit( status_register_int, 5 ) )
            print( "AAI : ", get_bit( status_register_int, 6 ) )
            print( "BPL : ", get_bit( status_register_int, 7 ) )
            print( )

        return

    ################################################################################
    # Subcommand: flash write                                                      #
    ################################################################################
    elif (user_subcommand == "write"):

        # Check if flash chip has writing operations enabled
        if ( not zavDevice.getFlashWriteProtection()
            and not (user_options[0] == '-h')):
            print("Error: Flash write has not been enabled. " +
                  "Run flash write enable to enable writing " +
                  "to the flash chip")
            return

        ################### -h option #########################
        if (user_options[0] == '-h'):
            commands.display_help_info('flash')
            return

        ################### -b option #########################
        elif (byte != None):
            # Send flash opcode
            zavDevice.sendByte( opcode )

            # Send flash subcommand 
            zavDevice.sendByte( flash_write_code )
            
            # Send base address
            zavDevice.sendBytes( address_bytes )

            # Send number of bytes to write
            zavDevice.sendBytes( b'\x01' )

            # Send byte to write to flash
            zavDevice.sendByte( byte )

            print("Flash write successful")
            return

        ################### -s option #########################
        elif (string != None):
            print("Error: Option not yet supported")
            return

        ################### -f option #########################
        elif (file != None):
            print("Error: Option not yet supported")
            return
        
        ################# Unknown option #####################
        else:
            print("Error: Something went wrong. The flash "+ 
                  "write command failed to find input "    +
                  "to write to flash")
            return


    ################################################################################
    # Subcommand: flash read                                                       #
    ################################################################################
    elif (user_subcommand == "read"):

        ################### -h option #########################
        if (user_options[0] == '-h'):
            commands.display_help_info('flash')
            return

        ################### -n option #########################
        elif( num_bytes != None ):

            # Send flash opcode
            zavDevice.sendByte(opcode)

            # Send flash operation code
            zavDevice.sendByte( flash_read_code )
            
            # Send base address
            zavDevice.sendBytes(address_bytes)

            # Send number of bytes to read
            num_bytes_byte = num_bytes.to_bytes( 1, 
                                           byteorder = 'big', 
                                           signed = False )
            zavDevice.sendByte( num_bytes_byte )

            # Receive Bytes into a byte array
            rx_bytes = []
            for i in range( num_bytes ):
                rx_bytes.append( zavDevice.readByte() )

            # Display Bytes on the terminal
            print( "Received bytes: \n" )
            for rx_byte in rx_bytes:
                print( rx_byte, ", ", end = "" )
            print()

            return

        ################### -f option #########################
        elif( file!= None ):
            print("Error: Option not yet supported")
            return


    ################################################################################
    # Subcommand: flash erase                                                      #
    ################################################################################
    elif (user_subcommand == "erase"):
        
        # Send flash opcode 
        zavDevice.sendByte( opcode )

        # Send flash erase subcommand code 
        zavDevice.sendByte( flash_erase_code )

        print( "Flash erase sucessful" )
        return


    ################################################################################
    # Subcommand: flash extract                                                    #
    ################################################################################
    elif ( user_subcommand == "extract" ):

        # Send flash opcode 
        zavDevice.sendByte( opcode )

        # Send flash extract subcommand code 
        zavDevice.sendByte( flash_extract_code )

        # Start timer
        start_time = time.perf_counter()

        # Recieve Data in 32 byte blocks
        # Flash contains 4096 blocks of data
        rx_byte_blocks = []
        for i in range( extract_num_frames ):
            if ( i%100 == 0 ):
                print( "Reading block " + str(i) + "..."  )
            rx_sensor_frame_block = get_sensor_frame_bytes( zavDevice )
            rx_byte_blocks.append( rx_sensor_frame_block )
        
        # Receive the unused bytes
        unused_bytes = zavDevice.readBytes( extract_num_unused_bytes )

        # Record ending time
        extract_time = time.perf_counter() - start_time

        # Convert the data from bytes to measurement readouts
        sensor_frames = get_sensor_frames( zavDevice.controller, rx_byte_blocks )

        # Set Create Output Data folder -> output/extract/controller/date
        if ( not os.path.exists( "output" ) ):
            os.mkdir( "output" )
        output_dir = "output/extract/"
        if ( not os.path.exists( output_dir ) ):
            os.mkdir( output_dir )
        output_dir += zavDevice.controller + "/"
        if ( not os.path.exists( output_dir ) ):
            os.mkdir( output_dir )
        run_date = datetime.date.today()
        run_date = run_date.strftime( "%m-%d-%Y" )
        output_dir += run_date
        if ( not os.path.exists( output_dir ) ):
            os.mkdir( output_dir )

        # Determine file name so as to not overwrite old data
        base_filename = "sensor_data"
        test_num = 0
        output_filename = output_dir + "/" + base_filename + str( test_num ) + ".txt"
        while ( os.path.exists( output_filename ) ):
            test_num += 1
            output_filename = output_dir + "/" + base_filename + str( test_num ) + ".txt"

        # Export the data to txt files
        with open( output_filename, 'w' ) as file:
            for sensor_frame in sensor_frames:
                for val in sensor_frame:
                    file.write( str( val ) )
                    file.write( '\t')
                file.write( '\n' )    

        # Parse return code
        print( "Flash extract successful" )
        print( "Extract time: {:.3f} sec".format( extract_time ) )
        return


    ################################################################################
    # Unknown Option                                                               #
    ################################################################################
    else:
        print("Error: unknown option passed to connect function")    
        commands.error_msg()
        return
# sensor # 


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         ignite                                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         issue the ignition signal to the controller or display                   #
#                                                                                  #
####################################################################################
def ignite(Args, zavDevice):

    ################################################################################
    # Local Variables                                                              #
    ################################################################################

    # Subcommand Dictionary
    # Options Dictionary
    ignite_inputs = { 
                    'main'  : {},
                    'drogue': {},
                    'cont'  : {},
                    'help'  : {}
                    }
    
    # Maximum number of arguments
    max_args = 1

    # Command type -- subcommand function
    command_type = 'subcommand'

    # Command opcode
    opcode = b'\x03' 

    # Subcommand codes
    ignite_main_code   = b'\x01'    
    ignite_drogue_code = b'\x02'    
    ignite_cont_code   = b'\x03'


    ################################################################################
    # Basic Inputs Parsing                                                         #
    ################################################################################

    parse_check = commands.parseArgs(
                                    Args,
                                    max_args,
                                    ignite_inputs,
                                    command_type 
                                    )

    # Return if user input fails parse checks
    if ( not parse_check ):
        return 

    # Set subcommand
    user_subcommand = Args[0]


    ################################################################################
    # Subcommand: ignite help                                                      #
    ################################################################################
    if (user_subcommand == "help"):
        commands.display_help_info('ignite')
        return


    ################################################################################
    # Subcommand: ignite main                                                      #
    ################################################################################
    elif (user_subcommand == "main"):

        # Send ignite opcode/subcommand
        zavDevice.sendByte( opcode           )
        zavDevice.sendByte( ignite_main_code )

        # Get ignition status code
        ign_status = zavDevice.readByte()

        # Show result 
        print( ign_messages[ign_status] )
        return

    ################################################################################
    # Subcommand: ignite  drogue                                                   #
    ################################################################################
    elif (user_subcommand == "drogue"):

        # Send ignite opcode
        zavDevice.sendByte( opcode             )
        zavDevice.sendByte( ignite_drogue_code )

        # Get ignition status code
        ign_status = zavDevice.readByte()

        # Show result 
        print( ign_messages[ign_status] )
        return

    ################################################################################
    # Subcommand: ignite cont                                                      #
    ################################################################################
    elif (user_subcommand == "cont"):

        # Send opcode/subcommand
        zavDevice.sendByte( opcode           )
        zavDevice.sendByte( ignite_cont_code )

        # Get ignition status code
        ign_cont   = zavDevice.readByte()
        ign_status = zavDevice.readByte()

        # Parse response code
        ign_cont = ord( ign_cont )

        # Switch continuity
        if ( ( ign_cont >> 0 ) & 1 ):
            print("Switch:        Connected")
        else: 
            print("Switch:        Disconnected")

        # Main ematch continuity
        if ( ( ign_cont >> 1 ) & 1 ):
            print("Main Ematch:   Connected")
        else: 
            print("Main Ematch:   Disconnected")

        # Drogue continuity
        if ( ( ign_cont >> 2 ) & 1 ):
            print("Drogue Ematch: Connected")
        else: 
            print("Drogue Ematch: Disconnected")

        return

    ################################################################################
    # Unknown Subcommand                                                           #
    ################################################################################
    else:
        print("Error: unknown subcommand passed to ignite " +
              "function")    
        commands.error_msg()
        return


###################################################################################
# END OF FILE                                                                     # 
###################################################################################