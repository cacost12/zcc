####################################################################################
#                                                                                  #
# zcc.py -- main terminal program. Contains main program                           #
#            loop and global objects                                               #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 7/30/2023                                                                  #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################

# Standard
import serial
import serial.tools.list_ports
import sys
import time

# Setup project directory structure
sys.path.insert( 0, './commands')
sys.path.insert( 0, './objects' )
sys.path.insert( 0, './util'    )

# General Project
import config  
import validator
import ZAVDevice

# Commands
import clear
import comports
import connect
import exitCommand
import flash
import helpCommand
import ignite
import ping
import sensor
import dualDeploy


####################################################################################
# Global Variables                                                                 #
####################################################################################

# List of terminal commands
command_callbacks = { 
                "exit"       : exitCommand.exitFunc,
                "help"       : helpCommand.helpFunc,
                "clear"      : clear.clearConsole  ,
                "comports"   : comports.comports   ,
                "ping"       : ping.ping           ,
                "connect"    : connect.connect     ,
                "ignite"     : ignite.ignite       ,
                "flash"      : flash.flash         ,
                "sensor"     : sensor.sensor       ,
                "dual-deploy": dualDeploy.dual_deploy
                }

# Display Constants
TERMINAL_PROMPT              = "ZCC> "
UNRECOGNIZED_COMMAND_MESSAGE = "Error: Unsupported command"


####################################################################################
# Application Entry Point                                                          #
####################################################################################
if __name__ == '__main__':
    
    # Initialize Serial Port Object
    zavDevice = ZAVDevice.ZAVDevice()

    # Look for possible connections
    avail_ports = serial.tools.list_ports.comports()
    for port_num, port in enumerate( avail_ports ):
        if ( 'CP2102' in port.description ):
            # Connect
            port_num = port.device
            connect_args  = [ '-p', port_num]
            connect.connect( connect_args, zavDevice )
            
    # Display command prompt
    while( True ):
        # Command prompt
        userin         = input( TERMINAL_PROMPT )

        # Parse command
        userinCleaned = validator.parseInput( userin )
        command       = userinCleaned[0]
        args          = userinCleaned[1:]

        # Execute Command
        zavDevice.execute_command( command_callbacks[command], args )

## main ##


####################################################################################
# END OF FILE                                                                      #
####################################################################################