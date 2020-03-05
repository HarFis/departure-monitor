# Personal Departure Monitor

## Description
![dep_moni](https://user-images.githubusercontent.com/43996812/76018984-4e462200-5f21-11ea-8335-d9842efee6e1.jpg | width=150px)

I usually just left the house without checking the schedule. To avoid running, missing busses, waiting in the cold, I needed an easy way to check the departure times of Västtrafik's busses at my stop before leaving the house. Since I can use busses in both directions to get to the center, the monitor shows the (next 3) departures for both directions. An "energy saving socket" is used to disconnect the raspberry pi from power after a certain time, since the display glows in bright white after shutting down the raspberry pi. 
The monitor starts at start-up of the raspberry pi and can be shut down with a click (touch screen FTW) on shut-down button.

## Hardware

+ Raspberry Pi (Model B+) with an USB Wifi dongle
+ 3.5" LCD (touch screen) display, ca. 19 EUR
+ ANSMANN 5024063 "energy saving socket", with time controlled countdown, ca. 12 EUR
+ LEGO case

## API
Departure monitor uses data from [Västtrafik's public API](https://developer.vasttrafik.se). After (free) registration & creation of an app, you'll receive your key & secret for authentication. Don't forget to "prenumera" your app to "reseplaneraren".

To find your busstop's ID after you created your app at Västtrafik's developer portal:
+ Go to prenumeration -> Reseplaneraren v2 -> Tab: API Console
+ Choose "location" -> get location.name. 
+ Type your stop in the "input" field -> Press button "Try out"
+ It will show you the matching stop details (among other the ID).

If you get an 401 error, you have to re-new your token. 
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
+ Mark the script as executable: `chmod +x dep_moni.py`
+ follow this instructions (I used method 2): https://www.raspberrypi-spy.co.uk/2014/05/how-to-autostart-apps-in-rasbian-lxde-desktop/
+ `autostart` file: add or modify so it looks similar to this:
```
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@point-rpi
@/usr/bin/python3 /home/pi/departure-monitor/dep_moni.py
@xscreensaver -no-splash
```
+ set up your raspberry pi to start into "desktop (with autologin)" - can be done in command line `sudo raspi-config` or in Raspbian (Preferences -> Raspberry Pi Configuration | Boot: to desktop | Autologin: Login as user 'pi' )

(Hint: an error in the autostart or script is hard to identify since error messages are not shown. Double-check python file if dep_moni does not start even though you did everything right with autostart)

## Known Issues

+ long start time
+ empty Respian desktop visible at startup
+ no automatic or time-based shutdown

## Based on

Dimitris Platis VasttraPi: https://github.com/platisd/vasttraPi
