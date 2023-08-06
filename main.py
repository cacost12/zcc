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
# Standard Imports                                                                 #
####################################################################################
import time
import serial
import serial.tools.list_ports
import sys


####################################################################################
# Project Modules                                                                  #
####################################################################################

sys.path.insert( 0, './commands')

import commands         # general terminal commands
import hw_commands      # general hardware commands
import flash
import ignite
import sensor
import flightComputer   # flight computer commands
from   config import *  # global settings


####################################################################################
# Global Variables                                                                 #
####################################################################################

# List of terminal commands
command_callbacks = { 
                "exit"       : commands.exitFunc                ,
                "help"       : commands.helpFunc                ,
                "clear"      : commands.clearConsole            ,
                "comports"   : commands.comports                ,
                "ping"       : commands.ping                    ,
                "connect"    : commands.connect                 ,
                "ignite"     : ignite.ignite                    ,
                "flash"      : flash.flash                      ,
                "sensor"     : sensor.sensor                    ,
                "dual-deploy": flightComputer.dual_deploy
                }

# Display Constants
TERMINAL_PROMPT              = "ZCC> "
UNRECOGNIZED_COMMAND_MESSAGE = "Error: Unsupported command"

# Flash Memory
FLASH_WRITE_ENABLED  = True
FLASH_WRITE_DISABLED = False


####################################################################################
#                                                                                  #
# OBJECT:                                                                          #
# 		ZAVDevice                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
#       Interface to zenith controller using serial port                           #
# 		serial port user API and handler for passing data                          #
#       between command functions                                                  #
#                                                                                  #
####################################################################################
class ZAVDevice:
    def __init__( self ):
        self.baudrate            = None
        self.comport             = None
        self.timeout             = None
        self.serialObj           = serial.Serial()
        self.config_status       = False 
        self.controller          = None
        self.firmware            = None
        self.flash_write_enabled = False 
        self.sensor_readouts     = {}

    # Initialize Serial Port
    def initComport(self, baudrate, comport, timeout):
        self.baudrate            = baudrate 
        self.comport             = comport 
        self.timeout             = timeout 
        self.serialObj.baudrate  = self.baudrate
        self.serialObj.port      = self.comport
        self.serialObj.timeout   = self.timeout
        self.config_status       = True

    # Configure Serial port from class attributes
    def configComport(self):
        self.serialObj.baudrate = self.baudrate
        self.serialObj.port     = self.comport
        self.serialObj.timeout  = self.timeout

    # Open the serial port
    # returns a boolean variable indicating whether the port
    # connection was sucessful
    def openComport(self):

        # Ensure serial port has been properly configured 
        if(not self.config_status):
            print("Error: Cannot open serial port. Serial " +
                  "port has not been properly configured")
            return False

        # open port
        self.serialObj.open()
        return True

    # Close the serial port
    # Returns a boolean value indicating whether the port connection was 
    # successfully closed
    def closeComport(self):
        # check that the serial port is open
        if (not self.serialObj.is_open):
            print("No open serial port detected")
            return False
        else:
            self.serialObj.close()
            return True

	# Check if serial port is active
    def is_active(self):
        return self.serialObj.is_open

	# List available serial port connections
    def list_ports(self):
	    available_ports = serial.tools.list_ports.comports()
	    available_port_names = []
	    for port in available_ports:
		    available_port_names.append(port.device)
	    return available_port_names

    # Write a single Byte to the serial port
    def sendByte(self, byte):
        if (not self.serialObj.is_open):
            print("Error: Could not transmit byte over serial port. No active" \
                   +"serial port connection")
        else:
            self.serialObj.write(byte)

    # Write an array of bytes to the serial port 
    def sendBytes(self, byte_array):
        if (not self.serialObj.is_open):
            print("Error: Could not transmit byte over serial port. No active" \
                   +"serial port connection")
        else:
            self.serialObj.write( byte_array )

    # Read a single Byte from the serial port
    def readByte(self):
        if (not self.serialObj.is_open):
            print("Error: Could not read byte from serial port. No active" \
                   +"serial port connection")
        else:
             return self.serialObj.read()

    # Read multiple bytes from the serial port
    def readBytes( self, num_bytes ):
        if (not self.serialObj.is_open):
            print("Error: Could not read byte from serial port. No active" \
                   +"serial port connection")
        else:
            rx_bytes = []
            for i in range( num_bytes ):
                rx_bytes.append( self.serialObj.read() )
            return rx_bytes 

	# Set the controller to enable board-specific commands
    def set_controller(self, controller_name, firmware_name = None ):
        self.controller = controller_name
        self.firmware   = firmware_name

	# Reset the controller to disable board-specific commands
    def reset_controller(self):
        self.controller    = None
        self.firmware_name = None

    # Execute a command using the current device connection
    def execute_command( self, command, args ):
        command_callbacks[command]( args, self )

    # Enable/Disbale writing to flash
    def flashWriteEnable( self ):
        self.flash_write_enabled = FLASH_WRITE_ENABLED

    def flashWriteDisable( self ):
        self.flash_write_enabled = FLASH_WRITE_DISABLED

    def getFlashWriteProtection( self ):
        return self.flash_write_enabled

## class ZAVDevice ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		parseInput                                                                 #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		checks user input against command list options                             #
#                                                                                  #
####################################################################################
def parseInput( userin ): 

    # Get rid of any whitespace
    userin.strip()

    # Split the input into commands and arguments
    userin = userin.split() 
    try:
        userCommand = userin[0]
        CommandArgs = userin[1:] 
    except TypeError:
        print( UNRECOGNIZED_COMMAND_MESSAGE )
        userin = input( TERMINAL_PROMPT )
        parseInput(userin)

    # Check if user input corresponds to a function
    for command in command_callbacks: 
        if userCommand == command:
           return userin

    # User input doesn't correspond to a command
    print( UNRECOGNIZED_COMMAND_MESSAGE )
    userin = input( TERMINAL_PROMPT )
    return parseInput(userin)
## parseInput ##


####################################################################################
# Application Entry Point                                                          #
####################################################################################
if __name__ == '__main__':
    
    # Initialize Serial Port Object
    zavDevice = ZAVDevice()

    # Look for possible connections
    avail_ports = serial.tools.list_ports.comports()
    for port_num, port in enumerate( avail_ports ):
        if ( 'CP2102' in port.description ):
            # Connect
            port_num = port.device
            connect_args  = [ '-p', port_num]
            commands.connect( connect_args, zavDevice )
            
    # Display command prompt
    while( True ):
        # Command prompt
        userin         = input( TERMINAL_PROMPT )

        # Parse command
        userin_clean   = parseInput( userin )
        userCommand    = userin_clean[0]
        userArgs       = userin_clean[1:]

        # Execute Command
        zavDevice.execute_command( userCommand, userArgs )
## parseInput ##


####################################################################################
# END OF FILE
####################################################################################