####################################################################################
#                                                                                  #
# ignite.py -- Ignite command, fires pyro ports and reports continuity infor       #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 8/5/2023                                                                   #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################
import config
import commands


####################################################################################
# Global Variables                                                                 #
####################################################################################

# Run config
if ( config.zav_debug ):
    default_timeout = 100 # 100 second timeout
else:
    default_timeout = 1   # 1 second timeout

# Ignition return codes
IGN_SUCCESS_CODE     = b'\x01'
IGN_SWITCH_FAIL      = b'\x02'
IGN_CONT_FAIL        = b'\x03'
IGN_FAILED_TO_IGNITE = b'\x04'
IGN_UNRECOGNIZED_CMD = b'\x05'

# Subcommands
INPUTS = { 
        'main'  : {},
        'drogue': {},
        'cont'  : {},
        'help'  : {}
}

# Maximum number of arguments
MAX_ARGS = 1

# Command type -- subcommand function
COMMAND_TYPE = 'subcommand'

# Command opcode
OPCODE = b'\x03' 

# Subcommand codes
MAIN_CODE   = b'\x01'    
DROGUE_CODE = b'\x02'    
CONT_CODE   = b'\x03'

# Return messages
RETURN_MESSAGES = {
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
# Procedures                                                                       #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         ignite                                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         issue the ignition signal to the controller or display                   #
#                                                                                  #
####################################################################################
def ignite( Args, zavDevice ):

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

    # Set subcommand
    subcommand = Args[0]


    ################################################################################
    # Subcommand: ignite help                                                      #
    ################################################################################
    if ( subcommand == "help" ):
        commands.display_help_info( 'ignite' )
        return


    ################################################################################
    # Subcommand: ignite main                                                      #
    ################################################################################
    elif ( subcommand == "main" ):

        # Send ignite opcode/subcommand
        zavDevice.sendByte( OPCODE    )
        zavDevice.sendByte( MAIN_CODE )

        # Get ignition status code
        ign_status = zavDevice.readByte()

        # Show result 
        print( RETURN_MESSAGES[ign_status] )
        return

    ################################################################################
    # Subcommand: ignite  drogue                                                   #
    ################################################################################
    elif ( subcommand == "drogue" ):

        # Send ignite opcode
        zavDevice.sendByte( OPCODE      )
        zavDevice.sendByte( DROGUE_CODE )

        # Get ignition status code
        ign_status = zavDevice.readByte()

        # Show result 
        print( RETURN_MESSAGES[ign_status] )
        return

    ################################################################################
    # Subcommand: ignite cont                                                      #
    ################################################################################
    elif ( subcommand == "cont" ):

        # Send opcode/subcommand
        zavDevice.sendByte( OPCODE    )
        zavDevice.sendByte( CONT_CODE )

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

## ignite ##


###################################################################################
# END OF FILE                                                                     # 
###################################################################################