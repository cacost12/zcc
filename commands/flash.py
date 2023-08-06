####################################################################################
#                                                                                  #
# flash.py -- flash command, controls the on board external flash                  #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 8/5/2023                                                                   #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################

# Standard 
import datetime
import os
import time

# Project
import binUtil
import config
import commands
import messageUtil
import sensor_conv
import zavController


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
MAX_ARGS = 5

# Command type -- subcommand function
COMMAND_TYPE = 'subcommand'

# Command opcode
OPCODE = b'\x04' 

MAX_NUM_BYTES = 31

# Subcommand codes
READ_CODE    = b'\x01'  
ENABLE_CODE  = b'\x02'  
DISABLE_CODE = b'\x03'  
WRITE_CODE   = b'\x04'  
ERASE_CODE   = b'\x05'  
STATUS_CODE  = b'\x06'  
EXTRACT_CODE = b'\x07'  


####################################################################################
# Procedures                                                                       #
####################################################################################



####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         flash                                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         read and write data to a controller's extenral flash                     #
#                                                                                  #
####################################################################################
def flash( Args, zavDevice ):

    ################################################################################
    # Local Variables                                                              #
    ################################################################################

    # Extract blocks
    EXTRACT_FRAME_SIZE       = zavController.sensor_frame_sizes[zavDevice.controller]
    EXTRACT_NUM_FRAMES       = 524288 // EXTRACT_FRAME_SIZE 
    EXTRACT_NUM_UNUSED_BYTES = 524288 %  EXTRACT_FRAME_SIZE 

    # flash IO data
    byte            = None
    string          = None
    file            = None
    num_bytes       = None

    # Flash status register contents 
    status_register = None

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

        # Pull options from args
        Args_options = Args[1:]

        # Check that two options with input data were supplied
        if ( Args_options[0] == '-h'):
            options = [Args_options[0]]
            options_command = False
        elif ( len(Args_options) < 4):
            print("Error: Not enough options/inputs")
            return
        else:
            options = [Args_options[0], Args_options[2]]
            inputs  = {
                       options[0] : Args_options[1],
                       options[1] : Args_options[3]
                    }
            options_command = True
    else:
        options_command = False


    ################################################################################
    # Command-Specific Checks                                                      #
    ################################################################################

    # Check input data for each option
    if ( options_command ):

        # Check for duplicate options
        if ( options[0] == options[1] ):
            print('Error: Duplicate option supplied')
            return

        # Perform option specific checks
        for option in options:

            ################# -b option #######################
            if ( option == '-b' ):
                # Check byte is formatted correctly
                # Format: 0xXX --> XX is a hex number

                # Check length
                if( len( inputs[option] ) != 4):
                    print('Error: Invalid byte format.')
                    return
                
                # Check for 0x prefix
                if( inputs[option][0:2] != '0x'):
                    print("Error: Invalid byte format. " +
                          " Missing 0x prefix")

                # Convert to integer
                try:
                    byte_int = int( inputs[option], 0 )
                except ValueError:
                    print('Error: Invalid byte.')
                    return

                # Convert to byte
                byte = byte_int.to_bytes(1, 'big')
                

            ################# -s option #######################
            elif ( option == '-s' ):
                # Currently no parse checks needed
                pass

            ################# -n option #######################
            elif ( option == '-n' ):
                # Verify number of bytes is an integer
                try:
                    num_bytes = int( inputs[option], 0)
                except ValueError:
                    print('Error: Invalid number of bytes.')
                    return

                # Verify numbers of bytes is in range
                if ( num_bytes <= 0 or num_bytes > MAX_NUM_BYTES ): 
                    print( "Error: Invalid number of bytes." )
                    return

            ################# -a option #######################
            elif ( option == '-a' ):
                # Check address is formatted correctly
                # Format: 0xXXXXXX

                # Check length
                if( len( inputs[option] ) != 8):
                    print('Error: Invalid Address format.')
                    return
                
                # Check for 0x prefix
                if( inputs[option][0:2] != '0x' ):
                    print("Error: Invalid byte format. " +
                          " Missing 0x prefix")

                # Convert to integer
                try:
                    address_int = int( inputs[option], 0 )
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
            elif ( option == '-f' ):
                # Verify output file doesn't already exist 
                # Verify input file exists
                pass

        # Verify read and write subcommands have an address supplied    
        if (   subcommand == 'write' 
            or subcommand == 'read'):
            if ('-a' not in options):
                print('Error: The write and read operations ' +
                      'require an address supplied by the '   +
                      '-a option')
                return


    ################################################################################
    # Subcommand: flash help                                                       #
    ################################################################################
    if ( subcommand == "help"):
        messageUtil.display_help_info('flash')
        return


    ################################################################################
    # Subcommand: flash enable                                                     #
    ################################################################################
    elif ( subcommand == "enable" ):

        # Send Opcode/Subcommand
        zavDevice.sendByte( OPCODE      )
        zavDevice.sendByte( ENABLE_CODE )

        # Reconfigure Controller
        zavDevice.flashWriteEnable()
        return


    ################################################################################
    # Subcommand: flash disable                                                    #
    ################################################################################
    elif ( subcommand == "disable" ):

        # Send the Opcode/Subcommand
        zavDevice.sendByte( OPCODE       )
        zavDevice.sendByte( DISABLE_CODE )

        zavDevice.flashWriteDisable()
        return


    ################################################################################
    # Subcommand: flash status                                                     #
    ################################################################################
    elif ( subcommand == "status" ):

        # Send command/subcommand codes 
        zavDevice.sendByte( OPCODE      )
        zavDevice.sendByte( STATUS_CODE )

        # Recieve the contents of the flash status register 
        status_register     = zavDevice.readByte()
        status_register_int = ord( status_register     )
        flash_status_code = zavDevice.readByte()

        # Parse return code
        if (status_register == b''):
            print("Error: No response recieved from " +
                  "controller")
        else:
            print("Status register contents: \n") 
            print( "BUSY: ", binUtil.get_bit( status_register_int, 0 ) )
            print( "WEL : ", binUtil.get_bit( status_register_int, 1 ) )
            print( "BP0 : ", binUtil.get_bit( status_register_int, 2 ) )
            print( "BP1 : ", binUtil.get_bit( status_register_int, 3 ) )
            print( "BP2 : ", binUtil.get_bit( status_register_int, 4 ) )
            print( "BP3 : ", binUtil.get_bit( status_register_int, 5 ) )
            print( "AAI : ", binUtil.get_bit( status_register_int, 6 ) )
            print( "BPL : ", binUtil.get_bit( status_register_int, 7 ) )
            print( )

        return


    ################################################################################
    # Subcommand: flash write                                                      #
    ################################################################################
    elif ( subcommand == "write" ):

        # Check if flash chip has writing operations enabled
        if ( not zavDevice.getFlashWriteProtection()
            and not ( options[0] == '-h' )):
            print("Error: Flash write has not been enabled. " +
                  "Run flash write enable to enable writing " +
                  "to the flash chip")
            return

        ################### -h option #########################
        if ( options[0] == '-h' ):
            commands.display_help_info('flash')
            return

        ################### -b option #########################
        elif ( byte != None ):
            # Send command/subcommand codes 
            zavDevice.sendByte( OPCODE     )
            zavDevice.sendByte( WRITE_CODE )
            
            # Send base address
            zavDevice.sendBytes( address_bytes )

            # Send number of bytes to write
            zavDevice.sendBytes( b'\x01' )

            # Send byte to write to flash
            zavDevice.sendByte( byte )

            print("Flash write successful")
            return

        ################### -s option #########################
        elif ( string != None ):
            print("Error: Option not yet supported")
            return

        ################### -f option #########################
        elif ( file != None ):
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
    elif ( subcommand == "read" ):

        ################### -h option #########################
        if ( options[0] == '-h' ):
            commands.display_help_info('flash')
            return

        ################### -n option #########################
        elif( num_bytes != None ):

            # Send command/subcommand codes 
            zavDevice.sendByte( OPCODE    )
            zavDevice.sendByte( READ_CODE )
            
            # Send base address
            zavDevice.sendBytes( address_bytes )

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
    elif ( subcommand == "erase" ):
        
        # Send command/subcommand codes 
        zavDevice.sendByte( OPCODE     )
        zavDevice.sendByte( ERASE_CODE )
        print( "Flash erase sucessful" )
        return


    ################################################################################
    # Subcommand: flash extract                                                    #
    ################################################################################
    elif ( subcommand == "extract" ):

        # Send command/subcommand codes 
        zavDevice.sendByte( OPCODE       )
        zavDevice.sendByte( EXTRACT_CODE )

        # Start timer
        start_time = time.perf_counter()

        # Recieve Data 
        rx_byte_blocks = []
        for i in range( EXTRACT_NUM_FRAMES ):
            if ( i%100 == 0 ):
                print( "Reading block " + str(i) + "..."  )
            rx_sensor_frame_block = zavDevice.getSensorFrameBytes()
            rx_byte_blocks.append( rx_sensor_frame_block )
        
        # Receive the unused bytes
        unused_bytes = zavDevice.readBytes( EXTRACT_NUM_UNUSED_BYTES )

        # Record ending time
        extract_time = time.perf_counter() - start_time

        # Convert the data from bytes to measurement readouts
        sensor_frames = zavDevice.getSensorFrames( rx_byte_blocks )

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
        messageUtil.error_msg()
        return

## flash ##


###################################################################################
# END OF FILE                                                                     # 
###################################################################################