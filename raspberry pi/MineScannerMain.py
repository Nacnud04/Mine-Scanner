devMode = True

import sys
import threading
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
stop_motor()

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
#example of how to send data
#     string = "ping"
#     ser.write(string.encode())
        
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
        xoff = stations[activeStation].x * -1
        yoff = stations[activeStation].y * -1
        room.rotate2Ddata(stations[activeStation].quatw, stations[activeStation].quatx, stations[activeStation].quaty, stations[activeStation].quatz)
    else:
        xoff = 0
        yoff = 0
    print(len(room.x2d))
    room.addOffset2D(xoff, yoff)
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
import math
allowPass3D = True
totRooms3d = 0
newPass = True
rooms3d = []
runTime = 0
distance = 5 * 12
position_start_time = time.time_ns()
position_start_time_sec = time.time()
pos_data = []
continue_after_pos_data = False
stop = False

def get_position_data():
    global position_start_time
    command = "laser_on"
    ser.write(command.encode())
    time.sleep(1)
    trash = "words"
    while trash != 'Command received: laser_on':
        trash = ser.readline().decode().rstrip()
        print(trash)
    command = "position_ping"
    ser.write(command.encode())
    status = ser.readline()
    print(status.decode().rstrip())
    position_start_time = time.time_ns()
    position_start_time_sec = time.time()
    
def record_position_data():
    global continue_after_pos_data
    firstTime = True
    while True:
        single_pos_data = [time.time_ns()]
        if stop == True and firstTime == True:
            firstTime = False
            command = "stop"
            ser.write(command.encode())
        
        data = ser.readline()
        cleaned = data.decode().rstrip()
        print(cleaned)
            
        if cleaned == "Command received: stop":
            continue_after_pos_data = True
            break
        elif cleaned != 'Done Callibrating' and cleaned != 'Command received: position_ping':
            pop = False
            try :
                text, w, x, y, z = cleaned.split("\t")
                if text == "quat":
                    single_pos_data.extend([w,x,y,z])
            except ValueError:
                if float(cleaned) >= 3 and float(cleaned) <= 200:
                    single_pos_data.append(float(cleaned))
                else :
                    single_pos_data.append(f"x{float(cleaned)}")
                    pop = True
            if pop == False:
                pos_data.append(single_pos_data)
            elif pop == True:
                continue
            
    #turn laser off
    command = "laser_off"
    ser.write(command.encode())
    trash = "junk"
    while trash != 'Command received: laser_off':
        trash = ser.readline().decode().rstrip()
        print(trash)
    
    #clean data
    continue_after_pos_data = False
    print(len(pos_data))
    for i in range(math.floor(len(pos_data)/2)):
        list_one = pos_data[i]
        list_two = pos_data[i+1]
        if len(list_one) == 5:
            quat_list = list_one
            dist_list = list_two
        elif len(list_one) == 2:
            quat_list = list_two
            dist_list = list_one
        time_ns = (quat_list[0] + dist_list[0])/2
        w, x, y, z = quat_list[1], quat_list[2], quat_list[3], quat_list[4]
        dist = dist_list[1]
        pos_data[i] = [time_ns, w, x, y, z, dist]
        pos_data.pop(i+1)
    print(pos_data)
    #find times with missing data and remove them
    for i in range(len(pos_data)):
        if len(pos_data[i]) <= 5 :
            pos_data.pop(i)
    #get rid of incorrect ultrasonic sensor values
    try:
        for i in range(len(pos_data)):
            temp_list = []
            for k in range(len(pos_data)):
                try:
                    temp_list.append(pos_data[i][5])
                except IndexError:
                    print(temp_list)
                    print(k)
            dist = pos_data[i][5]
            
            try :
                dist = float(dist)
            
            #This exception shouldn't happen, leaving it because why not
            except ValueError:
                for j in range(len(pos_data)-i):
                    try :
                        back_point = float(pos_data[i-j-1][5])
                        if back_point >= 3 and back_point <= 200:
                            break
                    except IndexError:
                        back_point = float(pos_data[i+j+1][5])
                        if back_point >= 3 and back_point <= 200:
                            break
                for j in range(len(pos_data)-i):
                    try:
                        front_point = float(pos_data[i+j+1][5])
                        if front_point >= 3 and front_point <= 200:
                            break
                    except IndexError:
                        front_point = float(pos_data[i-j-1][5])
                        if front_point >= 3 and front_point <= 200:
                            break
                dist = (back_point+front_point)/2
                
            pos_data[i].pop(5)
            pos_data[i].append(dist)
    except IndexError:
        print("!!CLEARING OF BAD ULTRASONIC VALUES FAILED!!")
    #INITIAL PROCESSING
    print("Processing...")
    rooms3d[totRooms3d-1].get_x_coordinates(pos_data)
    rooms3d[totRooms3d-1].get_y_coordinates(pos_data)
    rooms3d[totRooms3d-1].get_z_coordinates(pos_data)
    continue_after_pos_data = True

