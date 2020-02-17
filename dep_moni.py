from tkinter import Tk, Label, Button, W
import tkinter.font as tkFont

from datetime import datetime
import time

import PyTrafik.pytrafik.client
from subprocess import call
import os
import sys
import configparser

from socket import AF_INET, SOCK_DGRAM
import socket
import struct
import threading
from collections import defaultdict

mainThread = threading.current_thread()

# set variables and times
vasttrafik = None
timeoutNTP = 1.0  # How much to wait for the NTP server's response in seconds
# Busstop Säterigatan's ID
# saterigatan_id = vasttrafik.location_name('Säterigatan, Göteborg')[0]['id']
saterigatan_id = 9021014006580000
departure_Coop = []
departure_nonCoop = []
VT_secret = None
VT_key = None



starttime=time.time()
direction_31busA = 'Hjalmar Brantingspl.'
direction_31busB = 'Wieselgrenspl. (Eketräg.)'
timeNowObj = datetime.now()


# import secret and key from login.ini   
def getKeyNSecret():
    login = configparser.ConfigParser()
    login.read('login.ini')
    global VT_key, VT_secret
    VT_secret = login.get('login','secret')
    VT_key = login.get ('login','key')

# Fetches the time from NTP server. Source: http://blog.mattcrampton.com/post/88291892461/query-an-ntp-server-from-python
# copied from platsid
def getNTPTime(host="pool.ntp.org"):
    port = 123
    buf = 1024
    address = (host, port)
    msg = '\x1b' + 47 * '\0'

    # Reference time (in seconds since 1900-01-01 00:00:00)
    TIME1970 = 2208988800  # 1970-01-01 00:00:00

    # connect to server
    client = socket.socket(AF_INET, SOCK_DGRAM)
    client.settimeout(timeoutNTP)  # Do not wait too much to receive a response from the NTP server
    try:
        client.sendto(bytes(msg, "UTF-8"), address)
        msg, address = client.recvfrom(buf)
        t = struct.unpack("!12I", msg)[10]
        t -= TIME1970
    except:
        print ("WARNING: Could not fetch time from NTP server! Using system time instead.")
        t = time.time()  # Fall back to the system time when no response from ntp server

    d = time.strptime(time.ctime(t), "%a %b %d %H:%M:%S %Y")
    return (time.strftime("%Y-%m-%d", d), time.strftime("%H:%M", d))


# initialize connection to Västtrafik - get token
def initializeConnection():
    try:
        global vasttrafik
        vasttrafik = PyTrafik.pytrafik.client.Client("json", VT_key, VT_secret)
        time.sleep(15)
    except Exception as e:
        print (e)
        print ("Authentication failure!")
        sys.exit(1)


def extractDepartures(track_side):
    # print(track_side)
    # print(saterigatan_db)
    function_departure = []
    counter = 0
    for x in range(10):
        if(saterigatan_db[x]['track']==track_side):
            counter +=1
            track = saterigatan_db[x]['track']
            rtTimeExist = True if 'rtTime' in saterigatan_db[x] else False
            rtOrPt = 'RT' if rtTimeExist==True else 'PT'
            departureTime = saterigatan_db[x]['rtTime'] if rtTimeExist else saterigatan_db[x]['time']
            minutesToLeave = int(((datetime.strptime(departureTime, "%H:%M") - datetime.strptime(timeNowObj.strftime('%H:%M'), "%H:%M")).total_seconds() / 60))
            # meaning that the next departure time is on the next day
            if minutesToLeave < 0:
                MINUTES_IN_DAY = 1440
                minutesToLeave += MINUTES_IN_DAY
            mintuesToLeaveStr = ' ' +str(minutesToLeave).zfill(2) if minutesToLeave<=60 else '60+'
            busNumber = saterigatan_db[x]['sname']
    
            if saterigatan_db[x]['sname'] == '31' and saterigatan_db[x]['track'] == 'A':
                direction = direction_31busA
            elif saterigatan_db[x]['sname'] == '31' and saterigatan_db[x]['track'] == 'B':
                direction = direction_31busB
            else:
                direction = saterigatan_db[x]['direction']

             #direction =  direction_31bus if saterigatan_db[x]['direction'] == 'Hjalmar Brantingsplatsen via Lindholmen' else saterigatan_db[x]['direction']
            journeyTupel = (busNumber, direction, departureTime, mintuesToLeaveStr, rtTimeExist, track)
            function_departure.append(journeyTupel)
            if counter==3:break

    return function_departure

def getDepartures():
    # Get the current time and date from an NTP server as the host might not have an RTC
    (currentDate, currentTime) = getNTPTime()
    try:
        global saterigatan_db
        saterigatan_db = vasttrafik.get_departures(saterigatan_id, date=currentDate, time=currentTime)        
    except Exception as e:
            print (e)
            print ("Connection failure on departure request")

def prepareData():
    # Get json from Västtrafik
    getDepartures()
    # Extract from json relevant data for monitor
    departure_Coop = extractDepartures('A')
    departure_nonCoop = extractDepartures('B')
    print(departure_Coop)













def main():
    # Read Key and Secret from login.ini
    getKeyNSecret()
    # Initialize the connection to the Vasttrafik public API. If not succesful the script will exit here
    initializeConnection()
    prepareData()


if __name__ == "__main__":
    main()