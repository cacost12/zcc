####################################################################################
#                                                                                  #
# connect.py -- connect command, connects to a zenith avionics computer            #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 8/6/2023                                                                   #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################

# Project
import comports
import config
import messageUtil
import validator
import zavController


####################################################################################
# Global Variables                                                                 #
####################################################################################

# Serial port timeouts
if ( config.zav_debug ):
	default_timeout = 100 # 100 second timeout
else:
	default_timeout = 1   # 1 second timeout

# Connect Command Opcode
OPCODE = b'\x02'

# Options Dictionary
INPUTS = { 
        '-h' : 'Display help info',
        '-p' : 'Specify the connection serial port',
        '-d' : 'Disconnect from active serial port'
}

# Maximum number of arguments
MAX_ARGS = 2

# Command type -- subcommand function
COMMAND_TYPE = 'default'


####################################################################################
# Procedures                                                                       #
####################################################################################


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		connect                                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		establish a serial connection with an SDR board                            #
#                                                                                  #
####################################################################################
def connect( Args, zavDevice ):

	################################################################################
	# Local Variables                                                              #
	################################################################################

	# Firmware version
	firmware_version = None


	################################################################################
	# Basic inputs parsing                                                         #
	################################################################################
	parse_check = validator.parseArgs(
                            Args,
                            MAX_ARGS,
                            INPUTS,
                            COMMAND_TYPE 
                           )
	if ( not parse_check ):
		return # user inputs failed parse tests
	option = Args[0]
	if ( len(Args) > 1 ):
		user_port = Args[1]

	##############################################################################
	# Command-Specific Inputs Parsing                                            #
	##############################################################################

	# Check if there is an active serial port
	if ( zavDevice.is_active() and option == '-p' ):
		print("Error: Serial port " + zavDevice.comport + 
               "is active. Disconnect from the active" +
               " serial port before connecting" )
		return 
	elif ( (not zavDevice.is_active()) and option == '-d' ):
		print( 'Error: No active serial port to disconnect from' )
		return 

	# Check for valid serial port
	if ( len(Args) > 1 ):
		available_ports = zavDevice.list_ports()
		if ( not (user_port in available_ports) ):
			print( "Error: Invalid serial port. Valid ports:" )
			for port_num, port in enumerate( available_ports ):
				print( "\t" + port )
			return 
	else:
		if ( option == '-p' and
		     len(Args)   == 1):
			print( "Error: No serial port supplied " )
			return 

	##############################################################################
    # Help Option (-h)                                                           #
	##############################################################################
	if ( option == '-h' ):
		messageUtil.display_help_info( "connect" )
		return 

	##############################################################################
    # Port Option (-p)                                                           #
	##############################################################################
	elif ( option == '-p' ):
		# Open the serial comport
		comports.comports( ['-c', user_port, '921600'], zavDevice )
		
		# Send the connect opcode 
		zavDevice.sendByte( OPCODE )

		# Get the board identifier 
		controller_response = zavDevice.readByte()
		if ( (controller_response == b''                    ) or
             (not (controller_response in zavController.controller_codes) ) ):
			print( "Controller connection was unsuccessful." )
			comports.comports( ['-d'], zavDevice )
			return 
		else:
			# Get the firmware version 
			firmware_version = zavController.firmware_ids[zavDevice.readByte()]

			# Set global controller variable 
			zavDevice.set_controller(
						zavController.controller_descriptions[controller_response],
					    firmware_version	
									)

            # Display connection info									
			print( "Connection established with " + 
                    zavController.controller_descriptions[controller_response] )
			print( "Firmware: " + firmware_version )
			return 
		

	##############################################################################
    # Disconnect Option (-d)                                                     #
	##############################################################################
	elif ( option == '-d' ):
		comports.comports( ['-d'], zavDevice )
		zavDevice.reset_controller()
		return 

	##############################################################################
    # Unknown Option                                                             #
	##############################################################################
	else:
		print( "Error: unknown option passed to connect " +
               "function" )	
		messageUtil.error_msg()
		return 
## connect ##


##################################################################################
# END OF FILE                                                                    #
##################################################################################