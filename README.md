# DEP MONI - Personal Departure Monitor for Västtrafik
![dep_moni](https://user-images.githubusercontent.com/43996812/76021221-28bb1780-5f25-11ea-85be-2f3a824f114f.jpg)

## Description

I usually just left the house without checking the schedule. To avoid running, missing busses, waiting in the cold, I needed an easy way to check the departure times of Västtrafik's busses at my stop before leaving the house. Since I can use busses in both directions to get to the center, the monitor shows the (next 3) departures for both directions. An "energy saving socket" is used to disconnect the raspberry pi from power after a certain time, since the display glows in bright white after shutting it down. 
DEP MONI starts at start-up of the raspberry pi and can be shut down with a click (touch screen FTW) on the shut-down button.

## Hardware

+ Raspberry Pi (Model B+) with an USB Wifi dongle
+ 3.5" LCD (touch screen) display, ca. 19 EUR
+ ANSMANN 5024063 "energy saving socket", with time controlled countdown disconnection, ca. 12 EUR
+ (LEGO case)

## API
DEP MONI uses data from [Västtrafik's public API](https://developer.vasttrafik.se). After (free) registration & creation of an app, you'll receive your key & secret for authentication. Don't forget to "prenumera" your app to "Reseplaneraren v2".

To find your (bus) stop's ID (after you created your app in Västtrafik's developer portal):
+ Go to prenumeration -> Reseplaneraren v2 -> Tab: API Console
+ Choose "location" -> get location.name. 
+ Type your stop's name in the "input" field -> Press button "Try out"
+ It will show you the matching stop details (among other the ID).

If you get an 401 error, you need to re-new your token. 
(Mina applikationer-> Hantera nyckler -> copy & run in terminal the first "curl command" below the keys -> copy the token it returns. Go back to API Console, paste/replace the token and then try it again.)

## Installation

### System

Raspbian with desktop and working Wifi

### Screen

Instructions: http://www.lcdwiki.com/3.5inch_RPi_Display

### Departure Monitor

+ clone: `git clone https://github.com/HarFis/departure-monitor.git`
+ clone inside the departure monitor folder: `git clone https://github.com/axelniklasson/PyTrafik.git`
[Python wrapper of Västtrafik's journey planner REST API by [Axel Niklasson](https://github.com/axelniklasson/PyTrafik)]
+ in `departure-monitor` folder create `login.ini` in the following format with key & secret from Västtrafik and your busstop id:
```
[login]
key = 1234567890abcdef
secret = ABCDEF123567
[busstop]
id = 90123456789
```

### Autostart
+ mark the script as executable: `chmod +x dep_moni.py`
+ follow these instructions (I used method 2): https://www.raspberrypi-spy.co.uk/2014/05/how-to-autostart-apps-in-rasbian-lxde-desktop/ (correct path: /home/pi/.config/lxsession/LXDE-pi/)
+ add or modify the `autostart` file so that it looks similar to/like this:
```
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@point-rpi
@/usr/bin/python3 /home/pi/departure-monitor/dep_moni.py
@xscreensaver -no-splash
```
+ set up your raspberry pi to start into "desktop (with autologin)" - can be done in command line `sudo raspi-config` or in Raspbian (Preferences -> Raspberry Pi Configuration | Boot: to desktop | Autologin: Login as user 'pi')

+ to hide the mouse pointer on the screen install unclutter (`sudo apt-get install unclutter`) and add `@unclutter -idle 0` in the autostart file (between `@point-rpi` and `@/usr/bin/python3 ...`)

(Note: an error in the autostart or script is hard to identify since error messages are not shown. If DEP MONI does not start even though you did everything right with autostart, double-check the python file, paths, environmental file (login.ini) etc. )

## Known Issues & next steps

+ long start time
+ empty Respbian desktop visible at startup
+ no automatic or time-based shutdown
+ miscalculation of minutes to leave when busses are late (appear as '60+') - seems to be a problem with updating the time that only happens on the Raspberry
+ make more use of remaining space on the screen (weather info, etc)
+ make more use of the touch screen

## Inspired by & based on 

VasttraPi by Dimitris Platis (published under MIT license): https://github.com/platisd/vasttraPi
