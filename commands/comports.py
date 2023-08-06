####################################################################################
#                                                                                  #
# comports.py -- comports command, displays serial port info and connects/         #
#                disconnects from the serial port                                  #
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
import serial.tools.list_ports

# Project
import config
import messageUtil
import validator


####################################################################################
# Globals                                                                          #
####################################################################################

# Serial port timeouts
if ( config.zav_debug ):
	default_timeout = 100 # 100 second timeout
else:
	default_timeout = 1   # 1 second timeout

# Options Dictionary
INPUTS = { 
        '-h' : 'Display help info',
        '-l' : 'List available serial ports',
        '-c' : 'Connect to a serial port',
        '-d' : 'Disconnect from a serial port'
}

# Maximum number of arguments
MAX_ARGS = 3

# Command type -- subcommand function
COMMAND_TYPE = 'default'


####################################################################################
# Procedures                                                                       #
####################################################################################


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		comports                                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		connects to a USB device or displays connectivity                          #
#                                                                                  #
####################################################################################
def comports( Args, zavDevice ):


	##############################################################################
	# Basic inputs parsing                                                       #
	##############################################################################
	parse_check = validator.parseArgs(
                            Args,
                            MAX_ARGS,
                            INPUTS,
                            COMMAND_TYPE 
                           )

	if ( not parse_check ):
		return # user inputs failed parse tests

	##############################################################################
	# Command Specific Parsing                                                   #
	##############################################################################
	option            = Args[0]
	port_supplied     = False
	baudrate_supplied = False

	# Set variables if they exist 
	if ( len(Args) >= 2 ):
		target_port   = Args[1]
		port_supplied = True

	# Check for valid baudrate
	if ( len(Args) == 3 ):
		try: 
			baudrate = int( Args[2] )
			baudrate_supplied = True
		except ValueError:
			print( "Error: invalid baudrate. Check that the " +
                  "baudrate is in bits/s and is an integer" )
			return 

	##############################################################################
    # List Option (-l)                                                           #
	##############################################################################
	if ( option == "-l" ):

		avail_ports = serial.tools.list_ports.comports()
		print( "\nAvailable COM ports: " )
		for port_num,port in enumerate( avail_ports ):
			print( "\t" + str(port_num) + ": " + port.device + 
                   " - ", end="" ) 
			if ( port.manufacturer != None ):
				print( port.manufacturer + ": ", end="" )
			if ( port.description  != None ):
				print( port.product )
			else:
				print( "device info unavailable" )
		print()
		return 

	##############################################################################
    # Help Option (-h)                                                           #
	##############################################################################
	elif ( option == "-h" ):
		messageUtil.display_help_info( 'comports' )
		return 

	##############################################################################
    # Connect Option (-c)                                                        #
	##############################################################################
	elif ( option == "-c" ):
		# Check that port has been supplied
		if   ( not port_supplied     ):
			print( "Error: no port supplied to comports " +
                   "function" )
			return 

		# Check that baudrate has been supplied
		elif ( not baudrate_supplied ):
			print( "Error: no baudrate supplied to comports " +
                   "function" )
			return 

		# Check that inputed port is valid
		avail_ports = serial.tools.list_ports.comports()
		avail_ports_devices = []
		for port in avail_ports:
			avail_ports_devices.append(port.device)
		if ( not (target_port in avail_ports_devices) ):
			print( "Error: Invalid serial port\n" )
			comports( ["-l"] )
			return 

		# Initialize Serial Port
		zavDevice.initComport(
                             baudrate, 
                             target_port, 
                             default_timeout
                             )

		# Connect to serial port
		connection_status = zavDevice.openComport()
		if( connection_status ):
			print( "Connected to port " + target_port + 
                   " at " + str(baudrate) + " baud" )
		return 

	##############################################################################
    # Disconnect Option (-d)                                                     #
	##############################################################################
	elif ( option == "-d" ):
		connection_status = zavDevice.closeComport()
		if ( connection_status ):
			print( "Disconnected from active serial port" )
			return 
		else: 
			print( "An error ocurred while closing port " + 
                   target_port )
			return 

	return 
## comports ##


##################################################################################
# END OF FILE                                                                    #
##################################################################################