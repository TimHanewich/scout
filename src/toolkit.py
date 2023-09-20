import struct
import sys
import math
import io

def float_to_bytes(f:float) -> bytes:
    b = struct.pack("f", f)
    return b

def bytes_to_float(bs:bytes) -> float:
    return struct.unpack("f", bs)[0]

class ControlCommand:

    def __init__(self) -> None:

        # variables
        self.frame:int = 0
        self.throttle:float = 0.0 # desired throttle, as a percentage (between 0.0 and 1.0)
        self.roll:float = 0.0 # desired roll, as a percentage (between -1.0 and 1.0)
        self.pitch:float = 0.0 # desired pitch, as a percentage (between -1.0 and 1.0)
        self.yaw:float = 0.0 # desired yaw rotation speed, as a percentage (between -1.0 and 1.0). Note that this is UNLIKE pitch and roll. Because pitch and roll are set angles. But this is not a set position, but a rate of movement.
        
        # final variable - check sum (to ensure there aren't transmission errors). This is NOT included in the checksum calculation, but it IS included in the encoded bytes
        self.checksum:float = 0.0


    def calculate_checksum(self) -> float:
        ToReturn:float = 0.0
        ToReturn = ToReturn + float(self.frame)
        ToReturn = ToReturn + self.throttle
        ToReturn = ToReturn + self.roll
        ToReturn = ToReturn + self.pitch
        ToReturn = ToReturn + self.yaw
        return ToReturn

    def checksum_correct(self, tolerance:float = 0.00001) -> bool:
        """
        Determines if the checksum that is saved in the checksum variable is correct, according to the variables.
        :param tolerance: If the difference between the decoded checksum (class variable) and the calculated checksum is below this level, they are considered equal. We must do this due to rounding errors when encoding/decoding floating point numbers.
        """
        diff:float = abs(self.checksum - self.calculate_checksum())
        return diff < tolerance

    def encode(self) -> bytes:

        # Encoded format (in bytes)
        # frame:int (4 bytes)
        # throttle:float (4 bytes)
        # roll:float (4 bytes)
        # pitch:float (4 bytes)
        # yaw:float (4 bytes)
        # checksum:float (4 bytes)
        # total bytes: 24

        ToReturn:bytearray = bytearray()
        
        # frame (int to 4 bytes)
        # we have to do it differetnly by platform because micropython on the raspberry pi handles it differently
        if sys.platform == "rp2":
            frame_bytes = self.frame.to_bytes(4, 0)
        else:
            frame_bytes = self.frame.to_bytes(4, byteorder='big')
        for b in frame_bytes:
            ToReturn.append(b)

        # throttle, roll, pitch
        ToReturn.extend(float_to_bytes(self.throttle))
        ToReturn.extend(float_to_bytes(self.roll))
        ToReturn.extend(float_to_bytes(self.pitch))
        ToReturn.extend(float_to_bytes(self.yaw))

        # check sum
        ToReturn.extend(float_to_bytes(self.calculate_checksum()))

        return bytes(ToReturn)

    def decode(self, bs:bytes) -> None:

        # frame
        if sys.platform == "rp2":
            self.frame = int.from_bytes(bs[0:4], 0)
        else:
            self.frame = int.from_bytes(bs[:4], byteorder='big')

        # roll and pitch
        self.throttle = bytes_to_float(bs[4:8])
        self.roll = bytes_to_float(bs[8:12])
        self.pitch = bytes_to_float(bs[12:16])
        self.yaw = bytes_to_float(bs[16:20])

        # check sunm
        self.checksum = bytes_to_float(bs[20:24])

class PIDCommand:

    def __init__(self) -> None:
        
        self.axis:int = 0 # 0 = roll, 1 = pitch, 2 = yaw
        self.kp:float = 0.0
        self.ki:float = 0.0
        self.kd:float = 0.0

    def encode(self) -> bytes:
        ToReturn = bytearray()
        ToReturn.append(self.axis)
        ToReturn.extend(float_to_bytes(self.kp))
        ToReturn.extend(float_to_bytes(self.ki))
        ToReturn.extend(float_to_bytes(self.kd))
        return bytes(ToReturn)
    
    def decode(self, bs:bytes) -> None:
        self.axis = bs[0]
        self.kp = bytes_to_float(bs[1:5])
        self.ki = bytes_to_float(bs[5:9])
        self.kd = bytes_to_float(bs[9:13])

