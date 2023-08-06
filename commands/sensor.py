####################################################################################
#                                                                                  #
# sensor.py -- sensor command, controls the on board sensors                       #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 8/6/2023                                                                   #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################

# Standard
import time

# Project
import binUtil
import commands
import zavController
import config


####################################################################################
# Global Variables                                                                 #
####################################################################################

# Run config
if ( config.zav_debug ):
    default_timeout = 100 # 100 second timeout
else:
    default_timeout = 1   # 1 second timeout
    
# Subcommand and Options Dictionary
INPUTS = {
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
MAX_ARGS = 7

# Command type -- subcommand function
COMMAND_TYPE = 'subcommand'

# Command opcode 
OPCODE = b'\x05'

# Subcommand codes
SUBCOMMAND_CODES = {
                'dump' : b'\x01',
                'poll' : b'\x02'
}

# Sensor poll sequencing command codes
POLL_COMMANDS = {
                'START'   : b'\xF3',
                'REQUEST' : b'\x51',
                'WAIT'    : b'\x44',
                'RESUME'  : b'\xEF',
                'STOP'    : b'\x74'
}

# Timeout for sensor poll
POLL_TIMEOUT = 100


####################################################################################
# Procedures                                                                       #
####################################################################################


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

    # Complete list of sensor names/numbers 
    sensor_numbers = list( zavController.controller_sensors[zavDevice.controller].keys() )

    # Sensor poll codes
    sensor_poll_codes = zavController.sensor_codes[zavDevice.controller]

    # Size of sensor readouts
    readout_sizes = zavController.sensor_sizes[zavDevice.controller]

    # Lists of sensor data
    sensorByteData = []
    sensorIntData  = []


    ################################################################################
    # Basic Inputs Parsing                                                         #
    ################################################################################
    parse_check = commands.parseArgs(
                           Args,
                           MAX_ARGS,
                           INPUTS,
                           COMMAND_TYPE 
                           )

    # Return if user input fails parse checks
    if ( not parse_check ):
        return 

    # Set subcommand, options, and input data
    subcommand = Args[0]
    if ( len(Args) != 1 ):
        
        # Extract option
        option = Args[1]

        # Extract inputs
        selectedSensorNames = Args[2:]
        num_sensors      = len( selectedSensorNames )


    ################################################################################
    # Command-Specific Checks                                                      #
    ################################################################################

    # Verify sensor nums supplied are valid
    if (  ( subcommand == "poll" ) or
          ( subcommand == "plot" ) ):
        if ( option == "-n" ):

            # Throw error if no sensors were supplied
            if ( len(selectedSensorNames) == 0 ):
                print( "Error: no sensor numbers supplied" )

            # Loop over input sensors and validity of each
            for sensor_num in selectedSensorNames:
                if ( not (sensor_num in 
                          zavController.controller_sensors[zavDevice.controller].keys())
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
            for sensor_num in selectedSensorNames:
                sensor_poll_frame_size += readout_sizes[sensor_num] 


    ################################################################################
    # Subcommand: sensor help                                                      #
    ################################################################################
    if   ( subcommand == "help" ):
        commands.display_help_info( "sensor" )
        return


    ################################################################################
    # Subcommand: sensor dump                                                      #
    ################################################################################
    elif ( subcommand == "dump" ):

        # Send sensor command/subcommand codes 
        zavDevice.sendByte( OPCODE                       )
        zavDevice.sendByte( SUBCOMMAND_CODES[subcommand] )

        # Determine how many bytes are to be recieved
        sensor_dump_size = zavDevice.readByte()
        sensor_dump_size = int.from_bytes( 
                                     sensor_dump_size, 
                                     "big" )

        # Recieve data from controller
        for byteNum in range( sensor_dump_size ):
            sensorByteData.append( zavDevice.readByte() )

        # Get readouts from byte array
        sensor_readouts = zavDevice.getSensorReadouts( sensor_numbers, sensorByteData )

        # Display Sensor readouts
        if ( show_readouts ):
            for sensor in sensor_readouts:
                formattedReadout = zavDevice.formatSensorReadout( sensor, 
                                                                  sensor_readouts[sensor] )
                print( formattedReadout )
            
        return


    ################################################################################
    # Subcommand: sensor poll                                                      #
    ################################################################################
    elif ( subcommand == "poll" ):

        # Send command/subcommand codes 
        zavDevice.sendByte( OPCODE                       )
        zavDevice.sendByte( SUBCOMMAND_CODES[subcommand] )

        # Tell the controller how many sensors to use
        zavDevice.sendByte( num_sensors.to_bytes( 1, 'big' ) )

        # Send the controller the sensor codes
        for sensor_num in selectedSensorNames:
            zavDevice.sendByte( sensor_poll_codes[sensor_num] )
        
        # Start the sensor poll sequence
        zavDevice.sendByte( POLL_COMMANDS['START'] )

        # Receive and display sensor readouts 
        timeout_ctr = 0
        while ( timeout_ctr <= POLL_TIMEOUT ):
            zavDevice.sendByte( POLL_COMMANDS['REQUEST'] )
            sensorByteData  = zavDevice.readBytes( sensor_poll_frame_size ) 
            sensorReadouts = zavDevice.getSensorReadouts( selectedSensorNames, 
                                                          sensorByteData )

            for sensor in sensorReadouts:
                formattedReadout = zavDevice.formatSensorReadout( sensor, 
                                                                  sensorReadouts[sensor] )
                print( formattedReadout + '\t', end='' )
            print()

            # Pause for readibility
            zavDevice.sendByte( POLL_COMMANDS['WAIT'] )
            time.sleep(0.2)
            zavDevice.sendByte( POLL_COMMANDS['RESUME'])
            timeout_ctr += 1

        # Stop transmission    
        zavDevice.sendByte( POLL_COMMANDS['STOP'] )

        return

    ################################################################################
    # Subcommand: sensor list                                                      #
    ################################################################################
    elif ( subcommand == "list" ):
        # Identify current serial connection
        print("Sensor numbers for " + zavDevice.controller +
               " :" )

        # Loop over all sensors in list and print
        for sensor_num in zavController.controller_sensors[zavDevice.controller].keys():
            print( "\t" + sensor_num + " : " +
                    zavController.controller_sensors[zavDevice.controller][sensor_num] 
                 ) 
        return
    ## sensor list ##

    ################################################################################
    # Subcommand: sensor plot                                                      #
    ################################################################################
    elif ( subcommand == "plot" ):

        # Data Filename 
        filename = zavController.sensor_data_filenames[zavDevice.controller]

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
        for sensor in selectedSensorNames:
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