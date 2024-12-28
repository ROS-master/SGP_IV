import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

class GestureControlNode(Node):
    def __init__(self):
        super().__init__('gesture_control_node')
        self.subscription_gesture = self.create_subscription(String, '/gesture', self.gesture_callback, 10)
        self.subscription_status = self.create_subscription(String, '/robot_status', self.status_callback, 10)
        self.publisher_cmd = self.create_publisher(Twist, '/cmd_vel', 10)

        self.robot_status = "Locked"  # Default status
        self.last_gesture = "Stop"   # Last received gesture (default stop)

    def status_callback(self, msg):
        """Update the robot's lock/unlock status."""
        self.robot_status = msg.data
        self.get_logger().info(f"Robot Status Updated: {self.robot_status}")

    def gesture_callback(self, msg):
        """Store the latest gesture for processing."""
        self.last_gesture = msg.data
        self.get_logger().info(f"Gesture Status Updated: {self.last_gesture}")
        self.publish_velocity()

    def publish_velocity(self):
        """Publish velocity commands based on the robot's status and gesture."""
        twist = Twist()

        if self.robot_status == "Locked":
            # When locked, stop the robot
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        else:
            # Interpret gestures when unlocked
            if self.last_gesture == "Forward":
                twist.linear.x = 0.5
                twist.angular.z = 0.0
            elif self.last_gesture == "Stop":
                twist.linear.x = 0.0
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
