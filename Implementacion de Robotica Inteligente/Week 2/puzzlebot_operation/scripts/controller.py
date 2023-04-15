#!/usr/bin/env python
import rospy
import numpy as np
import math
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float32

wr = 0.
wl = 0.
r = 0.05
l = 0.18
pointSelf = [0,0]
direction = 0
distance = 0
angle = 0
total_distance = 0.0
total_angle = 0.0
pause = [0,0]
movement = [0,0]
speed = Twist()
speed.linear.x = 0.
speed.linear.y = 0.
speed.linear.z = 0.
speed.angular.x = 0.
speed.angular.y = 0.
speed.angular.z = 0.


def coordinates(coordinate):
  xdf = coordinate[0] - pointSelf[0]  
  ydf = coordinate[1] - pointSelf[1]
  magnitude = np.sqrt(xdf ** 2 + ydf ** 2)
  #v1_theta = math.atan2(ydf, xdf)
  #v2_theta = math.atan2(coordinate[1], coordinate[0])
  #angle = (v2_theta - v1_theta) * (180.0 / math.pi)
  angle = (np.arctan2(ydf, xdf))
  if(angle < 0):
    angle = math.pi - angle
  movement = [magnitude, angle]
  return movement


  
  


def callbackWr(msg):
  global wr
  wr = msg.data

def callbackWl(msg):
  global wl
  wl = msg.data

def stop():
 #Setup the stop message (can be the same as the control message)
  print("Stopping")

if __name__=='__main__':
    #Initialise and Setup node
    rospy.init_node("controller")
    rate = rospy.Rate(100)
    rospy.on_shutdown(stop)

    #Setup Publishers and subscribers here
    pub = rospy.Publisher("cmd_vel", Twist, queue_size = 10)
    pub2 = rospy.Publisher("distance", Vector3, queue_size = 10)
    rospy.Subscriber("/wr", Float32, callbackWr)
    rospy.Subscriber("/wl", Float32, callbackWl)
    debug = Vector3()
    pointSelf = [0,0]
    
    movement = [0,0]#rospy.get_param("/distance")

    print("Controller Node is Running")
    start_time = rospy.get_time()
    step = 0
    i = 0
    check = 0
    
    #Run the node
    while not rospy.is_shutdown():

      #next_point = rospy.get_param("/point")
      dt = rospy.get_time() - start_time
      if(check < 10):
        dt = 0.0
      distance = speed.linear.x * dt 
      angle = (speed.angular.z * dt)
      input_coordinates = [[2,0], [2,2], [0,2], [0,0]]
      


      movement = coordinates(input_coordinates[step])
      if(pointSelf == input_coordinates[step] and len(input_coordinates)-1>step):
        step += 1
      

      if(movement[1]-total_angle > 0.0):
        speed.linear.x = 0.
        speed.angular.z = 0.5
        total_angle = total_angle + angle
        """elif(movement[1]-total_angle > 0.0 and movement[1]-total_angle <= 5):
        speed.linear.x = 0.
        speed.angular.z = 0.25
        total_angle = total_angle + angle"""

      elif(pause[0] < 50 and total_distance == 0):
        pause[0] += 1
        speed.linear.x = 0.
        speed.angular.z = 0.

      elif(movement[0]-total_distance > 0.0005 and speed.angular.z == 0.):
        speed.linear.x = 0.5
        speed.angular.z = 0.
        """if(movement[0] - total_distance > 0.1):
        elif(movement[0] - total_distance <= 0.1 and total_distance >= movement[0]):
          speed.linear.x = 0.25
          speed.angular.z = 0."""
        total_distance = total_distance + distance
      
      elif(pause[1] < 50):
        pause[1] += 1
        speed.linear.x = 0.
        speed.angular.z = 0.

      else:
        pause = [0,0]
        if(angle > math.pi):
          angle = angle%math.pi
        speed.linear.x = 0.
        speed.angular.z = 0.
        total_angle = movement[1]
        total_distance = 0
        pointSelf = input_coordinates[step]

      debug.x = np.rad2deg(movement[1])
      debug.y = np.rad2deg(total_angle)
      debug.z = total_distance
      #Write your code here
      pub.publish(speed)
      pub2.publish(debug)
      start_time = rospy.get_time()
      check+=1

      rate.sleep()