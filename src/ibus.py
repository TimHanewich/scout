from machine import UART

# Works by connecting to uart, transferring data and then disconnecting
# Allows ibus to be polled regularly without creating a block

# returns raw values
# To make meaningful there is a normalize static method 
# approx (-100 to +100) for default (standard) controls
# 0 is centre. The zero point can be adjusted on the controller
# actual value of min and maximum may differ
# approx (0 to 100) for dials


# Select appropriate uart pin (following are defaults)
# For ibus receive then only RX pin needs to be connected
# UART 0: TX pin 0 GP0 RX pin 1 GP1 
# UART 1: TX pin 6 GP4 RX pin 7 GP5 
# Connect appropriate RX pin to rightmost pin on FS-iA6B

# returns list of channel values. First value (pseudo channel 0) is status
# 0 = initial values
# 1 = new values
# -1 = failed to receive data old values sent
# -2 = checksum error


class IBus ():
    
    # Number of channels (FS-iA6B has 6)
    def __init__ (self, uart_num, baud=115200, num_channels=6):
        self.uart_num = uart_num
        self.baud = baud
        self.uart = UART(self.uart_num, self.baud)
        self.num_channels = num_channels
        # ch is channel value
        self.ch = []
        # Set channel values to 0
        for i in range (self.num_channels+1):
            self.ch.append(0)
            
            
    # Returns list with raw data
    def read(self):
        # Max 10 attempts to read
        for z in range(10):
            buffer = bytearray (31)
            char = self.uart.read(1)
            # check for 0x20
            if char == b'\x20':
                # read reset of string into buffer
                self.uart.readinto(buffer)
                checksum = 0xffdf # 0xffff - 0x20
                # check checksum
                for i in range(29):
                    checksum -= buffer[i]
                if checksum == (buffer[30] << 8) | buffer[29]:
                    # buffer[0] = 0x40
                    self.ch[0] = 1 # status 1 = success
                    for i in range (1, self.num_channels + 1):
                        self.ch[i] = (buffer[(i*2)-1] + (buffer[i*2] << 8))                    
                    return self.ch
                else:
                    # Checksum error
                    self.ch[0] = -2
            else:
                self.ch[0] = -1
                
        # Reach here then timed out
        self.ch[0] = -1
        return self.ch
    
    
    # Convert to meaningful values - eg. -100 to 100
    # Typical use for FS-iA6B
    # channel 1 to 4 use type="default" provides result from -100 to +100 (0 in centre)
    # channel 5 & 6 are dials type="dial" provides result from 0 to 100 
    # Note approx depends upon calibration etc.
    @staticmethod
    def normalize (value, type="default"):
        if (type == "dial"):
            return ((value - 1000) / 10)
        else:
            return ((value - 1500) / 5)
        
    
