####################################################################################
#                                                                                  #
# Commands.py -- module with general command line functions                        #
# Author: Colton Acosta                                                            #
# Date: 4/16/2022                                                                  #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################

# Standard imports
import sys
import os
import serial.tools.list_ports
import time

# Project imports
import sensor_conv
from   config      import *
from   controller  import *


####################################################################################
# Global Variables                                                                 #
####################################################################################

# Serial port timeouts
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
# 		display_help_info                                                          #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		displays a command's help info from its doc file                           #
#                                                                                  #
####################################################################################
def display_help_info( command ):
	with open ("doc/" + command ) as file:
		doc_lines = file.readlines()
	print()
	for line in doc_lines:
		print( line, end='' )
	print()
## display_help_info ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		error_msg                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		displays a general software failure error message                          #
#                                                                                  #
####################################################################################
def error_msg():
	print( "Something went wrong. Report this issue to " + 
              "the Zenith development team" )	
## error_msg ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		parseArgs                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		runs basic checks on command inputs and outputs a                          #
#       boolean indicating if the user input passes the                            #
#       checks                                                                     #
#                                                                                  #
####################################################################################
def parseArgs(
             Args,          # function arguments
			 max_num_Args,  # maximum number of function arguments
             Args_dic,      # dictionary of supported inputs
             command_type,  # indicates if command has subcommands
             ):

	##############################################################################
	# Local Variables                                                            #
	##############################################################################

	# Error code returns
	parse_pass = True
	parse_fail = False

	# subcommand support
	if ( command_type == 'subcommand' ):
		subcommand_func = True
	else:
		subcommand_func = False


	##############################################################################
	# Input Tests                                                                #
	##############################################################################

	# No Subcommands/Options
	if ( subcommand_func ):
		if ( len(Args) == 0 ): # no subcommand
			print( 'Error: No subcommand supplied. Valid ' +
                   'subcommands include: ' )
			for subcommand in Args_dic:
				print( '\t' + subcommand )
			print()
			return parse_fail
		user_subcommand = Args[0]
	else:
		if ( len(Args) == 0 ): # no options
			print( 'Error: No options supplied. Valid ' +
                   'options include: ' )
			for option in Args_dic:
				print( '\t' + option + '\t' + Args_dic[option] ) 
			print()
			return parse_fail
		user_option = Args[0]

	# Too Many Inputs
	if ( len(Args) > max_num_Args ): 
		print( 'Error: To many inputs.' )
		return parse_fail

	# Unrecognized Subcommand
	if ( subcommand_func ):
		if ( not (user_subcommand in Args_dic) ): 
			print('Error: Unrecognized subcommand. Valid ' +
                  'subcommands include: ')
			for subcommand in Args_dic:
				print( '\t' + subcommand )
			print()
			return parse_fail
		num_options = len( Args_dic[user_subcommand] )
		# No option supplied after subcommand
		if ( (len(Args) == 1) and (num_options != 0) ):
			print( 'Error: No options supplied. Valid ' +
                   'options include: ' )
			for option in Args_dic[user_subcommand]:
				print( '\t' + option + '\t' + 
                       Args_dic[user_subcommand][option] ) 
			print()
			return parse_fail
		# Subcommand valid, exit if subcommand has no options
		if ( num_options == 0 ):
			return parse_pass
		else: 
			# Organize user options into a list
			user_options = []
			for arg in Args[1:]:
				if ( '-' in arg ):
					user_options.append(arg)

	# Unrecognized Option	
	if ( subcommand_func ): #subcommand supported
		for user_option in user_options:	
			if ( not(user_option in Args_dic[user_subcommand]) ): 
				print( 'Error: Unrecognized option. Valid ' +
                       'options include: ')
				for option in Args_dic[user_subcommand]:
					print( '\t' + option + '\t' + 
                           Args_dic[user_subcommand][option] ) 
				print()
				return parse_fail
	else: # subcommand not supported 
		if ( not(user_option in Args_dic) ): 
			print( 'Error: Unrecognized option. Valid ' +
                   'options include: ' )
			for option in Args_dic:
				print( '\t' + option + '\t' + Args_dic[option] ) 
			print()
			return parse_fail

	# User input passes all checks	
	return parse_pass
## parseArgs ##


####################################################################################
# Commands                                                                         #
####################################################################################


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		exit                                                                       #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		quits the program                                                          #
#                                                                                  #
####################################################################################
def exitFunc(Args, zavDevice):
   sys.exit()
## exitFunc ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		help                                                                       #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		displays command info from manpage                                         #
#                                                                                  #
####################################################################################
def helpFunc(Args, zavDevice):
    display_help_info('manpage')
    return 
## helpFunc ##
    

####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		clear                                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		clears the python terminal                                                 #
#                                                                                  #
####################################################################################
def clearConsole(Args, zavDevice):
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)
    return 
