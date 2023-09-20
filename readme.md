![logo](https://i.imgur.com/X2tfDfO.jpg)
*Scout* is an open-source custom quadcopter flight controller firmware that I developed from absolute scratch. The *Scout Flight Controller* is written in MicroPython and runs on a $4 Raspberry Pi Pico.
-----

Click on the image below to watch a brief video about *Scout's* development:
[![IMAGE ALT TEXT HERE](https://i.imgur.com/iNZ74vi.png)](https://www.youtube.com/watch?v=mbrcnaByMyo)

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
11. Potential Future Improvements — releasing September 25, 2023
12. Bonus Code — releasing October 2, 2023

## Repository Contents
- The complete source code can be found in [the `src` folder](./src/).
- "Bonus code" snippets (code that isn't immediately required by the flight controller software but can be of help for specific tasks anyway) can be found [in the `bonus_code` folder](./bonus_code/).

## Using this Code
[I am releasing *Scout's* the full source code under the MIT License](license.md). I hope this code can be of use for learning purposes, testing, personal projects, or any other benevolent reason. I do not condone the use of this software for menovlent reasons and do not take responsibility for any direct or indirect consequences. Please explore the skies responsibly.

## Liability Disclaimer
Please be aware that I, Tim Hanewich, the creator of this drone quadcopter code, do not assume any responsibility or liability for any consequences, including but not limited to injuries, damages, breaches of law, or any adverse events that may occur while deploying, testing, or using this code in any other way.

By accessing, modifying, or utilizing this code, you acknowledge and agree that you do so at your own risk. It is essential to exercise caution, adhere to safety regulations, and ensure compliance with all relevant laws and guidelines when working with drones or any related technology.

While this project is dedicated to promoting benevolent uses of drone technology, it is crucial to understand that unforeseen circumstances and unintended outcomes can arise. Users and developers are encouraged to prioritize safety, conduct thorough testing, and act responsibly at all times. Your safety and the safety of others should always be your utmost concern.
