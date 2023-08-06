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
import comports
from   config      import *
from   zavController  import *
import validator


####################################################################################
# Global Variables                                                                 #
####################################################################################

# Serial port timeouts
if ( zav_debug ):
	default_timeout = 100 # 100 second timeout
else:
	default_timeout = 1   # 1 second timeout


####################################################################################
# Commands                                                                         #
####################################################################################



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
	parse_check = validator.parseArgs(
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
		comports.comports( ['-c', user_port, '921600'], zavDevice )
		
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