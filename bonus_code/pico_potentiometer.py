### SETTINGS ###
adc_gpio = 26 # GPIO pin being used for the potentiometer input
pwm_gpio = 4 # GPIO pin being used for the PWM output
sample_rate_hz = 250 # number of times per second
moving_average = 10 # number of frames in the moving average
################

import machine
import time


def calculate_duty_cycle(throttle:float, dead_zone:float = 0.03) -> int:
    """Determines the appropriate PWM duty cycle, in nanoseconds, to use for an ESC (at 50 hz)"""

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

# set up
adc = machine.ADC(machine.Pin(adc_gpio))
pwm = machine.PWM(machine.Pin(pwm_gpio))
pwm.freq(250)
pwm.duty_u16(0)

# turn on led running light so we know it is on
led = machine.Pin(25, machine.Pin.OUT)
led.high()

ma:list[int] = []
while True:
    val = adc.read_u16()

    # add
    ma.append(val)
    while len(ma) > moving_average:
        ma.pop(0)

    # avg
    avg:int = int(round(sum(ma) / len(ma), 0))

    # percent
    percent:float = avg / 65535

    # change
    nanoseconds:int = calculate_duty_cycle(percent)
    pwm.duty_ns(nanoseconds)

    # print
    print(str(round(percent * 100, 0)) + "% (" + str(nanoseconds) + " nanoseconds)")

    # wait
    time.sleep(1 / sample_rate_hz)