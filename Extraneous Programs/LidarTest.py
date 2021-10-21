import os
from math import cos, sin, pi, floor
from adafruit_rplidar import RPLidar

PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME)
max_distance = 0
x = []
y = []

def process_data(data):
    global max_distance
    for angle in range(360):
        distance = data[angle]
        if distance > 0:
            max_distance = max([min([5000, distance]), max_distance])
            radians = angle * pi / 180.0
            xnew = distance * cos(radians)
            ynew = distance * sin(radians)
            print('x:' + str(xnew) + ' y:' + str(ynew))
            x.append(xnew)
            y.append(ynew)
    return x, y
scan_data = [0]*360     

print(lidar.info)
for scan in lidar.iter_scans():
    for (_, angle, distance) in scan:
        scan_data[min([359, floor(angle)])] = distance
    x, y = process_data(scan_data)
    if len(x) >= 3600:
        break

print(len(x))
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
plt.plot(x, y, 'o', color='black')
plt.show()
lidar.stop()
lidar.disconnect()
