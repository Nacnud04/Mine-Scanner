from tkinter import *
import json
data = {}
data['areas'] = []
section = ''
room = ''
points = ''
expedition = ''
notes = ''
neighborDirec = ''
i = 1

window = Tk()

window.title("Cave Scanner JSON Creator")

window.geometry('350x250')

lbl4 = Label(window, text="Expedition Name:")
lbl4.grid(column=2, row=0)
txt4 = Entry(window,width=10)
txt4.grid(column=0, row=0)
lbl1 = Label(window, text="Selected section:")
lbl1.grid(column=2, row=1)
txt1 = Entry(window,width=10)
txt1.grid(column=0, row=1)
lbl2 = Label(window, text="Selected room:")
lbl2.grid(column=2, row=2)
txt2 = Entry(window,width=10)
txt2.grid(column=0, row=2)
lbl3 = Label(window, text="Survey Points:")
lbl3.grid(column=2, row=3)
txt3 = Entry(window,width=10)
txt3.grid(column=0, row=3)
lbl7 = Label(window, text="Notes:")
lbl7.grid(column=2, row=4)
txt7 = Entry(window,width=10)
txt7.grid(column=0, row=4)
lbl8 = Label(window, text="Neighbor Direc:")
lbl8.grid(column=2, row=5)
txt8 = Entry(window,width=10)
txt8.grid(column=0, row=5)
lbl5 = Label(window, text="")
lbl5.grid(column=0, row=7)

def expeditionSet():
    global expedition
    res = "Expedition name: " + txt4.get()
    expedition = txt4.get
    lbl4.configure(text= res)
def sectionSet():
    global section
    res = "Selected section: " + txt1.get()
    section = txt1.get()
    lbl1.configure(text= res)
def roomSet():
    global room
    res = "Selected room: " + txt2.get()
    room = txt2.get()
    lbl2.configure(text= res)
def surveyPointsSet():
    global points
    res = "Survey Points: " + txt3.get()
    points = txt3.get()
    lbl3.configure(text= res)
def notesSet():
    global notes
    res = "Notes: " + "Added Note"
    notes = txt7.get()
    lbl7.configure(text= res)
def neighborDirecSet():
    global neighborDirec
    res = "Neigbor Direc. : " + txt8.get()
    neighborDirec = txt8.get()
    lbl8.configure(text= res)
def completeRoom():
    global i
    lbl5.configure(text= str("Added room: "+str(room)))
    data['areas'].append({
        'id': 'R'+str(i),
        'section': section,
        'room': room,
        'stations': points,
        'notes': notes,
        'neighborDirec': neighborDirec,
        'x2d': None,
        'y2d': None
    })
    i += 1
def saveAndExit():
    with open('outfile.json', 'w') as outfile:
        json.dump(data, outfile)
    window.destroy()

btn5 = Button(window, text="Set", command=expeditionSet)
btn5.grid(column=1, row=0)
btn1 = Button(window, text="Set", command=sectionSet)
btn1.grid(column=1, row=1)
btn2 = Button(window, text="Set", command=roomSet)
btn2.grid(column=1, row=2)
btn3 = Button(window, text="Set", command=surveyPointsSet)
btn3.grid(column=1, row=3)
btn7 = Button(window, text="Set", command=notesSet)
btn7.grid(column=1, row=4)
btn8 = Button(window, text="Set", command=neighborDirecSet)
btn8.grid(column=1, row=5)
btn4 = Button(window, text="Finish Room", command=completeRoom)
btn4.grid(column=0, row=6)
btn6 = Button(window, text="Save + Exit", command=saveAndExit)
btn6.grid(column=2, row=6)
window.mainloop()