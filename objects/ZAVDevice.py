####################################################################################
#                                                                                  #
# ZAVDevice.py -- ZAVDevice object, contains an interface for communicating with   #
#                 zenith avionics flight computers                                 #
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
import serial
import serial.tools.list_ports

# Project
import binUtil
import zavController
import sensor_conv


####################################################################################
# Globals                                                                          #
####################################################################################

# Flash Memory
FLASH_WRITE_ENABLED  = True
FLASH_WRITE_DISABLED = False


####################################################################################
# Objects                                                                          #
####################################################################################


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

    ################################################################################
    # General Methods                                                              #
    ################################################################################
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

	# Set the controller to enable board-specific commands
    def set_controller(self, controller_name, firmware_name = None ):
        self.controller = controller_name
        self.firmware   = firmware_name

	# Reset the controller to disable board-specific commands
    def reset_controller(self):
        self.controller    = None
        self.firmware_name = None

    # Execute a command using the current device connection
    def execute_command( self, command_callback, args ):
        command_callback( args, self )
    

    ################################################################################
    # Serial Port Configuration Methods                                            #
    ################################################################################

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
    

    ################################################################################
    # Serial Data Transmission Methods                                             #
    ################################################################################

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
    

    ################################################################################
    # Sensor Data Methods                                                          #
    ################################################################################

    # Converts an array of bytes into a dictionary containing the raw sensor 
    # readouts in integer format                                                 
    def getRawSensorReadouts( self, sensors, sensor_bytes ):

        # Sensor readout sizes
        sensor_size_dict = zavController.sensor_sizes[self.controller]

        # Starting index of bytes corresponding to individual 
        # sensor readout in sensor_bytes array
        index = 0

        # Result
        readouts = {}
        
        # Convert each sensor readout 
        for sensor in sensors:
            size             = sensor_size_dict[sensor]
            readout_bytes    = sensor_bytes[index:index+size]
            if ( zavController.sensor_formats[self.controller][sensor] == float ):
                sensor_val = binUtil.byte_array_to_float( readout_bytes )
            else:
                sensor_val = binUtil.byte_array_to_int(   readout_bytes )
            readouts[sensor] = sensor_val
            index           += size 

        return readouts
    ## getRawSensorReadouts ##


    # Converts raw sensor readouts in integer format into the appropriate format
    def convRawSensorReadouts( self, raw_readouts ):

        # Conversion functions
        conv_funcs = zavController.sensor_conv_funcs[self.controller]

        # Result
        readouts = {}

        # Convert each readout
        for sensor in raw_readouts:
            if ( conv_funcs[sensor] != None ):
                readouts[sensor] = conv_funcs[sensor]( raw_readouts[sensor] )
            else:
                readouts[sensor] = raw_readouts[sensor]
        
        return readouts
    ## convRawSensorReadouts ##


    # Converts a byte array into sensor readouts and converts digital readout
    def getSensorReadouts( self, sensors, sensor_bytes ):

        # Convert to integer form
        int_readouts = self.getRawSensorReadouts( sensors, sensor_bytes )

        # Make conversions
        readouts     = self.convRawSensorReadouts( int_readouts )
        return readouts
    ## getSensorReadouts ##


    # Formats a sensor readout into a label, rounded readout, and units 
    def formatSensorReadout( self, sensor, readout ):

        # Readout units
        units = zavController.sensor_units[self.controller][sensor] 

        # Rounded readout
        if ( units != None ):
            readout_str = "{:.3f}".format( readout )
        else:
            readout_str = str( readout )

        # Concatentate label, readout, and units
        if ( units != None ):
            output = sensor + ": " + readout_str + " " + units
        else:
            output = sensor + ": " + readout_str
        return output
    ## formatSensorReadout ##


    # Obtains a frame of sensor data from a controller's flash in byte format
    def getSensorFrameBytes( self ):

        # Determine the size of the frame
        frame_size = zavController.sensor_frame_sizes[self.controller]

        # Get bytes
        rx_bytes = self.readBytes( frame_size )
        return rx_bytes
    ## getSensorFrameBytes ##
    

    # Converts a list of sensor frames into measurements
    def getSensorFrames( self, sensor_frames_bytes, format = 'converted' ):

        # Convert to integer format
        sensor_frames_int = []
        for frame in sensor_frames_bytes:
            sensor_frame_int = []
            for sensor_byte in frame:
                sensor_frame_int.append( ord( sensor_byte ) )
            sensor_frames_int.append( sensor_frame_int )

        # Combine bytes from integer data and convert
        if ( format == 'converted'):
            sensor_frames = []
            for int_frame in sensor_frames_int:
                sensor_frame = []
                # Time of frame measurement
                time = ( ( int_frame[0]       ) + 
                        ( int_frame[1] << 8  ) + 
                        ( int_frame[2] << 16 ) +
                        ( int_frame[3] << 24 ) )
                # Conversion to seconds
                sensor_frame.append( sensor_conv.time_millis_to_sec( time ) )

                # Sensor readouts
                sensor_frame_dict = {}
                index = 4
                for i, sensor in enumerate( zavController.sensor_sizes[ self.controller ] ):
                    measurement = 0
                    float_bytes = []
                    for byte_num in range( zavController.sensor_sizes[self.controller][sensor] ):
                        if ( zavController.sensor_formats[self.controller][sensor] != float ):
                            measurement += ( int_frame[index + byte_num] << 8*byte_num )
                        else:
                            float_bytes.append( ( int_frame[index + byte_num] ).to_bytes(1, 'big' ) ) 
                    if ( zavController.sensor_formats[self.controller][sensor] == float ):
                        measurement = binUtil.byte_array_to_float( float_bytes )
                    sensor_frame_dict[sensor] = measurement
                    index += zavController.sensor_sizes[self.controller][sensor]
                sensor_vals_list = list( self.convRawSensorReadouts( sensor_frame_dict ).values() )
                for val in sensor_vals_list:
                    sensor_frame.append( val )
                sensor_frames.append( sensor_frame )
            return sensor_frames
        elif ( format == 'bytes' ):
            return sensor_frames_int 
    ## getSensorFrame ##

    ################################################################################
    # Misc                                                                         #
    ################################################################################

    # Enable/Disbale writing to flash
    def flashWriteEnable( self ):
        self.flash_write_enabled = FLASH_WRITE_ENABLED

    def flashWriteDisable( self ):
        self.flash_write_enabled = FLASH_WRITE_DISABLED

    def getFlashWriteProtection( self ):
        return self.flash_write_enabled

## class ZAVDevice ##


####################################################################################
# END OF FILE                                                                      #
####################################################################################