import numpy as np
import math as m
# fundamental rotation matrices
def Rx(theta):
  return np.matrix([[ 1, 0           , 0           ],
                   [ 0, m.cos(theta),-m.sin(theta)],
                   [ 0, m.sin(theta), m.cos(theta)]])
def Ry(theta):
  return np.matrix([[ m.cos(theta), 0, m.sin(theta)],
                   [ 0           , 1, 0           ],
                   [-m.sin(theta), 0, m.cos(theta)]])
  
def Rz(theta):
  return np.matrix([[ m.cos(theta), -m.sin(theta), 0 ],
                   [ m.sin(theta), m.cos(theta) , 0 ],
                   [ 0           , 0            , 1 ]])

#Stations
class Stations:
    
    num_of_stations = 1
    unwanted = 'abcdefghijklnmopqrstuvwxyzABCDEFGHIJKLNMOPQRSTUVWXYZ:'
    
    def __init__(self, name, number):
        self.name = name
        self.number = number
        Stations.num_of_stations += 1
        
    def generateData(self):
        import time
        from gpiozero import LED
        import serial
        from statistics import median
        try :
            ser = serial.Serial('/dev/ttyACM0',9600)
            print("Establishing Serial on /dev/ttyACM0...")
        except :
            try :
                ser = serial.Serial('/dev/ttyACM1',9600)
                print("Establishing Serial on /dev/ttyACM1...")
            except :
                print("No microcontroller found")
        shot = LED(26)
        distance = []
        a, b, c, d = [], [], [], []
        anew, bnew, cnew, dnew= "", "", "", ""
        shot.on()
        time.sleep(.1)
        shot.off()
        data = ser.readline()
        print(data)
        time.sleep(5)
        shot.on()
        time.sleep(.1)
        shot.off()
        for i in range(2):
            data = ser.readline()
            if data == b'Position Data:\r\n':
                for i in range(15):
                    data = ser.readline()
                    data = data.decode("utf-8")
                    junk, anew, bnew, cnew, dnew = data.split("\t")
                    for letter in Stations.unwanted :
                        anew = anew.replace(letter,'')
                        bnew = bnew.replace(letter,'')
                        cnew = cnew.replace(letter,'')
                        dnew = dnew.replace(letter,'')
                    a.append(float(anew))
                    b.append(float(bnew)) 
                    c.append(float(cnew))
                    d.append(float(dnew))
            elif data == b'Distance Data:\r\n':
                for i in range(31):
                    data = ser.readline()
                    data = float(data.decode("utf-8"))
                    distance.append(data)
                print('Shot Complete')
        self.quatw = median(a)
        self.quatx = median(b)
        self.quaty = median(c)
        self.quatz = median(d)
        self.dist = median(distance)
        print(f'Quat: {self.quatw}, {self.quatx}, {self.quaty}, {self.quatz}   Dist: {self.dist}')
        print('Done')

    def degToPosition(self, prevxpos, prevypos, prevzpos, key):
        from pyquaternion import Quaternion
        # import quat
        my_quat = Quaternion(self.quatw, self.quatx, self.quaty, self.quatz)
        # apply to vector
        vector = np.array([self.dist,0,0])
        self.pos = my_quat.rotate(vector)
        print(np.round(self.pos, decimals=2))
        self.x = self.pos[0] + prevxpos
        self.y = self.pos[1] + prevypos
        self.z = self.pos[2] + prevzpos
        
    def show(self, x, y, z):
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from PIL import Image
        ax = plt.axes(projection='3d')
        ax.scatter(x[1:self.number + 1], y[1:self.number + 1], z[1:self.number + 1], marker = 's', color = 'grey')
        ax.scatter(x[1:self.number + 1], y[1:self.number + 1], z[1:self.number + 1], marker = 'x', color = 'black')
        ax.plot3D(x[0:self.number + 1], y[0:self.number + 1], z[0:self.number + 1], 'gray')
        ax.scatter(x[0], y[0], z[0], marker = 's', color = 'red')
        ax.scatter(x[self.number], y[self.number], z[self.number], marker = 's', color = 'green')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        ax.set_xlabel('x')
        print(x)
        print(y)
        print(z)
        #For equal scaling create bounding box
        import numpy as np
        max_range = np.array([max(x)-min(y), max(y)-min(y), max(z)-min(z)]).max()
        Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(max(x)+min(x))
        Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(max(y)+min(y))
        Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(max(z)+min(z))
        #Plot bounding box
        for xb, yb, zb in zip(Xb, Yb, Zb):
           ax.plot([xb], [yb], [zb], 'w')
        #Save plot
        plt.savefig('statmap.png', bbox_inches='tight')
        image = Image.open('statmap.png')
        image.save('statmap.ppm')
