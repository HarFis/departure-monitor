import PyTrafik.pytrafik.client
from datetime import datetime
from subprocess import call
import time
import os
import sys
import configparser

#import secret and key from login.ini
login = configparser.ConfigParser()
login.read('login.ini')
VT_secret = login.get('login','secret')
VT_key = login.get ('login','key')

vasttrafik = None
counter = 0
starttime=time.time()
direction_31bus = 'Hjalmar Brantingspl.'


def printDepOfTrack():
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
    direction =  direction_31bus if saterigatan_db[x]['direction'] == 'Hjalmar Brantingsplatsen via Lindholmen' else saterigatan_db[x]['direction']
    print (departureTime +' ('+rtOrPt+')','Min: '+ mintuesToLeaveStr , 'Bus: '+ busNumber, direction,sep=' | ')

def screen_clear():
   _ = call('clear' if os.name =='posix' else 'cls')

def initializeConnection():
    try:
        global vasttrafik
        vasttrafik = PyTrafik.pytrafik.client.Client("json", VT_key, VT_secret)
    except Exception as e:
        print ("Authentication failure, exiting!")
        sys.exit(1)


initializeConnection()
time.sleep(15)

#saterigatan_id = vasttrafik.location_name('Säterigatan, Göteborg')[0]['id']

saterigatan_id = 9021014006580000

##print((saterigatan_db))
while (counter<=3):
    screen_clear()
    counter +=1
    saterigatan_db = vasttrafik.get_departures(saterigatan_id)
    for x in range (6):
        if(saterigatan_db[x]['track']=='A'):
            printDepOfTrack()
            
    print ('---------------')

    for x in range (6):
        if(saterigatan_db[x]['track']=='B'):
            printDepOfTrack()
    time.sleep(30.0 - ((time.time() - starttime) % 30.0))

time.sleep(15)
#os.system("sudo shutdown -h now")

