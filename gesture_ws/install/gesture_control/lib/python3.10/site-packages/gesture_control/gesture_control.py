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


#!/usr/bin/env python3 
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist

class GestureControlNode(Node):
    def __init__(self):
        super().__init__('gesture_control_node')

        # Subscribers
        self.subscription_gesture = self.create_subscription(String, '/gesture', self.gesture_callback, 10)
        self.subscription_status = self.create_subscription(String, '/robot_status', self.status_callback, 10)
        self.subscription_object = self.create_subscription(Bool, '/object_detected', self.object_callback, 10)

        # Publisher
        self.publisher_cmd = self.create_publisher(Twist, '/cmd_vel', 10)

        # Robot State
        self.robot_status = "Locked"  # Default to locked
        self.last_gesture = "Stop"    # Default gesture
        self.object_near = False      # Object detection flag

    def status_callback(self, msg):
        """Update the robot's lock/unlock status."""
        self.robot_status = msg.data
        self.get_logger().info(f"Robot Status Updated: {self.robot_status}")

    def gesture_callback(self, msg):
        """Store the latest gesture for processing."""
        self.last_gesture = msg.data
        self.get_logger().info(f"Gesture Status Updated: {self.last_gesture}")
        self.publish_velocity()

    def object_callback(self, msg):
        """Update the object detection status."""
        self.object_near = msg.data
        self.get_logger().info(f"Object Detection: {'Detected' if self.object_near else 'Clear'}")
        self.publish_velocity()

    def publish_velocity(self):
        """Publish velocity commands based on gesture and object detection."""
        twist = Twist()

        if self.robot_status == "Locked":
            self.get_logger().info("Robot is Locked. No movement.")
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        elif self.object_near:
            self.get_logger().info("Object Detected! Stopping robot.")
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        else:
            if self.last_gesture == "Forward":
                twist.linear.x = 0.5
                twist.angular.z = 0.0
            elif self.last_gesture == "Backward":
                twist.linear.x = -0.5
                twist.angular.z = 0.0
            elif self.last_gesture == "Left":
                twist.linear.x = 0.0
                twist.angular.z = 0.5
            elif self.last_gesture == "Right":
                twist.linear.x = 0.0
                twist.angular.z = -0.5
            else:
                # Default to stop for unknown gestures
                twist.linear.x = 0.0
                twist.angular.z = 0.0

        # Publish the velocity command
        self.publisher_cmd.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    control_node = GestureControlNode()
    rclpy.spin(control_node)  # Spin until shutdown
    control_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