## clearConsole ##


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
	# Local Variables                                                            #
	##############################################################################

	# Options Dictionary
	comports_inputs = { 
					   '-h' : 'Display help info',
					   '-l' : 'List available serial ports',
					   '-c' : 'Connect to a serial port',
					   '-d' : 'Disconnect from a serial port'
                      }
    
	# Maximum number of arguments
	max_args = 3

	# Command type -- subcommand function
	command_type = 'default'

	##############################################################################
	# Basic inputs parsing                                                       #
	##############################################################################
	parse_check = parseArgs(
                            Args,
                            max_args,
                            comports_inputs,
                            command_type 
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
		display_help_info( 'comports' )
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


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		ping                                                                       #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		transmit a byte over an active USB connection and await response from      # 
#       board                                                                      #
#                                                                                  #
####################################################################################
def ping( Args, zavDevice ):

    # Check for an active serial port connection and valid 
    # options/arguments
    if ( not zavDevice.is_active() ):
        print( "Error: no active serial port connection. "  +
               "Run the comports -c command to connect to " +
               "a device" )
        return 
    if   ( len(Args) < 1 ):
        print("Error: no options supplied to ping function")
        return 
    elif ( len(Args) > 2 ):
        print( "Error: too many options/arguments supplied " +
               "to ping function" )
    else:

        # Arguments parsing
        option = Args[0]
        timeout_supplied = False
        if ( len(Args) == 2 ):
            try:
                input_timeout = float( Args[1] )
                timeout_supplied = True
            except ValueError:
                print( "Error: Invalid ping timeout." )
                return 

        # Help option
        if ( option == "-h" ):
            display_help_info( 'ping' )
            return 

        # Ping option
        elif ( option == "-t" ):
            # Check for valid serial port connection
            if ( not zavDevice.is_active() ):
                print( "Error: no active serial port "    +
                       "connection. Run the comports -c " +
                       "command to connect to a device" )
                return 

            # Set timeout
            zavDevice.timeout = input_timeout
            zavDevice.configComport()

            # Ping
            opcode = b'\x01'
            ping_start_time = time.time()
            zavDevice.sendByte( opcode )
            print( "Pinging ..." )
            pingData = zavDevice.readbyte()
            if ( pingData == b'' ):
                print( "Timeout expired. No device " +
                       "response recieved." )
            else:
                ping_recieve_time = time.time()
                ping_time = ping_recieve_time - ping_start_time
                ping_time *= 1000.0
                if ( pingData in controller_codes ):
                    print( 
                           ("Response recieved at {0:1.4f} ms " +
                            "from {1}").format(
                                ping_time, 
                                controller_descriptions[pingData]
                                              )
                         )
                else:
                    print( 
                           ("Response recieved at {0:1.4f} ms " +
                           "from an unknown device").format(
                                                           ping_time
                                                           )
                         )
            return 

        # Ping option 
        else:
            print("Error: invalid option supplied to ping function")
            return 
## ping ##


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

	##############################################################################
	# local variables                                                            #
	##############################################################################
	opcode           = b'\x02'

	# Options Dictionary
	connect_inputs   = { 
					   '-h' : 'Display help info',
					   '-p' : 'Specify the connection serial port',
					   '-d' : 'Disconnect from active serial port'
                       }
    
	# Maximum number of arguments
	max_args         = 2

	# Command type -- subcommand function
	command_type     = 'default'

	# Firmware version
	firmware_version = None

	##############################################################################
	# Basic inputs parsing                                                       #
	##############################################################################
	parse_check = parseArgs(
                            Args,
                            max_args,
                            connect_inputs,
                            command_type 
                           )
	if ( not parse_check ):
		return # user inputs failed parse tests
	user_option = Args[0]
	if ( len(Args) > 1 ):
		user_port = Args[1]

	##############################################################################
	# Command-Specific Inputs Parsing                                            #
	##############################################################################

	# Check if there is an active serial port
	if ( zavDevice.is_active() and user_option == '-p' ):
		print("Error: Serial port " + zavDevice.comport + 
               "is active. Disconnect from the active" +
               " serial port before connecting" )
		return 
	elif ( (not zavDevice.is_active()) and user_option == '-d' ):
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
		if ( user_option == '-p' and
		     len(Args)   == 1):
			print( "Error: No serial port supplied " )
			return 

	##############################################################################
    # Help Option (-h)                                                           #
	##############################################################################
	if ( user_option == '-h' ):
		display_help_info( "connect" )
		return 

	##############################################################################
    # Port Option (-p)                                                           #
	##############################################################################
	elif ( user_option == '-p' ):
		# Open the serial comport
		comports( ['-c', user_port, '921600'], zavDevice )
		
		# Send the connect opcode 
		zavDevice.sendByte( opcode )

		# Get the board identifier 
		controller_response = zavDevice.readByte()
		if ( (controller_response == b''                    ) or
             (not (controller_response in controller_codes) ) ):
			print( "Controller connection was unsuccessful." )
			comports( ['-d'], zavDevice )
			return 
		else:
			# Get the firmware version 
			firmware_version = firmware_ids[zavDevice.readByte()]

			# Set global controller variable 
			zavDevice.set_controller(
						controller_descriptions[controller_response],
					    firmware_version	
									)

            # Display connection info									
			print( "Connection established with " + 
                    controller_descriptions[controller_response] )
			print( "Firmware: " + firmware_version )
			return 
		

	##############################################################################
    # Disconnect Option (-d)                                                     #
	##############################################################################
	elif ( user_option == '-d' ):
		comports( ['-d'], zavDevice )
		zavDevice.reset_controller()
		return 

	##############################################################################
    # Unknown Option                                                             #
	##############################################################################
	else:
		print( "Error: unknown option passed to connect " +
               "function" )	
		error_msg()
		return 
## connect ##


##################################################################################
# END OF FILE                                                                    #
##################################################################################