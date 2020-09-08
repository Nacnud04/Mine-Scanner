#Rooms
class Room:
    
    num_of_rooms = 0
    
    def __init__(self, name, number, intStation):
        Room.num_of_rooms += 1
        self.name = name
        self.number = number
        self.intStation = intStation
        
    def room2DScan(self, points):
        import sys
        import os
        from math import cos, sin, pi, floor
        from adafruit_rplidar import RPLidar
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
        print(len(x))
        lidar.stop()
        lidar.disconnect()
        self.x2d = x
        self.y2d = y
    
    def addOffset2D(self, start, end, statoffx, statoffy):
        x = self.x2d
        y = self.y2d
        for i in range(360):
            x[i] += statoffx
            y[i] += statoffy
        self.x2d = x
        self.y2d = y
        
    def rotate2Ddata(self, yaw):
        import math
        for i in range(len(self.x2d)):
            self.x2d[i] = self.x2d[i]*math.cos(yaw)-self.y2d[i]*math.sin(yaw)
            self.y2d[i] = self.x2d[i]*math.sin(yaw)+self.y2d[i]*math.cos(yaw)
        
    def showRoom(self, data):
        import matplotlib.pyplot as plt
        import math
        plt.style.use('seaborn-whitegrid')
        plt.plot(self.x2d, self.y2d, 'o', color='black')
        plt.axes().set_aspect('equal')
        plt.show()
        x = self.x2d
        y = self.y2d
        xline = []
        yline = []
        points = len(x)
        pointx = x[0]
        pointy = y[0]
        x.pop(0)
        y.pop(0)
#          for i in range(points):
#             mindist = 1000000000000000000000000
#             for j in range(len(x)):
#                 try:
#                     print(j)
#                     print(len(x))
#                     print(len(xline))
#                     dist = math.sqrt((x[j+1]-pointx)**2+(y[j+1]-pointy)**2)
#                     if dist <= mindist:
#                         mindist = dist
#                         pointx = x[j+1]
#                         pointy = y[j+1]
#                         pnum = j
#                 except IndexError:
#                     xline.append(x[pnum])
#                     yline.append(y[pnum]) 
#                     x.pop(pnum)
#                     y.pop(pnum)
        import matplotlib.pyplot as pltlin
        allx = []
        ally = []
        for i in range(len(data)):
            allx.extend(data[i].x2d)
            ally.extend(data[i].y2d)
            print(data[i].x2d)
            print(data[i].y2d)
        allx.extend(self.x2d)
        ally.extend(self.y2d)
        fig, (ax1, ax2) = pltlin.subplots(nrows=1, ncols=2)
        print(allx)
        print(ally)
        ax1.scatter(allx, ally, color='black')
        ax2.plot(self.x2d, self.y2d)
#         pltlin.axes().set_aspect('equal')
        ax1.axis('square')
        ax2.axis('square')
        pltlin.show()
