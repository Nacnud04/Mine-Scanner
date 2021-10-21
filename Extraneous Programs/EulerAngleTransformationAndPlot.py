from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import math as math

dist = 5
yaw = 0
pitch = 0
roll = 45
#yaw = 90 - yaw

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x =[3, -3, 3, -3, 3, -3, 3, -3]
y =[-3, -3, 3, 3, -3, -3, 3, 3]
z =[0, 0, 0, 0, 6, 6, 6, 6]

#Add X Rotations Influence
for i in range(len(x)) :
    x[i] = x[i]*1
for i in range(len(y)) :
    y[i] = y[i]*math.cos(pitch)-z[i]*math.sin(pitch)
for i in range(len(z)) :
    z[i] = y[i]*math.sin(pitch)+z[i]*math.cos(pitch)
#Add Y Rotations Influence
for i in range(len(x)) :
    x[i] = x[i]*math.cos(roll)+z[i]*math.sin(roll)
for i in range(len(y)) :
    y[i] = y[i]*1
for i in range(len(z)) :
    z[i] = -x[i]*math.sin(roll)+z[i]*math.cos(roll)
#Add Z Rotations Influence
for i in range(len(x)) :
    x[i] = x[i]*math.cos(yaw)-y[i]*math.sin(yaw)
for i in range(len(y)) :
    y[i] = x[i]*math.sin(yaw)+y[i]*math.cos(yaw)
for i in range(len(z)) :
    z[i] = z[i]*1
    
ax.scatter(x, y, z, c='r', marker='o')

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

plt.show()