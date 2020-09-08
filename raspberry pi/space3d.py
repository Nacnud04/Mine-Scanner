#for 3d spaces
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
        print(f"Created 3D space with: Name={name}, Number={number}, IntStation={intstation}")
    
    def scan3d(self, distance, points):
        print('scan3d: module must be held sideways')
        import sys
        import os
        from math import cos, sin, pi, floor
        from adafruit_rplidar import RPLidar
        #connect to lidar module
        try :
            PORT_NAME = '/dev/ttyUSB0'
            lidar = RPLidar(None, PORT_NAME)
        except :
            PORT_NAME = '/dev/ttyUSB1'
            lidar = RPLidar(None, PORT_NAME)
        max_distance = 0
        x = []
        y = []
        scan_data = [0]*360     
        try :
            print(lidar.info)
            for scan in lidar.iter_scans():
                for (_, angle, distance) in scan:
                    scan_data[min([359, floor(angle)])] = distance
                for angle in range(360):
                    distance = scan_data[angle]
                    if distance > 0:
                        max_distance = max([min([5000, distance]), max_distance])
                        radians = angle * pi / 180.0
                        if len(x) >= int(points):
                            distance = 'this is supposed to cause an error'
                        xnew = distance * cos(radians)
                        ynew = distance * sin(radians)
                        print('x:' + str(xnew) + ' y:' + str(ynew))
                        xnew = round(xnew, 3)/25.4
                        ynew = round(ynew, 3)/25.4
                        x.append(xnew)
                        y.append(ynew)
        except TypeError:
            print('Stoping')
        lidar.stop()
        lidar.disconnect()
        self.x3d.extend(x)
        self.y3d.extend(y)
    def z3D(self, distance, totpoints):
        z = []
        for i in range(totpoints):
            z.append(i*distance/totpoints)
        self.z3d.extend(z)
        print("added distances in z axis")
        print(self.z3d)