class TelemetryFrame:

    def __init__(self) -> None:

        self.time:int = 0 # the time stamp (ticks), in milliseconds

        # raw values
        self.accel_x:float = 0.0
        self.accel_y:float = 0.0
        self.accel_z:float = 0.0
        self.gyro_x:float = 0.0
        self.gyro_y:float = 0.0
        self.gyro_z:float = 0.0

        # calculated values
        self.pitch_angle:float = 0.0
        self.roll_angle:float = 0.0



    def encode(self) -> bytes:

        ToReturn:bytearray = bytearray()

        # add the time (int)
        if sys.platform == "rp2":
            for b in self.time.to_bytes(4, 0):
                ToReturn.append(b)
        else:
            for b in self.time.to_bytes(4, byteorder='big'):
                ToReturn.append(b)

        # add the readings
        ToReturn.extend(float_to_bytes(self.accel_x))
        ToReturn.extend(float_to_bytes(self.accel_y))
        ToReturn.extend(float_to_bytes(self.accel_z))
        ToReturn.extend(float_to_bytes(self.gyro_x))
        ToReturn.extend(float_to_bytes(self.gyro_y))
        ToReturn.extend(float_to_bytes(self.gyro_z))
        ToReturn.extend(float_to_bytes(self.pitch_angle))
        ToReturn.extend(float_to_bytes(self.roll_angle))

        return bytes(ToReturn)
    
    def decode(self, data:bytes) -> bytes:

        if len(data) != len(self.encode()):
            raise Exception("Unable to decode: the input data was not correct.")
        

        # time (first 4 bytes)
        if sys.platform == "rp2":
            self.time = int.from_bytes(data[0:4], 0)
        else:
            self.time = int.from_bytes(data[0:4], byteorder='big')

        self.accel_x = bytes_to_float(data[4:8])
        self.accel_y = bytes_to_float(data[8:12])
        self.accel_z = bytes_to_float(data[12:16])
        self.gyro_x = bytes_to_float(data[16:20])
        self.gyro_y = bytes_to_float(data[20:24])
        self.gyro_z = bytes_to_float(data[24:28])
        self.pitch_angle = bytes_to_float(data[28:32])
        self.roll_angle = bytes_to_float(data[32:36])
        

    def save(self, opened_file:io.BufferedWriter = None) -> None:
        """Appends the frame, in bytes, to the 'telemetry' file in the root directory."""
        
        if opened_file == None:
            f = open("telemetry", "ab")
            f.write(self.encode())
            f.close()
        else:
            opened_file.write(self.encode())

    
    @staticmethod
    def encode_frames(frames:list["TelemetryFrame"]) -> bytes:
        ToReturn:bytearray = bytearray()
        for frame in frames:
            for b in frame.encode():
                ToReturn.append(b)
        return bytes(ToReturn)
    
    @staticmethod
    def decode_frames(data:bytes) -> list["TelemetryFrame"]:

        frame_length:int = len(TelemetryFrame().encode()) # the length, in bytes, of a telemtry frame

        begin:int = 0
        end:int = frame_length

        ToReturn:list[TelemetryFrame] = []
        while end <= len(data):
            tf = TelemetryFrame()
            tf.decode(data[begin:end])
            ToReturn.append(tf)
            begin = begin + frame_length
            end = end + frame_length

        return ToReturn




    def add_float_bytes(self, ba:bytearray, f:float) -> None:
        for b in struct.pack("f", f):
            ba.append(b)


class NonlinearTransformer:
    """Converts a linear input to a nonlinear output (dampening) using tanh and a dead zone."""
    

    def __init__(self, nonlinearity_strength:float = 2.0, dead_zone_percent:float = 0.0) -> None:
        """
        Creates a new NonlinearTransformer.
        :param nonlinearity_strength: How strong you want the nonlinearity to be. 0.0 = perfectly linear, 5.0 = strongly nonlinear. Generally, 1.5-2.5 is a good bet.
        :param dead_zone_percent: The input percent to ignore before beginning to return values (any input less than this would result in 0.0).
        """

        # calculate multiplier
        self.multiplier = nonlinearity_strength

        # set dead zone
        self.dead_zone_percent = dead_zone_percent

    def y(self, x:float) -> float:
        return math.tanh(self.multiplier * (x - 1)) + 1

    def _transform(self, percent:float) -> float:

        # account for dead zone
        x:float = (percent - self.dead_zone_percent) / (1.0 - self.dead_zone_percent) # account for dead zone
        x = max(x, 0) # cannot be less than 0.0
        x = min(x, 1.0) # cannot be more than 1.0

        # determine the range we have to work with (minimum is tanh intersect at 0.0 x)
        min_y:float = self.y(0)
        max_y:float = 1.0 # intersect will always be at exactly (1, 1) based on the tanh equation I have set up
    
        # calculate and scale to within the min and max range
        ToReturn:float = self.y(x)
        ToReturn = (ToReturn - min_y) / (max_y - min_y)
        return ToReturn
    
    def transform(self, percent:float) -> float:
        """Convert linear input to nonlinear output."""
        if percent >= 0:
            return self._transform(percent)
        else:
            return (self._transform(abs(percent)) * -1)
        


def log(msg:str) -> None:
    fp = "/logs"
    f = open(fp, "a")
    f.write(msg + "\n\n")
    f.close()