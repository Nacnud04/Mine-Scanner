x = [0.0]
y = [0.0]
z = [0.0]

def showStations(start, end) :
    import csv
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import math
    with open('new.csv', 'r') as datafile:
        csv_reader = csv.reader(datafile, delimiter=',')
        line_count = start
        for row in csv_reader:
            if line_count >= start and line_count <= end:
                data = row
                print(data)
                distance = float(row[0])
                pitch = float(row[1]) 
                roll = float(row[2])
                yaw = float(row[3])
                x.append(distance + x[line_count])
                y.append(y[line_count])
                z.append(z[line_count])
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
            line_count += 1
    ax = plt.axes(projection='3d')
    ax.scatter(x, y, z, marker = 's', color = 'grey')
    ax.scatter(x, y, z, marker = 'x', color = 'black')
    ax.plot3D(x, y, z, 'gray')
    print(x)
    print(y)
    print(z)
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_xlabel('x')
    plt.show()