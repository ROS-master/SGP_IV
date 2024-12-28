import cv2
import mediapipe as mp
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class GestureRecognitionNode(Node):
    def __init__(self):
        super().__init__('gesture_recog_node')
        self.publisher = self.create_publisher(String , '/gesture', 10)
        self.status_publisher = self.create_publisher(String, '/robot_status', 10)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils
        self.robot_status = "Locked"
        self.locked = True    #robot state 

    def classify_gesture(self , landmarks , num_hands):
        if num_hands > 1:
            return "Lock"  # Automatically lock if multiple hands are detected

        # Extract key landmarks
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]

        # Determine finger positions (up/down)
        fingers_up = [
            index_tip['y'] < landmarks[6]['y'],  # Index finger
            middle_tip['y'] < landmarks[10]['y'],  # Middle finger
            ring_tip['y'] < landmarks[14]['y'],  # Ring finger
            pinky_tip['y'] < landmarks[18]['y']  # Pinky finger
        ]

        # Gesture classification logic
        if all(fingers_up):  # All fingers up
            return "Forward"
        elif not any(fingers_up):  # All fingers down (fist)
            return "Stop"
        elif not fingers_up[0] and not fingers_up[1] and not fingers_up[2] and fingers_up[3]:  # Only pinky up
            return "Left"
        elif not fingers_up[0] and not fingers_up[1] and fingers_up[2] and not fingers_up[3]:  # Only ring up
            return "Right"
        elif fingers_up[0] and fingers_up[1] and not fingers_up[2] and not fingers_up[3]:  # Victory sign
            return "Lock"
        elif fingers_up[0] and not fingers_up[1] and not fingers_up[2] and fingers_up[3]:  # Shaka sign
            return "Unlock"
        else:
            return "Unknown"
        
    def update_robot_action(self, gesture):
        """
        Updates the robot's action based on the detected gesture.
        """
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

    def process_video_feed(self):
        """
        Captures video feed and performs gesture detection and robot control.
        """
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to RGB
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

                        # Get landmarks as a list of dictionaries
                        landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in hand_landmarks.landmark]

                        # Classify gesture
                        gesture = self.classify_gesture(landmarks, num_hands)

            # Update robot status based on the gesture
            self.update_robot_action(gesture)

            # Publish gesture using the correct publisher name
            gesture_msg = String()
            gesture_msg.data = gesture
            self.publisher.publish(gesture_msg)  # Corrected to use `self.publisher`

            # Publish robot status
            status_msg = String()
            status_msg.data = self.robot_status
            self.status_publisher.publish(status_msg)

            # Display gesture and robot status
            cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Robot Status: {self.robot_status}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            cv2.imshow("Gesture Detection and Robot Control", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


def main(args=None):
    rclpy.init(args=args)
    gesture_node = GestureRecognitionNode()
    gesture_node.process_video_feed()
    gesture_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()