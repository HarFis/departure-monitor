from tkinter import Tk, Label, Button, N, S, E, W
import tkinter.font as tkFont
import tkinter.ttk as ttkSep

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

# tkinter stuff - sizes and colors
widths = [5, 20, 11, 6]
colorsDep1 = ['LightSkyBlue1', 'LightSkyBlue2', 'LightSkyBlue1', 'LightSkyBlue2']
colorsDep2 = ['SkyBlue1', 'SkyBlue2', 'SkyBlue1', 'SkyBlue2']

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
    global departure_Coop
    global departure_nonCoop
    departure_Coop = extractDepartures('A')
    departure_nonCoop = extractDepartures('B')

class departureGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")
        self.master.bind("<Escape>", self.end_fullscreen)
        #specifies "self.font"
        self.font = tkFont.Font(family="helvetica", size=18)
        #specifies for all belonging to TextFont (other types: TkDefaultFont, TkTextFont, TkFixedFont)
        self.default_font = tkFont.nametofont("TkTextFont")
        self.default_font.configure(size=14)

        self.master.grid_columnconfigure(1, weight=2)

        self.time_label = Label(master, font=self.font, text="Current time: "+timeNowObj.strftime('%H:%M'))
        self.time_label.grid(row=0, column=0, columnspan=2, sticky=W)

        self.update_button = Button(master, text="Update", command=self.update)
        self.update_button.grid(row=0, column = 3)

        # BUSnr | Direction | Departure Time | in Min 
        self.bus_label = Label(master, font=self.default_font, text="Bus", width=widths[0], bg='grey60')
        self.bus_label.grid(row=1, column=0)

        self.direction_label = Label(master, font=self.default_font, text="Direction", width=widths[1], bg='grey70')
        self.direction_label.grid(row=1, column=1, sticky=E+W)

        self.dep_label = Label(master, font=self.default_font, text="Departure", width=widths[2], bg='grey60')
        self.dep_label.grid(row=1, column=2)

        self.min_label = Label(master, font=self.default_font, text="in Min", width=widths[3], bg='grey70')
        self.min_label.grid(row=1, column=3)  

        self.departure_rows(departure_Coop,0)      

        self.spacer = Label(master, width=sum(widths)+2)
        self.spacer.grid(row=3+len(departure_Coop), column=0, columnspan=7)
        
        # SEPARATOR CODE
        #self.separator = ttkSep.Separator(master)
        #self.separator.grid(column=0, row=3+len(departure_Coop), columnspan=4, sticky=E+W)
        
        self.departure_rows(departure_nonCoop,3+len(departure_Coop))      


        #self.close_button = Button(master, text="Close", command=master.quit)
        #self.close_button.grid(row=1, column=3)

    # parameters the departure array + shift of rows
    def departure_rows(self, dep_info_array, row_shift):
        for y in range (0,len(dep_info_array)):
            for x in range (0, 4):
                if (y==0):
                    Label(self.master, font=self.default_font, text=dep_info_array[y][x], width=widths[x], bg=colorsDep2[x]).grid(row=(2+y+row_shift), column=x, sticky=E+W)
                else:
                    Label(self.master, font=self.default_font, text=dep_info_array[y][x], width=widths[x], bg=colorsDep1[x]).grid(row=(2+y+row_shift), column=x, sticky=E+W)


    def update(self):
        print("Update!")

    def end_fullscreen(self, event=None):
        self.state = False
        self.master.attributes("-fullscreen", False)
        #return "break" 


def start():  
    root = Tk()
    #root.overrideredirect(True)
    #root.overrideredirect(False)
    root.attributes('-fullscreen',True)

    my_gui = departureGUI(root)
    #updateScreen(my_gui)
    root.mainloop()
    #root.update()




def main():
    # Read Key and Secret from login.ini
    getKeyNSecret()
    # Initialize the connection to the Vasttrafik public API. If not succesful the script will exit here
    initializeConnection()
    prepareData()
    start()

if __name__ == "__main__":
    main()