# Personal Departure Monitor

## Description

I usually just left the house without checking the schedule. To avoid running, missing busses, avoiding waiting in the cold, I needed an easy way to check the departure times of Västtrafik's busses at my stop before leaving the house. Since I can use busses in both directions to get to the center, the monitor shows the (next 3) departures for both directions. An "energy saving socket" was included to disconnect the raspberry pi from power after a certain time, since the display glows in bright white after shutting down the pi.

## Hardware

+ Raspberry Pi (Model B+) with a USB Wifi dongle
+ 3.5" LCD (touch screen) display, ca. 19 EUR
+ ANSMANN 5024063 "energy saving socket", with time controlled countdown, ca. 12 EUR
+ LEGO case

## Software etc

+ Raspbian with desktop
+ python wrapper by Axel Niklasson: https://github.com/axelniklasson/PyTrafik

## API
Departure monitor uses data from [Västtrafik's public API](https://developer.vasttrafik.se). After registration you can get your key & secret for authentication. Don't forget to "prenumera" your app for "reseplaneraren".

### Installation

#### Screen
Instructions: http://www.lcdwiki.com/3.5inch_RPi_Display

#### Departure Monitor
+ clone: `git clone https://github.com/HarFis/departure-monitor.git`
+ clone inside the departure monitor folder: `https://github.com/axelniklasson/PyTrafik.git``
+ in main folder create `login.ini` in the following format with key & secret from Västtrafik and your busstop id:
```[login]
key = 1234567890
secret = ABCDEFE
[busstop]
id = 0123456789```

#### Autostart
+ Mark the script as executable: `chmod +x dep_moni.py`
+ follow this instructions (I used method 2): https://www.raspberrypi-spy.co.uk/2014/05/how-to-autostart-apps-in-rasbian-lxde-desktop/
+ autostart file - add or modify so it looks similar to this:
```@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@point-rpi
@/usr/bin/python3 /home/pi/departure-monitor/dep_moni.py
@xscreensaver -no-splash```
+ set up your raspberry pi to start into "desktop (with autologin)" - can be done in command line "sudo raspi-config" or in Raspbian (Preferences -> Raspberry Pi Configuration | Boot: to desktop | Autologin: Login as user 'pi' )


## Known Issues

+ long start time
+ 

## Based on

Dimitris Platis VasttraPi: https://github.com/platisd/vasttraPi