# You MUST run this with the Pi Pico plugged into the PC.
# Remove the +5V BEC input into the Pi. Plug in the pi

import machine
import time


# Motor GPIO's (not pin number, GPIO number) ###
gpio_motor1 = 28 # front left, clockwise
gpio_motor2 = 2 # front right, counter clockwise
gpio_motor3 = 16 # rear left, counter clockwise
gpio_motor4 = 15 # rear right, clockwise

# min and max throttle (nanoseconds)
throttle_max:int = 2000000
throttle_min:int = 1000000

def calibrate() -> None:

    print("Hello! Welcome to the ESC throttle range calibration script")
    print("The Pi Pico should be running on SEPARATE power from the ESC's")
    print("This is because the Pi Pico needs to be able to set the throttle to 100% BEFORE the ESC's gain power")
    print("To accomplish this, the Pi Pico will need to be on a different power source (USB) while the ESC's are powered by the LiPo.")
    print("MAKE SURE you have removed the +5V BEC circuit from the VSYS of the pico before continuing.")
    print("Please ensure that right now the ESC's are NOT powered on")
    print("Press enter to confirm this and when you are ready")
    input("")

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

    # set max throttle
    M1.duty_ns(throttle_max)
    M2.duty_ns(throttle_max)
    M3.duty_ns(throttle_max)
    M4.duty_ns(throttle_max)
    print("All 4 motors set to max throttle (" + str(throttle_max) + " ns)")

    # now ready to power on ESC's
    print("We are now ready to power on the ESC's")
    print("When you power on the ESC's, you will hear a sequence of 4 single beeps")
    print("Press enter on your keyboard BEFORE the fourth beep. (during the 4 beep period).")
    print("I will then go from the max throttle to the min throttle.")
    print("After this, you will hear a confirmation beep(s) to confirm that the max and min throttle position have been saved.")
    print("Ok, ready to continue?")
    print("1. Plug the power in")
    print("2. Wait for the 4-beep sequence to start")
    print("3. Before the 4th beep, press enter on your keyboard.")

    # min throttle
    print("")
    input("Hit ENTER before the fourth beep! Waiting for enter...")

    # send min throttle
    M1.duty_ns(throttle_min)
    M2.duty_ns(throttle_min)
    M3.duty_ns(throttle_min)
    M4.duty_ns(throttle_min)

    # confirmation beeps
    print("You should now hear confirmation beeps")
    print("After you hear those, your ESC's are calibrated. You may power down :)")

    # program complete
    print("")
    print("Program complete! Goodbye!")
