####################################################################################
#                                                                                  #
# controller.py -- Contains global variables with SDR controller information       #
# Author: Colton Acosta                                                            #
# Date: 7/30/2023                                                                  #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################
import sensor_conv


####################################################################################
# Global Variables                                                                 #
####################################################################################


# Controller identification codes
controller_codes = [ 
                  b'\x01', # Base Flight Computer,            Rev 1.0
                  b'\x02', # Full Flight Computer ,           Rev 1.0 
                  b'\x03', # Legacy SDR Flight Computer,      Rev 1.0 
                  b'\x04'  # Legacy SDR Flight Computer Lite, Rev 1.0
                   ]

# Controller Names
controller_names = [
                    "Base Flight Computer (A0001 Rev 1.0)"        ,
                    "Full Feature Flight Computer (A0002 Rev 1.0)",
                    "Legacy SDR Flight Computer (A0003 Rev 1.0)"  ,
                    "Legacy SDR Flight Computer Lite (A0004 Rev 1.0)"
                   ]

# Controller descriptions from identification codes
controller_descriptions = {
                    b'\x01': "Base Flight Computer (A0001 Rev 1.0)"        ,
                    b'\x02': "Full Feature Flight Computer (A0002 Rev 1.0)",
                    b'\x03': "Legacy SDR Flight Computer (A0003 Rev 1.0)"  ,
                    b'\x04': "Legacy SDR Flight Computer Lite (A0004 Rev 1.0)"
                        }

# Lists of sensors on each controller
controller_sensors = {
                # Base Flight Computer Rev 1.0
                controller_names[0]: {
                           "pres" : "Barometric Pressure   ",
                           "temp" : "Barometric Temperature",
                           "vbat" : "Battery Voltage"
                           },

                # Full Feature Flight Computer rev 1.0
                controller_names[1]: {
                           "accX" : "Accelerometer X       ",
                           "accY" : "Accelerometer Y       ",
                           "accZ" : "Accelerometer Z       ",
                           "gyroX": "gyroscope X           ",
                           "gyroY": "gyroscope Y           ",
                           "gyroZ": "gyroscope Z           ",
                           "magX" : "Magnetometer X        ",
                           "magY" : "Magnetometer Y        ",
                           "magZ" : "Magnetometer Z        ",
                           "imut" : "IMU Die Temperature   ",
                           "pres" : "Barometric Pressure   ",
                           "temp" : "Barometric Temperature",
                           "vbat" : "Battery Voltage"
                           },

                # Legacy SDR Flight Computer rev 1.0
                controller_names[2]: {
                           "accX" : "Accelerometer X       ",
                           "accY" : "Accelerometer Y       ",
                           "accZ" : "Accelerometer Z       ",
                           "gyroX": "gyroscope X           ",
                           "gyroY": "gyroscope Y           ",
                           "gyroZ": "gyroscope Z           ",
                           "magX" : "Magnetometer X        ",
                           "magY" : "Magnetometer Y        ",
                           "magZ" : "Magnetometer Z        ",
                           "imut" : "IMU Die Temperature   ",
                           "pres" : "Barometric Pressure   ",
                           "temp" : "Barometric Temperature",
                           },

                # Legacy SDR Flight Computer Lite rev 1.0 
                controller_names[3]: {
                           "pres" : "Barometric Pressure   ",
                           "temp" : "Barometric Temperature",
                           }

                     }

# Size of raw sensor readouts in bytes
sensor_sizes = {
                # Base Flight Computer rev 1.0
                controller_names[0]: {
                           "pres" : 4,
                           "temp" : 4,
                           "vbat" : 4
                           },

                # Full Feature Flight Computer rev 1.0
                controller_names[1]: {
                           "accX" : 2,
                           "accY" : 2,
                           "accZ" : 2,
                           "gyroX": 2,
                           "gyroY": 2,
                           "gyroZ": 2,
                           "magX" : 2,
                           "magY" : 2,
                           "magZ" : 2,
                           "imut" : 2,
                           "pres" : 4,
                           "temp" : 4,
                           "vbat" : 4
                           },

                # Legacy SDR Flight Computer rev 1.0
                controller_names[2]: {
                           "accX" : 2,
                           "accY" : 2,
                           "accZ" : 2,
                           "gyroX": 2,
                           "gyroY": 2,
                           "gyroZ": 2,
                           "magX" : 2,
                           "magY" : 2,
                           "magZ" : 2,
                           "imut" : 2,
                           "pres" : 4,
                           "temp" : 4 
                           },

                # Base Flight Computer rev 1.0
                controller_names[3]: {
                           "pres" : 4,
                           "temp" : 4
                           }

               }

