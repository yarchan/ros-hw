#!/usr/bin/python

import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn

from math import atan2

class Coords:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class TurtleChaser:
    def __init__(self):
        rospy.init_node('ivanov_node')

        self.chaser_speed = float(rospy.get_param('chaser_speed'))

        rospy.wait_for_service('/spawn')
        spawn_function = rospy.ServiceProxy('/spawn', Spawn)
        spawn_function(4.5, 5.5, 0.0, 'chaser')

        self.publisher = rospy.Publisher('/chaser/cmd_vel', Twist, queue_size=10)
        self.rate = rospy.Rate(1)
        
        self.turtle_position = Coords(0, 0)
        self.chaser_position = Coords(0, 0)

        self.pose = Pose()
        rospy.Subscriber('/turtle1/pose', Pose, self.turtle_callback)
        rospy.Subscriber('/chaser/pose', Pose, self.chaser_callback)

    def turtle_callback(self, msg):
        self.turtle_position.x = msg.x
        self.turtle_position.y = msg.y

    def chaser_callback(self, msg):
        self.pose = msg
        self.chaser_position.x = msg.x
        self.chaser_position.y = msg.y

    def distance_to_target(self):
        return (
            (self.turtle_position.x - self.chaser_position.x) ** 2 +
            (self.turtle_position.y - self.chaser_position.y) ** 2
        ) ** 0.5

    def angle_to_target(self):
        return atan2(
            self.turtle_position.y - self.chaser_position.y,
            self.turtle_position.x - self.chaser_position.x
        )

    def linear_vel(self):
        if (self.distance_to_target() > 1):
            return self.chaser_speed
        else:
            return 0 

    def angular_vel(self):
        if (self.distance_to_target() < 1): 
            return 0
        else:
            return (self.angle_to_target() - self.pose.theta)


    def chase(self):
        message = Twist()
        while not rospy.is_shutdown():
            if self.distance_to_target() > 1:
                message.angular.z = self.angular_vel()
                message.linear.x = self.linear_vel()

                self.publisher.publish(message)
                self.rate.sleep()
        rospy.spin()


if __name__ == '__main__':
    try:
        chaser = TurtleChaser()
        chaser.chase()
    except rospy.ROSInterruptException:
        pass
