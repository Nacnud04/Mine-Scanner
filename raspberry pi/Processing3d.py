#3d processing

from bisect import bisect_left

def take_closest(myList, myNumber):
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return pos
    else:
       return pos

def group_data(lidar_x, lidar_y, lidar_times, pos_x, pos_y, pos_z, quat_w, quat_x, quat_y, quat_z, pos_times):
	final_list = []
	for i in range(len(lidar_times)):
		time = lidar_times[i]
		value = take_closest(pos_times, lidar_times[i])
		time = (lidar_times[i]+pos_times[value])/2
		print(f"pair {i} : {value} @ {time}")
		item = [time, lidar_x[i], lidar_y[i], pos_x[value]*25.4, pos_y[value]*25.4, pos_z[value]*25.4, quat_w[value], quat_x[value], quat_y[value], quat_z[value]]
		final_list.append(item)
	return final_list

def align_data(biglist):
	import math
	from pyquaternion import Quaternion
	import numpy as np
	for i in range(len(biglist)):
		lidar_x, lidar_y = biglist[i][1], biglist[i][2]
		pos_x, pos_y, pos_z = biglist[i][3], biglist[i][4], biglist[i][5]
		w, quat_x, quat_y, quat_z = biglist[i][6], biglist[i][7], biglist[i][8], biglist[i][9]
		my_quat = Quaternion(w, quat_x, quat_y, quat_z)
		#lidar y does not move because stays pointed in same diretion when turned 90 degrees
		#lidar x turns to lidar z with the 90 degree shifting
		vector = np.array([0,lidar_y,lidar_x])
		point = my_quat.rotate(vector)
		print(np.round(point, decimals=3))
		#x = lidar_x + pos_x
		#y = lidar_y + pos_y
		#z = 0 + pos_z
		x = point[0] + pos_x
		y = point[1] + pos_y
		z = point[2] + pos_z
		position = [x,y,z]
		biglist[i].extend(position)

def show_data3d(biglist):
	x = []
	y = []
	z = []
	for i in range(len(biglist)):
		x.append(biglist[i][10])
		y.append(biglist[i][11])
		z.append(biglist[i][12])
		
	# Import libraries
	from mpl_toolkits import mplot3d
	import numpy as np
	import matplotlib.pyplot as plt
	 
	# Creating figure
	fig = plt.figure(figsize = (10, 7))
	ax = plt.axes(projection ="3d")
	 
	# Creating plot
	ax.scatter3D(x, y, z, color = "green")
	plt.title("simple 3D scatter plot")
	 
	# show plot
	plt.show()

def export3d(biglist):
	x = []
	y = []
	z = []
	for i in range(len(biglist)):
		x.append(biglist[i][10])
		y.append(biglist[i][11])
		z.append(biglist[i][12])
	#make filename
	from datetime import date
	today = date.today()
	date = today.strftime("%b-%d-%y")
	import os
	filenameDone = False
	number = 0
	while filenameDone==False:
		fileExistance = os.path.isfile(f'/home/pi/Desktop/CaveReader2.0/Exports/{date}-{number}')
		if fileExistance == False:
			filename = f'/home/pi/Desktop/CaveReader2.0/Exports/{date}-{number}'
			print(f'Export being created at: {filename}')
			filenameDone = True
			break
		number += 1
	#make csv file
	import csv
	with open(filename, mode='w') as export:
		exportWriter = csv.writer(export, delimiter=',')
		for i in range(len(x)):
			exportWriter.writerow([x[i], y[i], z[i]])
			print(f'{i}/{len(x)}')
	print('Export complete')
		
