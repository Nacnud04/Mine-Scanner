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
            print(data)
            if data == b'Position Data:\r\n':
                for i in range(16):
                    data = ser.readline()
                    data = data.decode("utf-8")
                    print(data)
                    anew, bnew, cnew, dnew = data.split("\t")
                    for letter in Stations.unwanted :
                        anew = anew.replace(letter,'')
                        bnew = bnew.replace(letter,'')
                        cnew = cnew.replace(letter,'')
                        dnew = dnew.replace(letter,'')
                    print(f"{str(anew)},{str(bnew)},{str(cnew)},{str(dnew)}")
                    a.append(float(anew))
                    b.append(float(bnew)) 
                    c.append(float(cnew))
                    d.append(float(dnew))
            elif data == b'Distance Data:\r\n':
                for i in range(31):
                    data = ser.readline()
                    data = float(data.decode("utf-8"))
                    print(data)
                    distance.append(data)
                print('Shot Complete')
        self.quata = median(a)
        self.quatb = median(b)
        self.quatc = median(c)
        self.quatd = median(d)
        self.dist = median(distance)
        print('Done')

    def degToPosition(self, prevxpos, prevypos, prevzpos, key):
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import math
        from scipy.spatial.transform import Rotation as R
        distance = self.dist
        r = R.from_quat([self.quatb, self.quatc, self.quatd, self.quata])
        vector = [distance, 0, 0]
        newvector = r.apply(v)
        print(newvector)
        if key == '-3D':
            #Add X Rotations Influence
            self.y = self.y*math.cos(pitch)-self.z*math.sin(pitch)
            self.z = self.y*math.sin(pitch)+self.z*math.cos(pitch)
            #Add Y Rotations Influence
            self.x = self.x*math.cos(roll)+self.z*math.sin(roll)
            self.z = -self.x*math.sin(roll)+self.z*math.cos(roll)
        if key == '-2D' or key == '-3D':
            #Add Z Rotations Influence :
            self.x = self.x*math.cos(yaw)-self.y*math.sin(yaw)
            self.y = self.x*math.sin(yaw)+self.y*math.cos(yaw)
        else :
            print("Key unknown")
        
    def show(self, x, y, z):
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from PIL import Image
        ax = plt.axes(projection='3d')
        ax.scatter(x[0:self.number + 1], y[0:self.number + 1], z[0:self.number + 1], marker = 's', color = 'grey')
        ax.scatter(x[0:self.number + 1], y[0:self.number + 1], z[0:self.number + 1], marker = 'x', color = 'black')
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
