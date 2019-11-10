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
#Busstop Säterigatan's ID
saterigatan_id = 9021014006580000
departureArray = []
counter = 0
starttime=time.time()
direction_31busA = 'Hjalmar Brantingspl.'
direction_31busB = 'Eketräg. via Wieselgrenspl.'
timeNowObj = datetime.now()


def saveDep():
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
    departureArray.append(journeyTupel)
    #print (departureTime +' ('+rtOrPt+')','Min: '+ mintuesToLeaveStr , 'Bus: '+ busNumber, direction,sep=' | ')
    #print (departureArray[0][2] +' ('+departureArray[0][3]+')','Min: '+ departureArray[0][4] , 'Bus: '+ departureArray[0][0], departureArray[0][1],sep=' | ')


def screen_clear():
   _ = call('clear' if os.name =='posix' else 'cls')

def initializeConnection():
    try:
        global vasttrafik
        vasttrafik = PyTrafik.pytrafik.client.Client("json", VT_key, VT_secret)
        time.sleep(15)
    except Exception as e:
        print ("Authentication failure!")
        sys.exit(1)

def printDep():
    for y in range(0, len(departureArray)):
        print (departureArray[y][2] +' ('+departureArray[y][3]+')','Min: '+ departureArray[y][4] , 'Bus: '+ departureArray[y][0], departureArray[y][1], 'Track: ' + departureArray[y][5], sep=' | ')


initializeConnection()

#saterigatan_id = vasttrafik.location_name('Säterigatan, Göteborg')[0]['id']


##print((saterigatan_db))
while (counter<=3):
    screen_clear()
    counter +=1
    saterigatan_db = vasttrafik.get_departures(saterigatan_id)
    for x in range (6):
        if(saterigatan_db[x]['track']=='A'):
            saveDep()
    printDep()
        
    print ('---------------')
    departureArray = []
    for x in range (6):
        if(saterigatan_db[x]['track']=='B'):
            saveDep()
    printDep()
    time.sleep(30.0 - ((time.time() - starttime) % 30.0))

time.sleep(15)
#os.system("sudo shutdown -h now")

