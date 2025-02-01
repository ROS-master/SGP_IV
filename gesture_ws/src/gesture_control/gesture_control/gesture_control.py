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

#         self.robot_status = "Locked"  # Default status
#         self.last_gesture = "Stop"   # Last received gesture (default stop)

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
#             # When locked, stop the robot
#             twist.linear.x = 0.0
#             twist.angular.z = 0.0
#         else:
#             # Interpret gestures when unlocked
#             if self.last_gesture == "Forward":
#                 twist.linear.x = 0.5
#                 twist.angular.z = 0.0
#             elif self.last_gesture == "Stop":
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
from std_msgs.msg import String, Float32
from geometry_msgs.msg import Twist

class GestureControlNode(Node):
    def __init__(self):
        super().__init__('gesture_control_node')

        # Subscribers
        self.subscription_gesture = self.create_subscription(String, '/gesture', self.gesture_callback, 10)
        self.subscription_status = self.create_subscription(String, '/robot_status', self.status_callback, 10)
        self.subscription_speed = self.create_subscription(Float32, '/robot_speed', self.speed_callback, 10)

        # Publisher
        self.publisher_cmd = self.create_publisher(Twist, '/cmd_vel', 10)

        # Internal State
        self.robot_status = "Locked"  # Default status
        self.last_gesture = "Stop"    # Default gesture
        self.speed = 0.5              # Default speed (0.1 to 1.0)

    def status_callback(self, msg):
        """Update the robot's lock/unlock status."""
        self.robot_status = msg.data
        self.get_logger().info(f"🔒 Robot Status Updated: {self.robot_status}")

    def gesture_callback(self, msg):
        """Update the last detected gesture and execute action."""
        self.last_gesture = msg.data
        self.get_logger().info(f"🖐 Gesture Detected: {self.last_gesture}")
        self.publish_velocity()

    def speed_callback(self, msg):
        """Update speed based on received value from the gesture node."""
        self.speed = msg.data
        self.get_logger().info(f"🚀 Speed Updated: {self.speed:.2f}")

    def publish_velocity(self):
        """Send velocity commands based on the robot's status and gesture input."""
        twist = Twist()

        if self.robot_status == "Locked":
            # When locked, stop the robot
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.get_logger().info("🔴 Robot is LOCKED. No movement allowed.")
        else:
            # Interpret gestures when unlocked
            if self.last_gesture == "Forward":
                twist.linear.x = self.speed  # Move forward with speed factor
                twist.angular.z = 0.0
            elif self.last_gesture == "Backward":
                twist.linear.x = -self.speed  # Move backward
                twist.angular.z = 0.0
            elif self.last_gesture == "Stop":
                twist.linear.x = 0.0
                twist.angular.z = 0.0
            elif self.last_gesture == "Left":
                twist.linear.x = 0.0
                twist.angular.z = 0.5 * self.speed  # Rotate left with speed factor
            elif self.last_gesture == "Right":
                twist.linear.x = 0.0
                twist.angular.z = -0.5 * self.speed  # Rotate right with speed factor
            elif self.last_gesture in ["Increase Speed", "Decrease Speed"]:
                # Speed is handled separately in speed_callback()
                return
            else:
                # Default to stop for unknown gestures
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.get_logger().warn(f"⚠️ Unknown gesture: {self.last_gesture}")

        # Publish the velocity command
        self.publisher_cmd.publish(twist)
        self.get_logger().info(f"➡️ Published Twist - Linear: {twist.linear.x:.2f}, Angular: {twist.angular.z:.2f}")


def main(args=None):
    rclpy.init(args=args)
    control_node = GestureControlNode()
    rclpy.spin(control_node)  # Keep running until shutdown
    control_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
