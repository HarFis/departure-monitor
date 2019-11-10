from tkinter import Tk, Label, Button, W
import tkinter.font as tkFont
from datetime import datetime
import time

timeNowObj = datetime.now()
widths = [5, 20, 18, 10]
colorsDep = ['LightSkyBlue1', 'LightSkyBlue2', 'LightSkyBlue1', 'LightSkyBlue2']

testArray = ['ich', 'bin', 'halb', 'müde', False]


class departureGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")
        self.master.bind("<Escape>", self.end_fullscreen)
        #specifies "self.font"
        self.font = tkFont.Font(family="helvetica", size=20)
        #sepecifies for all belonging to TextFont (other types: TkDefaultFont, TkTextFont, TkFixedFont)
        self.default_font = tkFont.nametofont("TkTextFont")
        self.default_font.configure(size=16)

        self.time_label = Label(master, font=self.font, text="Current time: "+timeNowObj.strftime('%H:%M'))
        self.time_label.grid(row=0, column=0, columnspan=2, sticky=W)

        self.update_button = Button(master, text="Update", command=self.update)
        self.update_button.grid(row=0, column = 3)

        # BUSnr | Direction | Departure Time | in Min 
        self.bus_label = Label(master, text="Bus", width=widths[0], bg='grey60')
        self.bus_label.grid(row=1, column=0)

        self.direction_label = Label(master, text="Direction", width=widths[1], bg='grey70')
        self.direction_label.grid(row=1, column=1)

        self.dep_label = Label(master, text="Departure", width=widths[2], bg='grey60')
        self.dep_label.grid(row=1, column=2)

        self.min_label = Label(master, text="in Min", width=widths[3], bg='grey70')
        self.min_label.grid(row=1, column=3)        

        for x in range (0, 4):
            if x == 2 and testArray[4]==False:
                Label(master, text=testArray[x], width=widths[x], fg='red3', bg=colorsDep[x]).grid(row=2, column=x)
            else:
                Label(master, text=testArray[x], width=widths[x], bg=colorsDep[x]).grid(row=2, column=x)

        
        

        #self.close_button = Button(master, text="Close", command=master.quit)
        #self.close_button.grid(row=1, column=3)

    def update(self):
        print("Update!")

    def end_fullscreen(self, event=None):
        self.state = False
        self.master.attributes("-fullscreen", False)
        #return "break" 

root = Tk()
#root.overrideredirect(True)
#root.overrideredirect(False)
root.attributes('-fullscreen',True)

my_gui = departureGUI(root)
root.mainloop()