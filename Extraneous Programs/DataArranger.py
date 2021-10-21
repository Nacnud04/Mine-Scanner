from tkinter import *
import json
import sys
window.title("Cave Scanner JSON Creator")
window.geometry('150x130')
areas = []
colors = ["red", "blue", "green", "grey", "orange", "purple", "pink"]

class area:
    def __init__(self, code, section, room, stations, notes, neighborDirec, x2d, y2d):
        self.code = code
        self.section = section
        self.room = room
        self.sations = stations
        self.notes = notes
        self.neighborDirec = neighborDirec
        self.x2d = x2d
        self.y2d = y2d

def loadJSON():
    with open('outfile.json') as json_file:
        data = json.load(json_file)
        areastot = 0
        for newarea in data['areas']:
            areas.append(area(newarea["id"], newarea["section"], newarea["room"],
                                   newarea["stations"], newarea["notes"], newarea["neighborDirec"], newarea["x2d"],
                                   newarea["y2d"]))
            areastot += 1
    import matplotlib.pyplot as plt
    for i in range(len(areas)):
        plt.scatter(areas[i].x2d, areas[i].y2d, c=colors[i], alpha=0.5)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()
    
def up1():
    print("Up 1in")
def up10():
    print("Up 10in")
def lft1():
    print("Left 1in")
def lft10():
    print("Left 10in")
def rht1():
    print("Right 1in")
def rht10():
    print("Right 10in")
def dwn1():
    print("Down 1in")
def dwn10():
    print("Down 10in")
    
loadJSON()
up1btn = Button(window, text="1▲", command=up1)
up1btn.grid(column=2, row=1)
up10btn = Button(window, text="10▲", command=up10)
up10btn.grid(column=2, row=0)
lft1btn = Button(window, text="◀1", command=lft1)
lft1btn.grid(column=1, row=2)
lft10btn = Button(window, text="◀10", command=lft10)
lft10btn.grid(column=0, row=2)
rht1btn = Button(window, text="1▶", command=rht1)
rht1btn.grid(column=3, row=2)
rht10btn = Button(window, text="10▶", command=rht10)
rht10btn.grid(column=4, row=2)
dwn1btn = Button(window, text="1▼", command=dwn1)
dwn1btn.grid(column=2, row=3)
dwn10btn = Button(window, text="10▼", command=dwn10)
dwn10btn.grid(column=2, row=4)
window.mainloop()