def stop_position_data_control():
    global stop
    stop = True

def stop_position_data():
    trash = "junk"
    command = "stop"
    ser.write(command.encode())
    while trash != 'Command received: stop':
        trash = ser.readline().decode().rstrip()
        print(trash)
    command = "laser_off"
    ser.write(command.encode())
    while trash != 'Command received: laser_off':
        trash = ser.readline().decode().rstrip()
        print(trash)
#     status = ser.readline()
#     print(status.decode().rstrip())

def passInt():
    global totRooms3d, rooms3d, newPass
    totRooms3d += 1
    print('passInt')
    command = "tilt"
    trash = "junk"
    ser.write(command.encode())
    while trash != 'Command received: tilt':
        trash = ser.readline().decode().rstrip()
        print(trash)
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
    global totRooms3d, rooms3d, startTime, endTime, newPass, runTime, allowpass3d
    from gpiozero import LED
    print('scan3d: module must be held sideways')
    
    #HOW TO GET XYZ POS THROUGH A PASSAGE
#    get_position_data()
#    import threading
#    threading.Thread(target=record_position_data).start()
#    threading.Thread(target=stop_position_data_control).start()
#    while continue_after_pos_data == False:
#        time.sleep(1)
#    if devMode == True:
#        rooms3d[totRooms3d-1].plot_x_coordinates()
#        rooms3d[totRooms3d-1].plot_xy_coordinates()
    #END
    
    #HOW TO GET LIDAR THROUGH A PASSAGE
#    start_motor()
#    time.sleep(1)
#    LED(12).on()
#    if newPass == True :
#        print('pass3D')
#        window.update()
#        startTime = time.time()
#        print(startTime)
#    def getData360():
#        global endTime
#        if allowPass3D == True :
#            rooms3d[totRooms3d-1].scan3d(distance)
#            window.after(0, getData360)
#    getData360()
#    runTime = time.time() - startTime
#    allowPass3d = False
#    newPass = False
#    return totRooms3d
    #END
    
    #BOTH
    get_position_data()
    start_motor()
    time.sleep(1)
    threading.Thread(target=record_position_data).start()
    LED(12).on()
    if newPass == True :
        print('pass3D')
        window.update()
        startTime = time.time()
        print(startTime)
    def getData360():
        global endTime
        if allowPass3D == True :
            rooms3d[totRooms3d-1].scan3d(distance)
            window.after(0, getData360)
    getData360()
    runTime = time.time() - position_start_time_sec
    allowPass3d = False
    newPass = False
    #Stop lidar module
    stop_motor()
    return totRooms3d
    
from Processing3d import *
def endpass3D():
    global allowPass3D, runTime
    allowPass3D = False
    
    #Stop gathering pos data:
    threading.Thread(target=stop_position_data_control).start()
    print(f"Points Collected: {len(rooms3d[totRooms3d-1].x3d)}, Run Time (s): {runTime}")
    
    #wait before further processing
    while continue_after_pos_data == False:
        time.sleep(6)
        print("Waiting for inital processing to finish.")
    
    #begin processing
    data = group_data(rooms3d[totRooms3d-1].x3d, rooms3d[totRooms3d-1].y3d, rooms3d[totRooms3d-1].lid_times, rooms3d[totRooms3d-1].x_scan_points, rooms3d[totRooms3d-1].y_scan_points, rooms3d[totRooms3d-1].z_scan_points, rooms3d[totRooms3d-1].w_quats, rooms3d[totRooms3d-1].x_quats, rooms3d[totRooms3d-1].y_quats, rooms3d[totRooms3d-1].z_quats, rooms3d[totRooms3d-1].pos_times)
    align_data(data)
    #untilt
    command = "untilt"
    trash = "junk"
    ser.write(command.encode())
    while trash != 'Command received: untilt':
        trash = ser.readline().decode().rstrip()
        print(trash)
    stop_motor()
    export3d(data)
    show_data3d(data)
    #end processing
    
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
