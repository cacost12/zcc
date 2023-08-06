####################################################################################
#                                                                                  #
# ping.py -- ping command, pings the connect device to test responsiveness and     #
#            provide basic device information                                      #
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
import messageUtil
import zavController


####################################################################################
# Procedures                                                                       #
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
            messageUtil.display_help_info( 'ping' )
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
            pingData = zavDevice.readByte()
            if ( pingData == b'' ):
                print( "Timeout expired. No device " +
                       "response recieved." )
            else:
                ping_recieve_time = time.time()
                ping_time = ping_recieve_time - ping_start_time
                ping_time *= 1000.0
                if ( pingData in zavController.controller_codes ):
                    print( 
                           ("Response recieved at {0:1.4f} ms " +
                            "from {1}").format(
                                ping_time, 
                                zavController.controller_descriptions[pingData]
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