# #!/usr/bin/env python3 
# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import String
# from geometry_msgs.msg import Twist

# class GestureControlNode(Node):
#     def __init__(self):
#         super().__init__('gesture_control_node')
#         self.subscription_gesture = self.create_subscription(String, '/gesture', self.gesture_callback, 10)
#         self.subscription_status = self.create_subscription(String, '/robot_status', self.status_callback, 10)
#         self.publisher_cmd = self.create_publisher(Twist, '/cmd_vel', 10)

#         self.robot_status = "Locked" 
#         self.last_gesture = "Stop"  

#     def status_callback(self, msg):
#         """Update the robot's lock/unlock status."""
#         self.robot_status = msg.data
#         self.get_logger().info(f"Robot Status Updated: {self.robot_status}")

#     def gesture_callback(self, msg):
#         """Store the latest gesture for processing."""
#         self.last_gesture = msg.data
#         self.get_logger().info(f"Gesture Status Updated: {self.last_gesture}")
#         self.publish_velocity()

#     def publish_velocity(self):
#         """Publish velocity commands based on the robot's status and gesture."""
#         twist = Twist()

#         if self.robot_status == "Locked":
           
#             twist.linear.x = 0.0
#             twist.angular.z = 0.0
#         else:
#             if self.last_gesture == "Forward":
#                 twist.linear.x = 0.5
#                 twist.angular.z = 0.0
#             elif self.last_gesture == "Backward":
#                 twist.linear.x = -0.5
#                 twist.angular.z = 0.0
#             elif self.last_gesture == "Left":
#                 twist.linear.x = 0.0
#                 twist.angular.z = 0.5
#             elif self.last_gesture == "Right":
#                 twist.linear.x = 0.0
#                 twist.angular.z = -0.5
#             else:
#                 # Default to stop for unknown gestures
#                 twist.linear.x = 0.0
#                 twist.angular.z = 0.0

#         # Publish the velocity command
#         self.publisher_cmd.publish(twist)


# def main(args=None):
#     rclpy.init(args=args)
#     control_node = GestureControlNode()
#     rclpy.spin(control_node)  # Spin until shutdown
#     control_node.destroy_node()
#     rclpy.shutdown()

# if __name__ == "__main__":
#     main()

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class GestureControl(Node):
    def __init__(self):
        super().__init__('gesture_control')
        
        # Subscribers
        self.gesture_subscriber = self.create_subscription(
            String, '/gesture_command', self.gesture_callback, 10)
        
        self.lidar_subscriber = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10)
        
        # Publisher for velocity commands
        self.velocity_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # Movement Restrictions
        self.obstacle_front = False
        self.obstacle_left = False
        self.obstacle_right = False
        self.stop_threshold = 0.5  # Distance threshold for obstacles
        self.current_gesture = "Stop"

        self.get_logger().info("Gesture Control Node Initialized.")

    def lidar_callback(self, msg):
        """ Continuously updates obstacle status based on LiDAR scan data. """
        front_range = msg.ranges[len(msg.ranges) // 2]  # Front center
        left_range = msg.ranges[int(len(msg.ranges) * 0.75)]  # Left side
        right_range = msg.ranges[int(len(msg.ranges) * 0.25)]  # Right side

        # Check for obstacles
        self.obstacle_front = front_range < self.stop_threshold
        self.obstacle_left = left_range < self.stop_threshold
        self.obstacle_right = right_range < self.stop_threshold
        
        self.get_logger().info(f"🔍 LiDAR - Front: {self.obstacle_front}, Left: {self.obstacle_left}, Right: {self.obstacle_right}")

        # Update movement based on the latest LiDAR data
        self.execute_movement()

    def gesture_callback(self, msg):
        """ Updates the current gesture command and executes movement. """
        self.current_gesture = msg.data
        self.get_logger().info(f"🖐 Gesture received: {self.current_gesture}")

        # Execute movement based on gesture and obstacle status
        self.execute_movement()

    def execute_movement(self):
        """ Executes movement based on gesture and obstacle detection. """
        twist = Twist()

        if self.current_gesture == "Forward":
            if self.obstacle_front:
                self.get_logger().info("🚫 Obstacle in Front! Cannot move forward.")
            else:
                twist.linear.x = 0.5  # Move forward

        elif self.current_gesture == "Backward":
            twist.linear.x = -0.5  # Always allowed to move backward

        elif self.current_gesture == "Left":
            if self.obstacle_left:
                self.get_logger().info("🚫 Obstacle on Left! Cannot turn left.")
            else:
                twist.angular.z = 0.5  # Turn left

        elif self.current_gesture == "Right":
            if self.obstacle_right:
                self.get_logger().info("🚫 Obstacle on Right! Cannot turn right.")
            else:
                twist.angular.z = -0.5  # Turn right

        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0  # Stop the robot

        self.velocity_publisher.publish(twist)
        self.get_logger().info(f"🚀 Executing: {self.current_gesture}")

def main(args=None):
    rclpy.init(args=args)
    node = GestureControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
