![logo](https://i.imgur.com/X2tfDfO.jpg)
*Scout* is an open-source custom quadcopter flight controller firmware that I developed from absolute scratch. The *Scout Flight Controller* is written in MicroPython and runs on a $4 Raspberry Pi Pico.
-----

## Scout Demo Videos
Click on the image below to watch a brief video about *Scout's* development:
[![IMAGE ALT TEXT HERE](https://i.imgur.com/iNZ74vi.png)](https://www.youtube.com/watch?v=mbrcnaByMyo)

- Scout's First Flight: [https://youtu.be/Wh5G9zdJbzk](https://youtu.be/Wh5G9zdJbzk)
- Scout Demo Flight 1: [https://youtu.be/LNRYPo5-4VI](https://youtu.be/LNRYPo5-4VI)

## Development Tutorial
I'm publicly sharing all that I learned during the three months I spent dreaming about and developing *Scout*. I wrote a 12-chapter series on how I developed *Scout* and the hardware requirements. You can find the articles on Medium below:
1. [Introducing the Scout Flight Controller](https://medium.com/@timhanewich/my-greatest-engineering-accomplishment-the-scout-flight-controller-d8937fb45b24)
2. [Quadcopter Flight Dynamics](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-1-quadcopter-flight-dynamics-400af73d21db)
3. [Capturing Telemetry with a Gyroscope](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-2-gyroscope-telemetry-91f40b76d0f9)
4. [Receiving Pilot Input with an RC Receiver](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-3-receiving-control-inputs-via-an-rc-receiver-afb4fa5183f5)
5. [Stabilizing Flight with PID Controllers](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-4-stabilizing-flight-with-pid-controllers-1e945577a9aa)
6. [Controlling Brushless Motors with ESC’s and PWM](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-5-controlling-brushless-motors-with-escs-and-2529606bfdc5)
7. [Setting up the Quadcopter Hardware](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-6-hardware-9f7e77acf874)
8. [Full Flight Controller Code & Explanation](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-7-full-flight-controller-code-4269c83b3b48)
9. [Taking Flight](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-8-taking-flight-c6e41d587d8a)
10. [A Lesson in Persistence](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-9-a-lesson-in-persistence-b969ea330436)
11. [Potential Future Improvements](https://medium.com/@timhanewich/how-i-developed-the-scout-flight-controller-part-10-future-improvements-ae1957f81f76)
12. [Bonus Code](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-11-bonus-code-b6bd4f18de64)

## Repository Contents
- The complete source code for the *Scout Flight Controller* can be found in [the `src` folder](./src/).
- "Bonus code" snippets (code that isn't immediately required by the flight controller software but can be of help for specific tasks anyway) can be found [in the `bonus_code` folder](./bonus_code/).

## Using this Code & Disclaimer of Liability
[I am releasing *Scout's* full source code under the MIT License](license.md). I hope this code can be of use for learning purposes, testing, personal projects, or any other benevolent reason. I do not condone the use of this software for malevolent reasons and do not take responsibility for any direct or indirect consequences. Please explore the skies responsibly.

## How to Use this Code in Your Own Quadcopter
1. Assemble the hardware components (i.e. Raspberry Pi Pico, MPU-6050,  FlySky FS-iA6B Receiver, motors, etc.) and wire them together as described in my article, [*How I Developed the Scout Flight Controller, Part: Hardware*](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-6-hardware-9f7e77acf874). **Be sure to map each motor to the appropriate GPIO pin on the Raspberry Pi**!
2. Move all of the code in the [`src`](./src/) folder onto the Raspberry Pi Pico. Provided you wired up everything *exactly* as depicted in the [hardware article](https://timhanewich.medium.com/how-i-developed-the-scout-flight-controller-part-6-hardware-9f7e77acf874), you will not need to modify any parts of the code.
3. Turn on your FlySky FS-i6 transmitter. Ensure the throttle position is at 0% (all the way pushed down) and the upper-left switch (which is mapped to channel 5) is in the up position (value of `0`). If these either of these is *not* the case, the Scout flight controller has a built-in safety mechanism which abort at power-up.
    1. You may need to map the top-left-most switch to Channel 5 of your FlySky FS-i6 transmitter as it likely doesn't come this way out of the box. This can be done on the controller itself and there are several youtube videos/guides you can find online which describe this.
4. Plug in the LiPo battery to power up the system.
    - 1. You should see the onboard small LED light on the Raspberry Pi Pico quickly flash several times. This is just an indicator that the Raspberry Pi Pico is on and the Scout Flight Controller program has been started.
    - 2. Scout will perform the safety checks described above in step 3, as well as a check to ensure communications with the MPU-6050 are stable. If any of these safety checks fail, Scout will abort the start up. You can tell if the startup was aborted as the Raspberry Pi Pico's onboard LED will pulsate solid on for one second, then off for one second, and will repeat this indefinitely. To re-try, unplug the LiPo battery (power down Scout) and plug it back in. 
5. Scout will perform a gyroscope calibration. For three seconds, Scout will continuously read values from the gyroscope to observe its unique bias. **It is extremely important to not touch or move the quadcopter during this time**. 
6. You will then see the Raspberry Pi Pico's onboard LED go solid (on). This means that everything looks good and Scout is now ready to fly!
7. To switch Scout from *standby* mode to *flight* mode, switch the top-left-most switch down to the *on* position (`1`). This will put Scout into flight mode. You will see the propellers begin to spin at a low RPM, providing some thrust, but not enough for the quadcopter to lift off the ground.
8. Use the left stick to control throttle and yaw and the right stick to control pitch and roll, as [depicted here in this image](https://miro.medium.com/v2/resize:fit:700/0*-TObP3eRAyH7Rs3Y.png).
9. When finished flying (safely landed), flip the top-left-most switch to the *off* position (`0`) to switch back to standby mode, stopping the propellers.


## Liability Disclaimer
Please be aware that I, Tim Hanewich, the creator of this drone quadcopter code, do not assume any responsibility or liability for any consequences, including but not limited to injuries, damages, breaches of law, or any adverse events that may occur while deploying, testing, or using this code in any other way.

By accessing, modifying, or utilizing this code, you acknowledge and agree that you do so at your own risk. It is essential to exercise caution, adhere to safety regulations, and ensure compliance with all relevant laws and guidelines when working with drones or any related technology.

While this project is dedicated to promoting benevolent uses of drone technology, it is crucial to understand that unforeseen circumstances and unintended outcomes can arise. Users and developers are encouraged to prioritize safety, conduct thorough testing, and act responsibly at all times. Your safety and the safety of others should always be your utmost concern.
