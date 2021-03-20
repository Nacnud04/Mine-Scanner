import sys
#Establish Serial
import serial
try :
    ser = serial.Serial('/dev/ttyACM0',9600)
    print("Establishing Serial on /dev/ttyACM0...")
except :
    try :
        ser = serial.Serial('/dev/ttyACM1',9600)
        print("Establishing Serial on /dev/ttyACM1...")
    except :
        print("No microcontroller found")
        sys.exit()
ser.close()
ser.open()

#load JSON data
import json
import os
with open('outfile.json') as json_file:
    data = json.load(json_file)
    for area in data['areas']:
        print(json.dumps(data, indent=1))

#Import My Methods and Functions
from CaveReaderClasses import *
from Room import *
from space3d import *

#Functions
import time
from tkinter import *

def updateXYZ(newX, newY, newZ):
    global x, y, z
    xlabel.config(text = "X: " + str(newX) + " in")
    ylabel.config(text = "Y: " + str(newY) + " in")
    zlabel.config(text = "Z: " + str(newZ) + " in")
    x.append(newX)
    y.append(newY)
    z.append(newZ)

def calibrate():
    from gpiozero import LED
    calibrate = LED(16)
    calibrate.on()
    time.sleep(10)
    calibrate.off()
    for i in range(12):
        status = ser.readline()
        print(status.decode().rstrip())
    print("Callibration & setup complete")
        
        
def Shot2D():
    global totStations
    global stations
    global activeStation
    totStations += 1
    station = Stations('Alley',totStations)
    station.generateData()
    if totStations == 1 :
        station.degToPosition(0,0,0,'-2D')
    else :
        print(x)
        station.degToPosition(x[totStations-1], y[totStations-1], z[totStations-1], '-2D')
    stations.append(station)
    activeStation += 1
    updateXYZ(station.x, station.y, station.z)
    station.show(x, y, z)
    statmapphoto = PhotoImage(file = 'statmap.ppm')
    statmap = Label(image=statmapphoto)
    statmap.image = statmapphoto
    statmap.grid(column=0,row=4)
    print(stations)

def Room2D():
    global totRooms
    from gpiozero import LED
    LED(12).on()
    totRooms += 1
    intStations = [0]
    points2D = 360
    with open('outfile.json') as json_file:
        data = json.load(json_file)
        for area in data['areas']:
            if area['id'] == 'R' + str(totRooms):
                roomname = area['room']
                stationname = area['stations']
                note = area['notes']
    activeroomtxt.configure(text = 'Active Room: ' + roomname)
    stationlabel.configure(text = 'Station: ' + stationname)
    stationnotes.configure(text = 'Note: ' + note)
    window.update()
    room = Room(roomname, totRooms, intStations)
    room.room2DScan(points2D)
    if activeStation >= 0 :
        xoff = stations[activeStation].x
        yoff = stations[activeStation].y
    else:
        xoff = 0
        yoff = 0
    print(len(room.x2d))
    room.addOffset2D((totRooms-1)*len(room.x2d), (totRooms-1)*len(room.x2d)+360, xoff, yoff)
    #room.rotate2Ddata(stations[activeStation].yaw)
    room.showRoom(rooms)
    rooms.append(room)
    with open('outfile.json') as out_file:
        data = json.load(out_file)
        for area in data['areas']:
            if area['id'] == 'R' + str(totRooms):
                area['x2d'] = room.x2d
                area['y2d'] = room.y2d
    window.update()
    os.remove('outfile.json')
    with open('outfile.json', 'w') as out_file:
        json.dump(data, out_file, indent = 4)
    print(rooms)
    LED(12).off()

#forpassage3D
allowPass3D = True
totRooms3d = 0
newPass = False
rooms3d = []
runTime = 0
distance = 5 * 12

def passInt():
    global totRooms3d, rooms3d, newPass
    totRooms3d += 1
    print('passInt')
    with open('outfile.json') as json_file:
        data = json.load(json_file)
        for area in data['areas']:
            if area['id'] == 'R' + str(totRooms3d):
                roomname = area['room']
                stationname = area['stations']
                note = area['notes']
    room3d = Space3d(roomname, totRooms3d, stationname)
    rooms3d.append(room3d)
    activeroomtxt3d.configure(text = 'Active Room: ' + roomname)
    stationlabel3d.configure(text = 'Station: ' + stationname)
    stationnotes3d.configure(text = 'Note: ' + note)
    window.update()
    newPass = True
def pass3D():
    global totRooms3d, rooms3d, startTime, endTime, newPass, runTime
    from gpiozero import LED
    LED(12).on()
    points3D = 360
    if newPass == True :
        print('pass3D')
        window.update()
        startTime = time.time()
        print(startTime)
    def getData360():
        global endTime
        if allowPass3D == True :
            rooms3d[totRooms3d-1].scan3d(distance, points3D)
            endTime = time.time()
            window.after(0, getData360)
    getData360()
    runTime = endTime - startTime
    allowPass3d = False
    newPass = False
    return totRooms3d
