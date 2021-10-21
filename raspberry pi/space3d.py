import math
 
def euler_from_quaternion(x, y, z, w):
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)
    
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)
    
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)
    
    return roll_x, pitch_y, yaw_z # in radians

max_distance = 0
x = []
y = []
def process_data(data):
    global max_distance
    for angle in range(360):
        distance = data[angle]
        if distance > 0:
            max_distance = max([min([5000, distance]), max_distance])
            radians = angle * math.pi / 180.0
            xnew = distance * math.cos(radians)
            ynew = distance * math.sin(radians)
#            print('x:' + str(xnew) + ' y:' + str(ynew))
            x.append(xnew)
            y.append(ynew)
    return x, y

#for 3d spaces
from adafruit_rplidar import RPLidar

#connect to lidar module
try :
    PORT_NAME = '/dev/ttyUSB0'
    lidar = RPLidar(None, PORT_NAME)
except :
    PORT_NAME = '/dev/ttyUSB1'
    lidar = RPLidar(None, PORT_NAME)

def start_motor():
        lidar.start_motor()
        
def stop_motor():
        lidar.stop_motor()
        
def lidar_disconnect():
        lidar.disconnect()

class Space3d:
    spaceCount3d = 0
    unwanted = 'abcdefghijklnmopqrstuvwxyzABCDEFGHIJKLNMOPQRSTUVWXYZ:'
    
    def __init__(self, name, number, intstation):
        self.name = name
        self.number = number
        self.intStation = intstation
        self.x3d = []
        self.y3d = []
        self.z3d = []
        self.lid_times = []
        self.x_scan_points = []
        self.y_scan_points = []
        self.z_scan_points = []
        self.pos_times = []
        self.w_quats = []
        self.x_quats = []
        self.y_quats = []
        self.z_quats = []
        print(f"Created 3D space with: Name={name}, Number={number}, IntStation={intstation}")
        
    def get_x_coordinates(self, data):
        x_scan_points = []
        pos_times = []
        w_quats = []
        x_quats = []
        y_quats = []
        z_quats = []
        for i in range(len(data)):
            time = data[i][0]
            w = float(data[i][1])
            x_quat = float(data[i][2])
            y_quat = float(data[i][3])
            z_quat = float(data[i][4])
            ultr_dist = data[i][5]
            roll, pitch, yaw = euler_from_quaternion(w, x_quat, y_quat, z_quat)
            #all of this assumes a flat surface wall
            angle_a, angle_b = pitch, math.pi/2
            angle_c = math.pi - (angle_a - angle_b)
            x = ultr_dist*(math.sin(angle_c)/math.sin(angle_b))
            x_scan_points.append(x)
            pos_times.append(time)
            w_quats.append(w)
            x_quats.append(x_quat)
            y_quats.append(y_quat)
            z_quats.append(z_quat)
        print("X Distances Calculated.")
        self.x_scan_points = x_scan_points
        self.pos_times = pos_times
        self.w_quats = w_quats
        self.x_quats = x_quats
        self.y_quats = y_quats
        self.z_quats = z_quats
            
    def plot_x_coordinates(self):
        import matplotlib.pyplot as x_coordinates_plot
        import numpy as np
        x_coordinates = self.x_scan_points
        zeros = [0]*len(self.x_scan_points)
        zeros2 = np.array(zeros)
        x_coordinates_plot.scatter(np.array(x_coordinates), zeros2, c='grey')
        x_coordinates_plot.scatter([0],[0], c='red')
        x_coordinates_plot.show(block=False)
        
    def get_y_coordinates(self, data):
        y_scan_points = []
        for i in range(len(data)):
            time = data[i][0]
            w = float(data[i][1])
            x_quat = float(data[i][2])
            y_quat = float(data[i][3])
            z_quat = float(data[i][4])
            ultr_dist = data[i][5]
            roll, pitch, yaw = euler_from_quaternion(w, x_quat, y_quat, z_quat)
            #all of this assumes a flat surface wall
            angle_a, angle_b = pitch, math.pi/2
            angle_c = math.pi - (angle_a - angle_b)
            #math bit, -1*abs(theta)/theta, makes it so the y value has the correct sign
            #Dsin(theta) gets the magnitude of the vertical deviation
            if angle_a != 0.0 :
                y = -1*(abs(angle_a)/angle_a)*ultr_dist*math.sin(angle_a)
            elif angle_a == 0.0:
                y = 0
            y_scan_points.append(y)
        print("Y distances calculated.")
        self.y_scan_points = y_scan_points
        
    def plot_xy_coordinates(self):
        import matplotlib.pyplot as xy_coordinates_plot
        import numpy as np
        x_coordinates = np.array(self.x_scan_points)
        y_coordinates = np.array(self.y_scan_points)
        xy_coordinates_plot.scatter(x_coordinates, y_coordinates, c='grey')
        xy_coordinates_plot.scatter([0],[0], c='red')
        xy_coordinates_plot.show(block=False)
        
    def get_z_coordinates(self, data):
        z_scan_points = []
        for i in range(len(data)):
            time = data[i][0]
            w = float(data[i][1])
            x_quat = float(data[i][2])
            y_quat = float(data[i][3])
            z_quat = float(data[i][4])
            ultr_dist = data[i][5]
            roll, pitch, yaw = euler_from_quaternion(w, x_quat, y_quat, z_quat)
            #all of this assumes a flat surface wall
            angle_a, angle_b = pitch, math.pi/2
            angle_c = math.pi - (angle_a - angle_b)
            #calculating z is like y, but with yaw
            if yaw != 0.0:
                z = -1*(abs(roll)/roll)*ultr_dist*math.sin(yaw)
            elif yaw == 0.0:
                z = 0
            z_scan_points.append(z)
        print("Z distances calculated.")
        self.z_scan_points = z_scan_points
        
    def scan3d(self, distance):
        import os, time
        from math import cos, sin, pi, floor
        from adafruit_rplidar import RPLidar

        PORT_NAME = '/dev/ttyUSB0'
        lidar = RPLidar(None, PORT_NAME)
        max_distance = 0
        maxPoints = 360
        x = []
        y = [] 
        scan_data = [0]*360  
        times = []
        print("scanning...")
        for scan in lidar.iter_scans():
            for (_, angle, distance) in scan:
                scan_data[min([359, floor(angle)])] = distance
                times.append(time.time_ns())
            x, y = process_data(scan_data)
            if len(x) >= maxPoints:
                break
        print('end')
        self.x3d.extend(x)
        self.y3d.extend(y)
        self.lid_times.extend(times)
        lidar.stop()
        
    def z3D(self, distance, totpoints):
        z = []
        for i in range(totpoints):
            z.append(i*distance/totpoints)
        self.z3d.extend(z)
        print("added distances in z axis")
        print(self.z3d)