# Sensor poll codes
sensor_codes = {
                # Base Flight Computer Rev 1.0
                controller_names[0]: {
                           "pres" : b'\x00',
                           "temp" : b'\x01',
                           "vbat" : b'\x02'
                           },

                # Full Feature Flight Computer rev 1.0
                controller_names[1]: {
                           "accX" : b'\x00',
                           "accY" : b'\x01',
                           "accZ" : b'\x02',
                           "gyroX": b'\x03',
                           "gyroY": b'\x04',
                           "gyroZ": b'\x05',
                           "magX" : b'\x06',
                           "magY" : b'\x07',
                           "magZ" : b'\x08',
                           "imut" : b'\x09',
                           "pres" : b'\x0A',
                           "temp" : b'\x0B',
                           "vbat" : b'\x0C'
                           },

                # Legacy SDR Flight Computer rev 1.0
                controller_names[2]: {
                           "accX" : b'\x00',
                           "accY" : b'\x01',
                           "accZ" : b'\x02',
                           "gyroX": b'\x03',
                           "gyroY": b'\x04',
                           "gyroZ": b'\x05',
                           "magX" : b'\x06',
                           "magY" : b'\x07',
                           "magZ" : b'\x08',
                           "imut" : b'\x09',
                           "pres" : b'\x0A',
                           "temp" : b'\x0B' 
                           },

                # Legacy Flight Computer Lite Rev 1.0
                controller_names[3]: {
                           "pres" : b'\x00',
                           "temp" : b'\x01' 
                           },
               }

# Size of a frame of data in flash memory
sensor_frame_sizes = {
                    # Base Flight Computer rev 1.0
                    controller_names[0]: 16,

                    # Full Feature Flight Computer rev 1.0
                    controller_names[1]: 36,

                    # Legacy SDR Flight Computer rev 1.0
                    controller_names[2]: 32,

                    # Legacy SDR Flight Computer Lite rev 1.0
                    controller_names[3]: 12,
                     }

# Sensor raw readout conversion functions
sensor_conv_funcs = {
                # Base Flight Computer rev 1.0
                controller_names[0]: {
                           "pres" : sensor_conv.baro_press,
                           "temp" : sensor_conv.baro_temp ,
                           "vbat" : sensor_conv.adc_readout_to_voltage
                           },

                # Full Feature Flight Computer rev 1.0
                controller_names[1]: {
                           "accX" : sensor_conv.imu_accel,
                           "accY" : sensor_conv.imu_accel,
                           "accZ" : sensor_conv.imu_accel,
                           "gyroX": sensor_conv.imu_gyro,
                           "gyroY": sensor_conv.imu_gyro,
                           "gyroZ": sensor_conv.imu_gyro,
                           "magX" : None                  ,
                           "magY" : None                  ,
                           "magZ" : None                  ,
                           "imut" : None                  ,
                           "pres" : sensor_conv.baro_press,
                           "temp" : sensor_conv.baro_temp ,
                           "vbat" : sensor_conv.adc_readout_to_voltage
                           },

                # Legacy SDR Flight Computer rev 1.0
                controller_names[2]: {
                           "accX" : sensor_conv.imu_accel,
                           "accY" : sensor_conv.imu_accel,
                           "accZ" : sensor_conv.imu_accel,
                           "gyroX": sensor_conv.imu_gyro,
                           "gyroY": sensor_conv.imu_gyro,
                           "gyroZ": sensor_conv.imu_gyro,
                           "magX" : None                  ,
                           "magY" : None                  ,
                           "magZ" : None                  ,
                           "imut" : None                  ,
                           "pres" : sensor_conv.baro_press,
                           "temp" : sensor_conv.baro_temp 
                           },

                # Legacy SDR Flight Computer Lite rev 1.0
                controller_names[3]: {
                           "pres" : sensor_conv.baro_press,
                           "temp" : sensor_conv.baro_temp 
                           },
                    }

