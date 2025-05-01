import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class GestureControl(Node):
    def __init__(self):
        super().__init__('gesture_control')

        self.gesture_subscriber = self.create_subscription(
            String, '/gesture_command', self.gesture_callback, 10)
        
        self.lidar_subscriber = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10)
        

        self.velocity_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.status_publisher = self.create_publisher(String, '/robot_status', 10)
        

        self.robot_locked = True 
        self.obstacle_front = False
        self.obstacle_left = False
        self.obstacle_right = False
        self.stop_threshold = 0.5 
        self.current_gesture = "Stop"

        self.update_robot_status()
        self.get_logger().info(" Gesture Control Node Initialized (LOCKED).")

    def update_robot_status(self):
        """ Publishes current robot status (Locked/Unlocked). """
        status_msg = String()
        status_msg.data = "Locked" if self.robot_locked else "Unlocked"
        self.status_publisher.publish(status_msg)
        self.get_logger().info(f" Robot Status: {status_msg.data}")

    def lidar_callback(self, msg):
        """ Continuously updates obstacle status based on LiDAR scan data. """
        front_range = msg.ranges[len(msg.ranges) // 2]
        left_range = msg.ranges[int(len(msg.ranges) * 0.75)] 
        right_range = msg.ranges[int(len(msg.ranges) * 0.25)] 


        self.obstacle_front = front_range < self.stop_threshold
        self.obstacle_left = left_range < self.stop_threshold
        self.obstacle_right = right_range < self.stop_threshold
        
        self.get_logger().info(f"🔍 LiDAR - Front: {self.obstacle_front}, Left: {self.obstacle_left}, Right: {self.obstacle_right}")

        self.execute_movement()

    def gesture_callback(self, msg):
        """ Handles gestures and updates movement or robot status. """
        gesture = msg.data
        self.get_logger().info(f" Gesture received: {gesture}")

 
        if gesture == "Unlock":
            self.robot_locked = False
            self.update_robot_status()
            return

        elif gesture == "Lock":
            self.robot_locked = True
            self.update_robot_status()
            return
        

        if self.robot_locked:
            self.get_logger().info(" Robot is Locked. Gesture Ignored.")
            return

 
        self.current_gesture = gesture
        self.execute_movement()

    def execute_movement(self):
        """ Executes movement based on gesture and obstacle detection. """
        twist = Twist()


        if self.robot_locked:
            self.get_logger().info(" Robot is locked. Ignoring movement.")
            self.velocity_publisher.publish(Twist()) 
            return


        if self.current_gesture == "Forward":
            if self.obstacle_front:
                self.get_logger().info("Obstacle in Front! Cannot move forward.")
            else:
                twist.linear.x = 0.5 

        elif self.current_gesture == "Backward":
            twist.linear.x = -0.5

        elif self.current_gesture == "Left":
            if self.obstacle_left:
                self.get_logger().info(" Obstacle on Left! Cannot turn left.")
            else:
                twist.angular.z = 0.5 
        elif self.current_gesture == "Right":
            if self.obstacle_right:
                self.get_logger().info(" Obstacle on Right! Cannot turn right.")
            else:
                twist.angular.z = -0.5  

        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.velocity_publisher.publish(twist)
        self.get_logger().info(f"Executing: {self.current_gesture}")

def main(args=None):
    rclpy.init(args=args)
    node = GestureControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
