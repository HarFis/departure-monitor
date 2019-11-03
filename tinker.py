from tkinter import Tk, Label, Button, W

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")
        self.master.bind("<Escape>", self.end_fullscreen)


        self.time_label = Label(master, text="Current time: ")
        self.time_label.grid(row=0, column=0)

        self.current_time = Label(master, text="12:00")
        self.current_time.grid(row=0, column=2)

        self.dep_label = Label(master, text="Departure", width=18, bg='green')
        self.dep_label.grid(row=1, column=0)

        self.min_label = Label(master, text="in Min", width=10, bg='blue')
        self.min_label.grid(row=1, column=1)

        self.bus_label = Label(master, text="Bus", width=5, bg='grey55')
        self.bus_label.grid(row=1, column=2)

        self.direction_label = Label(master, text="Direction", width=20, bg='grey22')
        self.direction_label.grid(row=1, column=3)

        self.divider_label = Label(master, text="--------------------------")
        self.divider_label.grid(row=2, columnspan=4)

        
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

my_gui = MyFirstGUI(root)
root.mainloop()