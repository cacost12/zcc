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




##################################################################################
# END OF FILE                                                                    #
##################################################################################