import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from matplotlib import animation
import random
import math
import pickle
import csv
from args import FLAGS

fig = plt.figure()
plt.axis('equal')
plt.grid()
ax = fig.add_subplot(111)
ax.set_xlim(-25, 125)
ax.set_ylim(-25, 125)
ax.set_xticks(np.arange(-25, 126, 25))
ax.set_yticks(np.arange(-25, 126, 25))
car = patches.Rectangle((0, 0), 0, 0, fc='y')
car.set_width(7.5)
car.set_height(7.5)

drone = patches.Rectangle((0, 0), 0, 0, fc='r')
drone.set_width(5)
drone.set_height(5)

fov_circle = patches.Circle((0, 0), radius=25, fc=None, ec='k', alpha=0.3)

current_x = 0
current_y = 0

current_direction = 1

move_dir_x = 0
move_dir_y = 0

current_x_drone = 0
current_y_drone = 0
current_z_drone = 0

drone_dir_x = 0
drone_dir_y = 0

################ adding obstacles
obstacle1 = patches.Circle((30, 30), radius=2.5, fc='g')
obstacle2 = patches.Circle((20, 5), radius=2.5, fc='g')
obstacle3 = patches.Circle((50, 50), radius=5, fc='g') 

### initially writting 0, 0 to both text files
file = open("state_car.txt", "w")
file.write("0.0 0.0")
file.close()

file = open("state_drone.txt", "w")
file.write("0.0 0.0 0.0 0")
file.close()
moving_direction = ['0', '0', '0', '0']  
###

def distance_2d(x1, y1, x2, y2):
	return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def get_direction_random():
	move_to_x = random.uniform(0, 100)
	move_to_y = random.uniform(0, 100)
	return move_to_x, move_to_y

def choose_direction(arr, current_direction, x, y):
	if (current_direction == 0):
		if (1 in arr):
			arr.remove(1)
	elif (current_direction == 1):
		if (0 in arr):
			arr.remove(0)
	elif (current_direction == 2):
		if (3 in arr):
			arr.remove(3)
	elif (current_direction == 3):
		if (2 in arr):
			arr.remove(2)
	if(x == 0):
		if(y==0):
			if(0 in arr):
				arr.remove(0)
			if(2 in arr):
				arr.remove(2)
		elif(y==100):
			if(3 in arr):
				arr.remove(3)
			if(0 in arr):
				arr.remove(0)
		else:
			if(0 in arr):
				arr.remove(0)
	if(x == 100):
		if(y==0):
			if(1 in arr):
				arr.remove(1)
			if(2 in arr):
				arr.remove(2)
		elif(y==100):
			if(1 in arr):
				arr.remove(1)
			if(3 in arr):
				arr.remove(3)
		else:
			if(1 in arr):
				arr.remove(1)
	if (y == 0):
		if(x==0):
			if(0 in arr):
				arr.remove(0)
			if(2 in arr):
				arr.remove(0)
		if(x==100):
			if(1 in arr):
				arr.remove(1)
			if(2 in arr):
				arr.remove(2)
		else:
			if (2 in arr):
				arr.remove(2)
	if(y == 100):
		if(x==0):
			if(0 in arr):
				arr.remove(0)
			if(3 in arr):
				arr.remove(3)
		if(x==100):
			if(1 in arr):
				arr.remove(1)
			if(3 in arr):
				arr.remove(3)
		else:
			if(3 in arr):
				arr.remove(3)
	# add for 100 also
	num = len(arr)
	ind = random.randint(0, num-1)
	return arr[ind]

def get_direction_from_map_file(x, y, current_direction):
	# for car only

	possible_dir = []

	x = int(x)
	y = int(y)

	with open ('map', 'rb') as fp:
		arr = pickle.load(fp)

	if (arr[x-1][y] == 1):
		possible_dir.append(0)
	if (arr[x+1][y] == 1):
		possible_dir.append(1)
	if (arr[x][y-1] == 1):
		possible_dir.append(2)
	if (arr[x][y+1] == 1):
		possible_dir.append(3)

	d = choose_direction(possible_dir, current_direction, x, y)
	return d

