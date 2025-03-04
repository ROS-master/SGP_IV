# #!/usr/bin/env python3
# import cv2
# import mediapipe as mp
# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import String


# class GestureRecognitionNode(Node):
#     def __init__(self):
#         super().__init__('gesture_recog_node')
#         self.publisher = self.create_publisher(String, '/gesture', 10)
#         self.status_publisher = self.create_publisher(String, '/robot_status', 10)

#         self.mp_hands = mp.solutions.hands
#         self.hands = self.mp_hands.Hands()
#         self.mp_draw = mp.solutions.drawing_utils
#         self.robot_status = "Locked"
#         self.locked = True

#     def classify_gesture(self, landmarks, num_hands):
#         if num_hands > 1:
#             return "Lock"

#         thumb_tip = landmarks[4]
#         index_tip = landmarks[8]
#         middle_tip = landmarks[12]
#         ring_tip = landmarks[16]
#         pinky_tip = landmarks[20]

#         fingers_up = [
#             index_tip['y'] < landmarks[6]['y'],
#             middle_tip['y'] < landmarks[10]['y'],
#             ring_tip['y'] < landmarks[14]['y'],
#             pinky_tip['y'] < landmarks[18]['y']
#         ]

#         if all(fingers_up):
#             return "Forward"
#         elif not any(fingers_up):
#             return "Backward"
#         elif fingers_up[0] and not fingers_up[1] and not fingers_up[2] and not fingers_up[3]:
#             return "Left"
#         elif not fingers_up[0] and fingers_up[1] and fingers_up[2] and  fingers_up[3]:
#             return "Right"
#         elif fingers_up[0] and fingers_up[1] and not fingers_up[2] and not fingers_up[3]:
#             return "Lock"
#         elif fingers_up[0] and not fingers_up[1] and not fingers_up[2] and fingers_up[3]:
#             return "Unlock"
#         else:
#             return "Unknown"

#     def update_robot_action(self, gesture):
#         if self.locked:
#             if gesture == "Unlock":
#                 self.locked = False
#                 self.robot_status = "Unlocked"
#             else:
#                 self.robot_status = "Locked"
#         else:
#             if gesture == "Lock":
#                 self.locked = True
#                 self.robot_status = "Locked"
#             else:
#                 self.robot_status = gesture

#     def process_video_feed(self):
#         cap = cv2.VideoCapture(0)
#         try:
#             while rclpy.ok() and cap.isOpened():
#                 ret, frame = cap.read()
#                 if not ret:
#                     break

#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 results = self.hands.process(rgb_frame)

#                 gesture = "Unknown"
#                 if results.multi_hand_landmarks:
#                     num_hands = len(results.multi_hand_landmarks)
#                     if num_hands > 1:
#                         gesture = "Lock"
#                     else:
#                         for hand_landmarks in results.multi_hand_landmarks:
#                             self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
#                             landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in hand_landmarks.landmark]
#                             gesture = self.classify_gesture(landmarks, num_hands)

#                 self.update_robot_action(gesture)

#                 gesture_msg = String()
#                 gesture_msg.data = gesture
#                 self.publisher.publish(gesture_msg)

#                 status_msg = String()
#                 status_msg.data = self.robot_status
#                 self.status_publisher.publish(status_msg)

#                 cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#                 cv2.putText(frame, f"Robot Status: {self.robot_status}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

#                 cv2.imshow("Gesture Detection and Robot Control", frame)
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break
#         finally:
#             cap.release()
#             cv2.destroyAllWindows()


# def main(args=None):
#     rclpy.init(args=args)
#     gesture_node = GestureRecognitionNode()
    
#     try:
#         gesture_node.process_video_feed()
#     finally:
#         gesture_node.destroy_node()
#         rclpy.shutdown()


# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
import cv2
import mediapipe as mp
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class GestureRecognitionNode(Node):
    def __init__(self):
        super().__init__('gesture_recog_node')
        
        # ROS 2 Publishers
        self.publisher = self.create_publisher(String, '/gesture', 10)
        self.status_publisher = self.create_publisher(String, '/robot_status', 10)

        # ROS 2 Subscriber to RealSense RGB Image
        self.image_subscriber = self.create_subscription(
            Image,
            'camera/camera/color/image_raw',  # RealSense RGB topic
            self.image_callback,
            10
        )

        # OpenCV Bridge
        self.bridge = CvBridge()

        # MediaPipe Hand Recognition
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils

        # Robot Lock State
        self.robot_status = "Locked"
        self.locked = True

    def image_callback(self, msg):
        """Callback function to process the RealSense image."""
        try:
            # Convert ROS 2 Image message to OpenCV format
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            self.process_frame(frame)
        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

    def process_frame(self, frame):
        """Process each frame for gesture recognition."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        gesture = "Unknown"
        if results.multi_hand_landmarks:
            num_hands = len(results.multi_hand_landmarks)
            if num_hands > 1:
                gesture = "Lock"
            else:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in hand_landmarks.landmark]
                    gesture = self.classify_gesture(landmarks, num_hands)

        self.update_robot_action(gesture)

        # Publish gesture and status
        self.publish_messages(gesture)

        # Display the result
        self.display_output(frame, gesture)

    def classify_gesture(self, landmarks, num_hands):
        """Classifies hand gesture based on landmarks."""
        if num_hands > 1:
            return "Lock"

        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]

        fingers_up = [
            index_tip['y'] < landmarks[6]['y'],
            middle_tip['y'] < landmarks[10]['y'],
            ring_tip['y'] < landmarks[14]['y'],
            pinky_tip['y'] < landmarks[18]['y']
        ]

        if all(fingers_up):
            return "Forward"
        elif not any(fingers_up):
            return "Backward"
        elif fingers_up[0] and not fingers_up[1] and not fingers_up[2] and not fingers_up[3]:
            return "Left"
        elif not fingers_up[0] and fingers_up[1] and fingers_up[2] and fingers_up[3]:
            return "Right"
        elif fingers_up[0] and fingers_up[1] and not fingers_up[2] and not fingers_up[3]:
            return "Lock"
        elif fingers_up[0] and not fingers_up[1] and not fingers_up[2] and fingers_up[3]:
            return "Unlock"
        else:
            return "Unknown"

    def update_robot_action(self, gesture):
        """Updates the robot status based on recognized gesture."""
        if self.locked:
            if gesture == "Unlock":
                self.locked = False
                self.robot_status = "Unlocked"
            else:
                self.robot_status = "Locked"
        else:
            if gesture == "Lock":
                self.locked = True
                self.robot_status = "Locked"
            else:
                self.robot_status = gesture

    def publish_messages(self, gesture):
        """Publishes gesture and robot status messages."""
        gesture_msg = String()
        gesture_msg.data = gesture
        self.publisher.publish(gesture_msg)

        status_msg = String()
        status_msg.data = self.robot_status
        self.status_publisher.publish(status_msg)

    def display_output(self, frame, gesture):
        """Displays gesture detection output using OpenCV."""
        cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Robot Status: {self.robot_status}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("Gesture Detection and Robot Control", frame)
        cv2.waitKey(1)  # Allow OpenCV to update

def main(args=None):
    """Main function to initialize and run the ROS 2 node."""
    rclpy.init(args=args)
    gesture_node = GestureRecognitionNode()
    rclpy.spin(gesture_node)
    gesture_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