# Sensor readout units
sensor_units = {
                # Base Flight Computer rev 1.0
                controller_names[0]: {
                           "pres" : "kPa",
                           "temp" : "C"  ,
                           "vbat" : "V"
                           },

                # Full Flight Computer rev 1.0
                controller_names[1]: {
                           "accX" : "m/s/s",
                           "accY" : "m/s/s",
                           "accZ" : "m/s/s",
                           "gyroX": "deg/s",
                           "gyroY": "deg/s",
                           "gyroZ": "deg/s",
                           "magX" : None   ,
                           "magY" : None   ,
                           "magZ" : None   ,
                           "imut" : None   ,
                           "pres" : "kPa"  ,
                           "temp" : "C"    ,
                           "vbat" : "V"
                           },

                # Legacy SDR Flight Computer rev 1.0
                controller_names[2]: {
                           "accX" : "m/s/s",
                           "accY" : "m/s/s",
                           "accZ" : "m/s/s",
                           "gyroX": "deg/s",
                           "gyroY": "deg/s",
                           "gyroZ": "deg/s",
                           "magX" : None   ,
                           "magY" : None   ,
                           "magZ" : None   ,
                           "imut" : None   ,
                           "pres" : "kPa",
                           "temp" : "C" 
                           },

                # Legacy SDR Flight Computer rev 1.0
                controller_names[3]: {
                           "pres" : "kPa",
                           "temp" : "C" 
                           }
               }

# Inidices of sensors in output file 
sensor_indices = {
                # Base Flight Computer rev 1.0
                controller_names[0]: {
                            "pres" : 1,
                            "temp" : 2, 
                            "vbat" : 3
                                     },

                # Full Feature Flight Computer rev 1.0
                controller_names[1]: {
                            "accX" : 1,
                            "accY" : 2,
                            "accZ" : 3,
                            "gyroX": 4,
                            "gyroY": 5,
                            "gyroZ": 6,
                            "magX" : 7,
                            "magY" : 8,
                            "magZ" : 9,
                            "imut" : 10,
                            "pres" : 11,
                            "temp" : 12,
                            "vbat" : 13
                                       },
                # Legacy SDR Flight Computer rev 1.0
                controller_names[2]: {
                            "accX" : 1,
                            "accY" : 2,
                            "accZ" : 3,
                            "gyroX": 4,
                            "gyroY": 5,
                            "gyroZ": 6,
                            "magX" : 7,
                            "magY" : 8,
                            "magZ" : 9,
                            "imut" : 10,
                            "pres" : 11,
                            "temp" : 12 
                                       },
                # Legacy SDR Flight Computer Lite rev 1.0
                controller_names[3]: {
                            "pres" : 1,
                            "temp" : 2 
                                     }
                }

# Sensor raw readout formats
sensor_formats = {
                # Base Flight Computer rev 1.0
                controller_names[0]: {
                           "pres" : float,
                           "temp" : float,
                           "vbat" : float
                           },
                # Full Feature Flight Computer rev 1.0
                controller_names[1]: {
                           "accX" : int  ,
                           "accY" : int  ,
                           "accZ" : int  ,
                           "gyroX": int  ,
                           "gyroY": int  ,
                           "gyroZ": int  ,
                           "magX" : int  ,
                           "magY" : int  ,
                           "magZ" : int  ,
                           "imut" : int  ,
                           "pres" : float,
                           "temp" : float,
                           "vbat" : float
                           },

                # Legacy SDR Flight Computer rev 1.0
                controller_names[2]: {
                           "accX" : int  ,
                           "accY" : int  ,
                           "accZ" : int  ,
                           "gyroX": int  ,
                           "gyroY": int  ,
                           "gyroZ": int  ,
                           "magX" : int  ,
                           "magY" : int  ,
                           "magZ" : int  ,
                           "imut" : int  ,
                           "pres" : float,
                           "temp" : float 
                           },

                # Leacy SDR Flight Computer Lite rev 1.0
                controller_names[3]: {
                           "pres" : float,
                           "temp" : float 
                           }
                 }

# Firmware Ids
firmware_ids = {
                b'\x01': "Terminal"   ,
				b'\x02': "Data Logger",
				b'\x03': "Dual Deploy"
               }
			

##################################################################################
# END OF FILE                                                                    #
##################################################################################