def get_direction_given():
	# for drone only
	global moving_direction

	file = open("state_drone.txt", "r")
	move_to = file.read().split()

	print ('x, y, z= ', move_to)

	if (len(move_to) > 0):
		moving_direction = move_to
		return float(move_to[0]), float(move_to[1]), float(move_to[2])
	else:
		return float(moving_direction[0]), float(moving_direction[1]), float(moving_direction[2])

def write_car_state(state):
	file = open("state_car.txt", "w")
	file.write(str(state[0]) + " " + str(state[1]))
	file.close()

def move_car(move_direction):
	global current_x
	global current_y
	global current_direction

	if (move_direction == 0):
		next_x = current_x - 1
		next_y = current_y
		current_direction = 0
	elif (move_direction == 1):
		next_x = current_x + 1
		next_y = current_y
		current_direction = 1
	elif (move_direction == 2):
		next_x = current_x
		next_y = current_y - 1
		current_direction = 2
	elif (move_direction == 3):
		next_x = current_x
		next_y = current_y + 1
		current_direction = 3

	car.set_xy([next_x, next_y])

	current_x = next_x
	current_y = next_y
	write_car_state([current_x, current_y])

	with open('target_trajectory.csv', mode='a') as csv_file:
		writer=csv.writer(csv_file)
		writer.writerow([current_x,current_y])

	return car	

def move_drone(drone_dir_x, drone_dir_y, speed):
	global current_x_drone
	global current_y_drone

	if (distance_2d(current_x_drone, current_y_drone, drone_dir_x, drone_dir_y) >= 1):
		theta = math.atan2((drone_dir_y - current_y_drone) , (drone_dir_x - current_x_drone + 0.000001))
		next_x = current_x_drone + speed*math.cos(theta)
		next_y = current_y_drone + speed*math.sin(theta)
	else:
		next_x = current_x_drone
		next_y = current_y_drone

	with open('drone_trajectory.csv', mode='a') as csv_file:
		writer=csv.writer(csv_file)
		writer.writerow([next_x,next_y])

	drone.set_xy([next_x, next_y])
	
	current_x_drone = next_x
	current_y_drone = next_y
	return drone	

def move_fov():
	fov_circle.center = (current_x_drone, current_y_drone)
	return fov_circle	

def get_car_state():
	file1 = open("state_car.txt", "r")
	move_to_car = file1.read().split()
	move_to_car = list(map(float, move_to_car))
	return move_to_car[0], move_to_car[1]

def init():
    ax.add_patch(car)
    ax.add_patch(drone)
    ax.add_patch(fov_circle)
    ax.add_patch(obstacle1)
    ax.add_patch(obstacle2)
    ax.add_patch(obstacle3)
    ax.add_patch(obstacle4)
    ax.add_patch(obstacle5)
    return car, drone,

def animate(i):
	global move_dir_x_drone
	global move_dir_y_drone
	
	# for car
	car_x, car_y = get_car_state()
	car_movement_direction = get_direction_from_map_file(car_x, car_y, current_direction)
	c = move_car(car_movement_direction)
	print ('\n')

	# for drone
	speed_drone = 1.0
	move_dir_x_drone, move_dir_y_drone, move_dir_z_drone = get_direction_given()
	d = move_drone(move_dir_x_drone, move_dir_y_drone, speed_drone)

	f = move_fov()

	return c, d, f,

def main_animation():
	# anim = animation.FuncAnimation(fig, animate,
	# 							   init_func=init,
	# 							   frames=1000,
	# 							   interval=500,
	# 							   blit=False)
	anim = animation.FuncAnimation(fig, animate,init_func=init,frames=500,
								   interval=500,
								   blit=False)
	anim.save('movie.gif', writer='imagemagick')
	plt.title('X-Y Plot')
	plt.xlabel('X')
	plt.ylabel('Y')
	plt.show()
	
if (__name__ == '__main__'):
	main_animation()
