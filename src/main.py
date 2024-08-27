"""
The Scout Flight Controller
by Tim Hanewich - github.com/TimHanewich
For more information: https://github.com/TimHanewich/scout

Copyright 2023 Tim Hanewich
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

########################################
###########  SETTINGS  #################
########################################

# Motor GPIO's (not pin number, GPIO number) ###
gpio_motor1 = 2 # front left, clockwise
gpio_motor2 = 28 # front right, counter clockwise
gpio_motor3 = 15 # rear left, counter clockwise
gpio_motor4 = 16 # rear right, clockwise

# i2c pins used for MPU-6050
gpio_i2c_sda = 12
gpio_i2c_scl = 13

# RC-receiver UART
# either a 0 or 1 (Raspberry Pi Pico supports two UART interfaces)
rc_uart = 1

# throttle settings
throttle_idle:float = 0.14 # the minumum throttle needed to apply to the four motors for them all to spin up, but not provide lift (idling on the ground). the only way to find this value is through testing (with props off).
throttle_governor:float = 0.22 # the maximum throttle that can be applied. So, if the pilot is inputting 100% on the controller, it will max out at this. And every value below the pilot's 100% will be scaled linearly within the range of the idle throttle seen above and this governor throttle. If you do not wish to apply a governor (not recommended), set this to None.

# Max attitude rate of change rates (degrees per second)
max_rate_roll:float = 30.0 # roll
max_rate_pitch:float = 30.0 # pitch
max_rate_yaw:float = 50.0 # yaw

# Desired Flight Controller Cycle time
# This is the number of times per second the flight controller will perform an adjustment loop (PID loop)
target_cycle_hz:float = 250.0

# PID Controller values
pid_roll_kp:float = 0.00043714285
pid_roll_ki:float = 0.00255
pid_roll_kd:float = 0.00002571429
pid_pitch_kp:float = pid_roll_kp
pid_pitch_ki:float = pid_roll_ki
pid_pitch_kd:float = pid_roll_kd
pid_yaw_kp:float = 0.001714287
pid_yaw_ki:float = 0.003428571
pid_yaw_kd:float = 0.0

########################################
########################################
########################################

import machine
import time
import ibus
import toolkit

# THE FLIGHT CONTROL LOOP
def run() -> None:
    
    print("Hello from Scout!")

    # flash the LED a few times to show the microcontroller has received power and the program is active
    led = machine.Pin(25, machine.Pin.OUT) # the onboard LED of the Raspberry Pi Pico
    for x in range(8):
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)

    # wait a few seconds for the IMU to settle
    print("Waiting 3 seconds for the IMU to settle...")
    time.sleep(3)

    # overclock
    machine.freq(250000000)
    print("Overclocked to 250,000,000")

    # set up RC receiver
    rc:ibus.IBus = ibus.IBus(rc_uart)
    print("RC receiver set up")

    # check that flight mode is not on when we are first starting - it needs to be set into standby mode
    # this is a safety check. Prevents from the drone taking off (at least spinning props) as soon as power is plugged in
    print("Validating that mode switch is not in flight position...")
    for x in range(0, 60):
        rc_data = rc.read()
        if rc_data[5] == 2000: # flight mode on
            FATAL_ERROR("Flight mode detected as on (from RC transmitter) as soon as power was received. As a safety precaution, mode switch needs to be in standby mode when system is powered up.")
        time.sleep(0.025)

    # Print settings that are important
    print("Roll PID: " + str(pid_roll_kp) + ", " + str(pid_roll_ki) + ", " + str(pid_roll_kd))
    print("Pitch PID: " + str(pid_pitch_kp) + ", " + str(pid_pitch_ki) + ", " + str(pid_pitch_kd))
    print("Yaw PID: " + str(pid_yaw_kp) + ", " + str(pid_yaw_ki) + ", " + str(pid_yaw_kd))

    # Set up IMU (MPU-6050)
    i2c = machine.I2C(0, sda = machine.Pin(gpio_i2c_sda), scl = machine.Pin(gpio_i2c_scl))
    mpu6050_address:int = 0x68
    i2c.writeto_mem(mpu6050_address, 0x6B, bytes([0x01])) # wake it up
    i2c.writeto_mem(mpu6050_address, 0x1A, bytes([0x05])) # set low pass filter to 5 (0-6)
    i2c.writeto_mem(mpu6050_address, 0x1B, bytes([0x08])) # set gyro scale to 1 (0-3)

    # confirm IMU is set up
    whoami:int = i2c.readfrom_mem(mpu6050_address, 0x75, 1)[0]
    lpf:int = i2c.readfrom_mem(mpu6050_address, 0x1A, 1)[0]
    gs:int = i2c.readfrom_mem(mpu6050_address, 0x1B, 1)[0]
    
    # did who am I work?
    if whoami == 104: #0x68
        print("MPU-6050 WHOAMI validated!")
    else:
        FATAL_ERROR("ERROR! MPU-6050 WHOAMI failed! '" + str(whoami) + "' returned.")

    # did lpf get set?
    if lpf == 0x05:
        print("MPU-6050 LPF set to " + str(lpf) + " correctly.")
    else:
        FATAL_ERROR("ERROR! MPU-6050 LPF did not set correctly. Set to '" + str(lpf) + "'")

    # did gyro scale get set?
    if gs == 0x08:
        print("MPU-6050 Gyro Scale set to " + str(gs) + " correctly.")
    else:
        FATAL_ERROR("ERROR! MPU-6050 gyro scale did not set correctly. " + str(gs) + " returned.")

    # measure gyro bias
    print("Measuring gyro bias...")
    gxs:list[float] = []
    gys:list[float] = []
    gzs:list[float] = []
    started_at_ticks_ms:int = time.ticks_ms()
    while ((time.ticks_ms() - started_at_ticks_ms) / 1000) < 3.0:
        gyro_data = i2c.readfrom_mem(mpu6050_address, 0x43, 6) # read 6 bytes (2 for each axis)
        gyro_x = (translate_pair(gyro_data[0], gyro_data[1]) / 65.5)
        gyro_y = (translate_pair(gyro_data[2], gyro_data[3]) / 65.5)
        gyro_z = (translate_pair(gyro_data[4], gyro_data[5]) / 65.5) * -1 # multiply by -1 because of the way I have it mounted on the quadcopter - it may be upside down. I want a "yaw to the right" to be positive and a "yaw to the left" to be negative.
        gxs.append(gyro_x)
        gys.append(gyro_y)
        gzs.append(gyro_z)
        time.sleep(0.025)
    gyro_bias_x = sum(gxs) / len(gxs)
    gyro_bias_y = sum(gys) / len(gys)
    gyro_bias_z = sum(gzs) / len(gzs)
    print("Gyro bias: " + str((gyro_bias_x, gyro_bias_y, gyro_bias_z)))

    # Set up PWM's
    M1:machine.PWM = machine.PWM(machine.Pin(gpio_motor1))
    M2:machine.PWM = machine.PWM(machine.Pin(gpio_motor2))
    M3:machine.PWM = machine.PWM(machine.Pin(gpio_motor3))
    M4:machine.PWM = machine.PWM(machine.Pin(gpio_motor4))
    M1.freq(250)
    M2.freq(250)
    M3.freq(250)
    M4.freq(250)
    print("Motor PWM's set up @ 250 hz")

    # Constants calculations / state variables - no need to calculate these during the loop (save processor time)
    cycle_time_seconds:float = 1.0 / target_cycle_hz
    cycle_time_us:int = int(round(cycle_time_seconds * 1000000, 0)) # multiply by 1,000,000 to go from seconds to microseconds (us)
    max_throttle = throttle_governor if throttle_governor is not None else 1.0 # what is the MAX throttle we can apply (considering governor)?
    throttle_range:float = max_throttle - throttle_idle # used for adjusted throttle calculation
    i_limit:float = 150.0 # PID I-term limiter. The applied I-term cannot exceed or go below (negative) this value. (safety mechanism to prevent excessive spooling of the motors)
    last_mode:bool = False # the most recent mode the flight controller was in. False = Standby (props not spinning), True = Flight mode
    
    # State variables - PID related
    # required to be delcared outside of the loop because their state will be used in multiple loops (passed from loop to loop)
    roll_last_integral:float = 0.0
    roll_last_error:float = 0.0
    pitch_last_integral:float = 0.0
    pitch_last_error:float = 0.0
    yaw_last_integral:float = 0.0
    yaw_last_error:float = 0.0

    # INFINITE LOOP
    led.on() # turn on the onboard LED to signal that the flight controller is now active
    print("-- BEGINNING FLIGHT CONTROL LOOP NOW --")
    try:
        while True:
            
            # mark start time
            loop_begin_us:int = time.ticks_us()

            # Capture raw IMU data
            # we divide by 65.5 here because that is the modifier to use at a gyro range scale of 1, which we are using.
            gyro_data = i2c.readfrom_mem(mpu6050_address, 0x43, 6) # read 6 bytes (2 for each axis)
            gyro_x = ((translate_pair(gyro_data[0], gyro_data[1]) / 65.5) - gyro_bias_x) * -1 # Roll rate. we multiply by -1 here because of the way I have it mounted. it should be rotated 180 degrees I believe, but it's okay, I can flip it here. 
            gyro_y = (translate_pair(gyro_data[2], gyro_data[3]) / 65.5) - gyro_bias_y # Pitch rate.
            gyro_z = ((translate_pair(gyro_data[4], gyro_data[5]) / 65.5) * -1) - gyro_bias_z # Yaw rate. multiply by -1 because of the way I have it mounted - it may be upside down. I want a "yaw to the right" to be positive and a "yaw to the left" to be negative.

            # Read control commands from RC
            rc_data = rc.read()

            # normalize all RC input values
            input_throttle:float = normalize(rc_data[3], 1000.0, 2000.0, 0.0, 1.0) # between 0.0 and 1.0
            input_pitch:float = (normalize(rc_data[2], 1000.0, 2000.0, -1.0, 1.0)) * -1 # between -1.0 and 1.0. We multiply by -1 because... If the pitch is "full forward" (i.e. 75), that means we want a NEGATIVE pitch (when a plane pitches it's nose down, that is negative, not positive. And when a place pitches it's nose up, pulling back on the stick, it's positive, not negative.) Thus, we need to flip it.
            input_roll:float = normalize(rc_data[1], 1000.0, 2000.0, -1.0, 1.0) # between -1.0 and 1.0
            input_yaw:float = normalize(rc_data[4], 1000.0, 2000.0, -1.0, 1.0) # between -1.0 and 1.0

            # ADJUST MOTOR OUTPUTS!
            # based on channel 5. Channel 5 I have assigned to the switch that determines flight mode (standby/flight)
            if rc_data[5] == 1000: # standby mode - switch in "up" or OFF position
            
                # turn motors off completely
                duty_0_percent:int = calculate_duty_cycle(0.0)
                M1.duty_ns(duty_0_percent)
                M2.duty_ns(duty_0_percent)
                M3.duty_ns(duty_0_percent)
                M4.duty_ns(duty_0_percent)

                # reset PID's
                roll_last_integral = 0.0
                roll_last_error = 0.0
                pitch_last_integral = 0.0
                pitch_last_error = 0.0
                yaw_last_integral = 0.0
                yaw_last_error = 0.0

                # set last mode
                last_mode = False # False means standby mode

            elif rc_data[5] == 2000: # flight mode (idle props at least) - swith in "down" or ON position

                # if last mode was standby (we JUST were turned onto flight mode), perform a check that the throttle isn't high. This is a safety mechanism
                # this prevents an accident where the flight mode switch is turned on but the throttle position is high, which would immediately apply heavy throttle to each motor, shooting it into the air.
                if last_mode == False: # last mode we were in was standby mode. So, this is the first frame we are going into flight mode
                    if input_throttle > 0.05: # if throttle is > 5%
                        FATAL_ERROR("Throttle was set to " + str(input_throttle) + " as soon as flight mode was entered. Throttle must be at 0% when flight mode begins (safety check).")
                
                # calculate the adjusted desired throttle (above idle throttle, below governor throttle, scaled linearly)
                adj_throttle:float = throttle_idle + (throttle_range * input_throttle)

                # calculate errors - diff between the actual rates and the desired rates
                # "error" is calculated as setpoint (the goal) - actual
                error_rate_roll:float = (input_roll * max_rate_roll) - gyro_x
                error_rate_pitch:float = (input_pitch * max_rate_pitch) - gyro_y
                error_rate_yaw:float = (input_yaw * max_rate_yaw) - gyro_z

                # roll PID calc
                roll_p:float = error_rate_roll * pid_roll_kp
                roll_i:float = roll_last_integral + (error_rate_roll * pid_roll_ki * cycle_time_seconds)
                roll_i = max(min(roll_i, i_limit), -i_limit) # constrain within I-term limits
                roll_d:float = pid_roll_kd * (error_rate_roll - roll_last_error) / cycle_time_seconds
                pid_roll:float = roll_p + roll_i + roll_d

                # pitch PID calc
                pitch_p:float = error_rate_pitch * pid_pitch_kp
                pitch_i:float = pitch_last_integral + (error_rate_pitch * pid_pitch_ki * cycle_time_seconds)
                pitch_i = max(min(pitch_i, i_limit), -i_limit) # constrain within I-term limits
                pitch_d:float = pid_pitch_kd * (error_rate_pitch - pitch_last_error) / cycle_time_seconds
                pid_pitch = pitch_p + pitch_i + pitch_d

                # yaw PID calc
                yaw_p:float = error_rate_yaw * pid_yaw_kp
                yaw_i:float = yaw_last_integral + (error_rate_yaw * pid_yaw_ki * cycle_time_seconds)
                yaw_i = max(min(yaw_i, i_limit), -i_limit) # constrain within I-term limits
                yaw_d:float = pid_yaw_kd * (error_rate_yaw - yaw_last_error) / cycle_time_seconds
                pid_yaw = yaw_p + yaw_i + yaw_d

                # calculate throttle values
                t1:float = adj_throttle + pid_pitch + pid_roll - pid_yaw
                t2:float = adj_throttle + pid_pitch - pid_roll + pid_yaw
                t3:float = adj_throttle - pid_pitch + pid_roll + pid_yaw
                t4:float = adj_throttle - pid_pitch - pid_roll - pid_yaw

                # Adjust throttle according to input
                M1.duty_ns(calculate_duty_cycle(t1))
                M2.duty_ns(calculate_duty_cycle(t2))
                M3.duty_ns(calculate_duty_cycle(t3))
                M4.duty_ns(calculate_duty_cycle(t4))

                # Save state values for next loop
                roll_last_error = error_rate_roll
                pitch_last_error = error_rate_pitch
                yaw_last_error = error_rate_yaw
                roll_last_integral = roll_i
                pitch_last_integral = pitch_i
                yaw_last_integral = yaw_i

                # set last mode
                last_mode = True # True = flight mode (props spinning, pid active, motors receiving power commands, etc)

            else: # the input from channel 5 is unexpected
                print("Channel 5 input '" + str(rc_data[5]) + "' not valid. Is the transmitter turned on and connected?")

            # mark end time
            loop_end_us:int = time.ticks_us()

            # wait to make the hz correct
            elapsed_us:int = loop_end_us - loop_begin_us
            if elapsed_us < cycle_time_us:
                time.sleep_us(cycle_time_us - elapsed_us)
        

    except Exception as e: # something went wrong. Flash the LED so the pilot sees it

        # before we do anything, turn the motors OFF
        duty_0_percent:int = calculate_duty_cycle(0.0)
        M1.duty_ns(duty_0_percent)
        M2.duty_ns(duty_0_percent)
        M3.duty_ns(duty_0_percent)
        M4.duty_ns(duty_0_percent)

        # deinit
        M1.deinit()
        M2.deinit()
        M3.deinit()
        M4.deinit()
        
        FATAL_ERROR(str(e))















# UTILITY FUNCTIONS BELOW (Anything that is used by the flight controller loop should go here, not in a separate module or class (to save on processing time)

def calculate_duty_cycle(throttle:float, dead_zone:float = 0.03) -> int:
    """Determines the appropriate PWM duty cycle, in nanoseconds, to use for an ESC controlling a BLDC motor"""

    ### SETTINGS (that aren't parameters) ###
    duty_ceiling:int = 2000000 # the maximum duty cycle (max throttle, 100%) is 2 ms, or 10% duty (0.10)
    duty_floor:int = 1000000 # the minimum duty cycle (min throttle, 0%) is 1 ms, or 5% duty (0.05). HOWEVER, I've observed some "twitching" at exactly 5% duty cycle. It is off, but occasionally clips above, triggering the motor temporarily. To prevent this, i'm bringing the minimum down to slightly below 5%
    ################

    # calcualte the filtered percentage (consider dead zone)
    range:float = 1.0 - dead_zone - dead_zone
    percentage:float = min(max((throttle - dead_zone) / range, 0.0), 1.0)
    
    dutyns:int = duty_floor + ((duty_ceiling - duty_floor) * percentage)

    # clamp within the range
    dutyns = max(duty_floor, min(dutyns, duty_ceiling))

    return int(dutyns)

def normalize(value:float, original_min:float, original_max:float, new_min:float, new_max:float) -> float:
    """Normalizes (scales) a value to within a specific range."""
    return new_min + ((new_max - new_min) * ((value - original_min) / (original_max - original_min)))

def translate_pair(high:int, low:int) -> int:
        """Converts a byte pair to a usable value. Borrowed from https://github.com/m-rtijn/mpu6050/blob/0626053a5e1182f4951b78b8326691a9223a5f7d/mpu6050/mpu6050.py#L76C39-L76C39."""
        value = (high << 8) + low
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value   

def FATAL_ERROR(msg:str) -> None:
    em:str = "Fatal error @ " + str(time.ticks_ms()) + " ms: " + msg
    print(em)
    toolkit.log(em)
    led = machine.Pin(25, machine.Pin.OUT)
    while True:
            led.off()
            time.sleep(1.0)
            led.on()
            time.sleep(1.0)








########### RUN THE SCOUT FLIGHT CONTROLLER PROGRAM ###########
run()