def endpass3D():
    global allowPass3D, runTime
    allowPass3D = False
    print(f"Points Collected: {len(rooms3d[totRooms3d-1].x3d)}, Run Time (s): {runTime}")
    print(f"Distance/Point: {distance/len(rooms3d[totRooms3d-1].x3d)}")
    rooms3d[totRooms3d-1].z3D(distance, len(rooms3d[totRooms3d-1].x3d))
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(rooms3d[totRooms3d-1].x3d, rooms3d[totRooms3d-1].y3d, rooms3d[totRooms3d-1].z3d, marker='o')
    plt.show()
#     import plotly.graph_objects as go
#     values = []
#     for i in range(len(rooms3d[totRooms3d-1].x3d)):
#         values.append(i+1)
#     figplot = go.Figure(data=go.Isosurface(
#         x=rooms3d[totRooms3d-1].x3d,
#         y=rooms3d[totRooms3d-1].y3d,
#         z=rooms3d[totRooms3d-1].z3d,
#         value=values,
#         isomin=2,
#         isomax=6,
#     ))
    figplot.show()
    with open('outfile.json') as out_file:
        data = json.load(out_file)
        for area in data['areas']:
            if area['id'] == 'R' + str(totRooms3d):
                area['x3d'] = rooms3d[totRooms3d-1].x3d
                area['y3d'] = rooms3d[totRooms3d-1].y3d
                area['z3d'] = rooms3d[totRooms3d-1].z3d
    os.remove('outfile.json')
    with open('outfile.json', 'w') as out_file:
        json.dump(data, out_file, indent = 4)
    

x = [0.0]
y = [0.0]
z = [0.0]
stations = []
rooms = []
totStations = 0
totRooms = 0
startTime = 0
endTime = 0
activeStation = -1
activeRoom = -1

#Establish Main Gui
backgroundcolor = '#303030'
foregroundcolor = '#FF7300'
window = Tk()
window.title("Cave Reader")
window.geometry('800x600')
window['background']='#303030'
shotbtn = Button(window, text="2D Shot", command=Shot2D, background = backgroundcolor, foreground = foregroundcolor)
shotbtn.grid(column=0,row=1)
passagebtnstrt = Button(window, text="Pass. Go", command=pass3D, background = backgroundcolor, foreground = foregroundcolor)
passagebtnstrt.grid(column=1,row=1)
passagebtnend = Button(window, text="Pass. End", command=endpass3D, background = backgroundcolor, foreground = foregroundcolor)
passagebtnend.grid(column=1,row=2)
roombtn = Button(window, text="Pass. Int", command=passInt, background = backgroundcolor, foreground = foregroundcolor)
roombtn.grid(column=1,row=0)
formationbtn = Button(window, text="2D", command=Room2D, background = backgroundcolor, foreground = foregroundcolor)
formationbtn.grid(column=0,row=2)
calibbtn = Button(window, text="Calibrate", command=calibrate, background = backgroundcolor, foreground = foregroundcolor)
calibbtn.grid(column=0,row=0)
xlabel = Label(window, text = "X: 0.00   ", background = backgroundcolor, foreground = foregroundcolor)
xlabel.grid(column = 3, row = 0)
ylabel = Label(window, text = "Y: 0.00   ", background = backgroundcolor, foreground = foregroundcolor)
ylabel.grid(column = 3, row = 1)
zlabel = Label(window, text = "Z: 0.00   ", background = backgroundcolor, foreground = foregroundcolor)
zlabel.grid(column = 3, row = 2)
activeroomtxt = Label(window, text = "Active room:", background = backgroundcolor, foreground = foregroundcolor)
activeroomtxt.grid(column = 4, row = 2)
stationlabel = Label(window, text = "Station:", background = backgroundcolor, foreground = foregroundcolor)
stationlabel.grid(column = 4, row = 1)
stationnotes = Label(window, text = "Notes:", background = backgroundcolor, foreground = foregroundcolor)
stationnotes.grid(column = 4, row = 3)
label2d = Label(window, text = "2D", background = backgroundcolor, foreground = foregroundcolor)
label2d.grid(column = 4, row = 0)
activeroomtxt3d = Label(window, text = "Active room:", background = backgroundcolor, foreground = foregroundcolor)
activeroomtxt3d.grid(column = 5, row = 2)
stationlabel3d = Label(window, text = "Station:", background = backgroundcolor, foreground = foregroundcolor)
stationlabel3d.grid(column = 5, row = 1)
stationnotes3d = Label(window, text = "Notes:", background = backgroundcolor, foreground = foregroundcolor)
stationnotes3d.grid(column = 5, row = 3)
label3d = Label(window, text = "3D", background = backgroundcolor, foreground = foregroundcolor)
label3d.grid(column = 5, row = 0)
window.mainloop()
