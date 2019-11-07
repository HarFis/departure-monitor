from tkinter import Tk, Label, Button, W
from datetime import datetime
import time

timeNowObj = datetime.now()

class departureGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")
        self.master.bind("<Escape>", self.end_fullscreen)


        self.time_label = Label(master, text="Current time: "+timeNowObj.strftime('%H:%M'))
        self.time_label.grid(row=0, column=0, columnspan=2, sticky=W)

        self.bus_label = Label(master, text="Bus", width=5, bg='grey55')
        self.bus_label.grid(row=1, column=0)

        self.dep_label = Label(master, text="Departure", width=18, bg='green')
        self.dep_label.grid(row=1, column=1)

        self.min_label = Label(master, text="in Min", width=10, bg='blue')
        self.min_label.grid(row=1, column=2)

        self.direction_label = Label(master, text="Direction", width=20, bg='grey22')
        self.direction_label.grid(row=1, column=3)

        
        #self.greet_button = Button(master, text="Greet", command=self.greet)
        #self.greet_button.grid(column=1, row=5)

        #self.close_button = Button(master, text="Close", command=master.quit)
        #self.close_button.grid(row=1, column=3)

    def greet(self):
        print("Greetings!")

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