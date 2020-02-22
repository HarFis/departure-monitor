from tkinter import Tk, Label, Button, N, S, E, W, Frame
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
# Bus stop Säterigatan's ID
# saterigatan_id = vasttrafik.location_name('Säterigatan, Göteborg')[0]['id']
saterigatan_id = 9021014006580000
departure_Coop = []
departure_nonCoop = []
VT_secret = None
VT_key = None

direction_31busA = 'Hj. Brantingspl.'
direction_31busB = 'Wieselg.pl. (Eketräg.)'
timeoutNTP = 1.5  # How much to wait for the NTP server's response in seconds
guiRefreshRate = 45
tokenTimeout = 3600  # How much time your token is valid (default is 3600 seconds, i.e. 1 hour)


# tkinter stuff - sizes and colors
widths = [5, 18, 10, 6]
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
    # We need to reinitialize the token after it's timed out
    if mainThread.is_alive():
        threading.Timer(tokenTimeout, initializeConnection).start()



def extractDepartures(track_side):
    # print(track_side)
    # print(saterigatan_db)
    function_departure = []

    for x in range(10):
        if(saterigatan_db[x]['track']==track_side):
            track = saterigatan_db[x]['track']
            rtTimeExist = True if 'rtTime' in saterigatan_db[x] else False
            rtOrPt = 'RT' if rtTimeExist==True else 'PT'
            departureTime = saterigatan_db[x]['rtTime'] if rtTimeExist else saterigatan_db[x]['time']
            minutesToLeave = (int)((datetime.strptime(departureTime, "%H:%M") - datetime.strptime(now, "%H:%M")).total_seconds() / 60)
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

            journeyTupel = (busNumber, direction, departureTime, mintuesToLeaveStr, rtTimeExist, track)
            
            if(minutesToLeave>0):
                function_departure.append(journeyTupel)
            if len(function_departure)==3:break

    return function_departure

def getDepartures():
    # Get the current time and date from an NTP server as the host might not have an RTC
    global now
    (currentDate, currentTime) = getNTPTime()
    now = currentTime
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
    departure_Coop = extractDepartures('B')
    departure_nonCoop = extractDepartures('A')

class departureGUI:
    def __init__(self, master):
        self.master = master
        # A list that will hold the temporary departure frames so to destroy them upon refreshing
        self.departureRowFrames = []
        self.currentlyDisplayedDepartures = [0]*2  # Used to decide whether to refresh the display

        master.title("GUI")
        self.master.bind("<Escape>", self.end_fullscreen)

        departuresFrame = Frame(master) 
        departuresFrame.grid()
        self.departuresFrame = departuresFrame


    def populate_with_departures(self, departure_C, departure_nonC):
        depFrame = Frame(self.departuresFrame)
         #specifies "self.font" for time/clock
        self.font = tkFont.Font(family="helvetica", size=18)
        #specifies for all belonging to TextFont (other types: TkDefaultFont, TkTextFont, TkFixedFont)
        self.default_font = tkFont.nametofont("TkTextFont")
        self.default_font.configure(size=14)
        # bold for "in min"
        self.in_min_font = tkFont.Font(size=14, weight='bold')

        
        depFrame.grid_columnconfigure(1, weight=2)

        self.time_label = Label(self.master, font=self.font, text="Current time: "+now)  # .strftime('%H:%M'))
        self.time_label.grid(row=0, column=0, columnspan=2, sticky=W)

        self.update_button = Button(self.master, text="Shutdown", command=self.update)
        self.update_button.grid(row=0, column = 2, columnspan=2, sticky=E)

        # label colums
        self.label_columns("<- Direction <-", 1)
        # departures on track A
        self.departure_rows(departure_C,0)     

        # SPACE between directions CODE
        self.spacer = Label(self.master, width=sum(widths)+2)
        self.spacer.grid(row=2+len(departure_C), column=0, columnspan=7)
        
         # label colums
        self.label_columns("-> Direction ->", 3+len(departure_C))
        # departures on track B
        self.departure_rows(departure_nonC,4+len(departure_C))

        # Add the newly created frame to a list so we can destroy it later when we refresh the departures
        self.departureRowFrames.append(depFrame)


    def label_columns(self, direction, row_count):
        # BUSnr | Direction | Departure Time | in Min 
        self.bus_label = Label(self.master, font=self.default_font, text="Bus", width=widths[0], bg='grey60')
        self.bus_label.grid(row=row_count, column=0)

        self.direction_label = Label(self.master, font=self.default_font, text=direction, width=widths[1], bg='grey70')
        self.direction_label.grid(row=row_count, column=1, sticky=E+W)

        self.dep_label = Label(self.master, font=self.default_font, text="Departure", width=widths[2], bg='grey60')
        self.dep_label.grid(row=row_count, column=2)

        self.min_label = Label(self.master, font=self.default_font, text="in Min", width=widths[3], bg='grey70')
        self.min_label.grid(row=row_count, column=3, sticky=E+W) 


    # parameters the departure array + shift of rows
    def departure_rows(self, dep_info_array, row_shift):
        fore='black'
        for y in range (0,len(dep_info_array)):
            for x in range (0, 4):
                if(x==3): # make "in Min" bold
                    font1=self.in_min_font
                    if(int(dep_info_array[y][x])<4): 
                        # only few minutes, make "in Min" bold & red
                        fore='firebrick3'
                         
                else:
                    fore='black'
                    font1=self.default_font

                if (y==0):
                    Label(self.master, font=font1, text=dep_info_array[y][x], width=widths[x], fg=fore, bg=colorsDep2[x]).grid(row=(2+y+row_shift), column=x, sticky=E+W+N+S)
                else:
                    Label(self.master, font=font1, text=dep_info_array[y][x], width=widths[x], fg=fore, bg=colorsDep1[x]).grid(row=(2+y+row_shift), column=x, sticky=E+W+N+S)

    # Destroy any existing frames containing departures that already exist
    def resetDepartures(self):
        for frame in self.departureRowFrames:
            frame.destroy()
        # Empty the list as we have destroyed everything that was included in it
        self.departureRowFrames = []

    def update(self):
        print("Shutdown")
        end()

    def end_fullscreen(self, event=None):
        self.state = False
        self.master.attributes("-fullscreen", False)
        #return "break" 


def updateGui(my_gui):
    # Get the next trips from Vasttrafik's public API for the station we are interested in
    prepareData()
    # Update the displayed departures if they are different to the ones currently displayed
    if departure_Coop != my_gui.currentlyDisplayedDepartures[0] or departure_nonCoop != my_gui.currentlyDisplayedDepartures[1]:
        my_gui.resetDepartures()  # Remove any already existing departures
        my_gui.populate_with_departures(departure_Coop, departure_nonCoop)
        my_gui.currentlyDisplayedDepartures[0] = departure_Coop
        my_gui.currentlyDisplayedDepartures[1] = departure_nonCoop
    if mainThread.is_alive():
        threading.Timer(guiRefreshRate, updateGui, [my_gui]).start()


def start(): 
    global root 
    root = Tk()
    #root.overrideredirect(True)
    #root.overrideredirect(False)
    root.attributes('-fullscreen',True)
    global my_gui
    my_gui = departureGUI(root)
    updateGui(my_gui)
    #updateScreen(my_gui)
    root.mainloop()
    #root.update()


def end():
    root.destroy()
    os.system("sudo shutdown -h")

def main():
    # Read Key and Secret from login.ini
    getKeyNSecret()
    # Initialize the connection to the Vasttrafik public API. If not succesful the script will exit here
    initializeConnection()
    # prepareData()
    start()

if __name__ == "__main__":
    main()