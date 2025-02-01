#!/usr/bin/env python3
import cv2
import mediapipe as mp
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
import math

class GestureRecognitionNode(Node):
    def __init__(self):
        super().__init__('gesture_recog_node')

        # Publishers
        self.publisher = self.create_publisher(String, '/gesture', 10)
        self.status_publisher = self.create_publisher(String, '/robot_status', 10)
        self.speed_publisher = self.create_publisher(Float32, '/robot_speed', 10)  # New speed publisher

        # Mediapipe Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils

        # Robot State
        self.robot_status = "Locked"
        self.locked = True
        self.speed = 0.5  # Default speed

    def classify_gesture(self, landmarks):
        """
        Classifies the hand gesture based on finger positions.
        
        Parameters:
            landmarks (list): List of dictionaries containing hand landmarks.

        Returns:
            str: The recognized gesture.
        """
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]

        # Determine fingers up (1 = up, 0 = down)
        fingers_up = [
            thumb_tip['y'] < landmarks[3]['y'],  # Thumb
            index_tip['y'] < landmarks[6]['y'],  # Index
            middle_tip['y'] < landmarks[10]['y'],  # Middle
            ring_tip['y'] < landmarks[14]['y'],  # Ring
            pinky_tip['y'] < landmarks[18]['y'],  # Pinky
        ]

        # Distance calculations for speed control
        thumb_index_distance = math.hypot(index_tip['x'] - thumb_tip['x'], index_tip['y'] - thumb_tip['y'])
        thumb_pinky_distance = math.hypot(pinky_tip['x'] - thumb_tip['x'], pinky_tip['y'] - thumb_tip['y'])

        # Gesture classification based on unique finger combinations
        if fingers_up == [1, 1, 1, 1, 1]:  
            return "Lock"  # 🖐 (Open palm)
        elif fingers_up == [1, 0, 0, 0, 0]:  
            return "Unlock"  # ✋ (All fingers except thumb)
        elif fingers_up == [0, 1, 0, 0, 0]:  
            return "Forward"  # ☝ (Only index)
        elif fingers_up == [0, 1, 1, 0, 0]:  
            return "Backward"  # ✌ (Index + Middle)
        elif fingers_up == [0, 0, 0, 0, 1]:  
            return "Left"  # 👆 (Only pinky)
        elif fingers_up == [0, 1, 0, 0, 1]:  
            return "Right"  # 🤘 (Index + Pinky)
        
        # Speed Control Gestures
        elif thumb_index_distance < 0.05:  
            return "Increase Speed"  # Pinch Gesture
        elif thumb_pinky_distance < 0.05:  
            return "Decrease Speed"  # Rock-on 🤟

        return "Unknown"

    def update_robot_action(self, gesture):
        """Updates the robot's status (locked/unlocked) and actions."""
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

    def adjust_speed(self, gesture):
        """Adjusts speed when Increase/Decrease Speed gestures are detected."""
        if gesture == "Increase Speed":
            self.speed = min(1.0, self.speed + 0.1)
        elif gesture == "Decrease Speed":
            self.speed = max(0.1, self.speed - 0.1)

        # Publish new speed
        speed_msg = Float32()
        speed_msg.data = self.speed
        self.speed_publisher.publish(speed_msg)

    def process_video_feed(self):
        """Processes video feed and detects gestures in real time."""
        cap = cv2.VideoCapture(0)
        try:
            while rclpy.ok() and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

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
                            gesture = self.classify_gesture(landmarks)

                self.update_robot_action(gesture)
                self.adjust_speed(gesture)

                # Publish gesture
                gesture_msg = String()
                gesture_msg.data = gesture
                self.publisher.publish(gesture_msg)

                # Publish robot status
                status_msg = String()
                status_msg.data = self.robot_status
                self.status_publisher.publish(status_msg)

                # Display output on video frame
                cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Robot Status: {self.robot_status}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(frame, f"Speed: {self.speed:.2f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                cv2.imshow("Gesture Detection and Robot Control", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()


def main(args=None):
    rclpy.init(args=args)
    gesture_node = GestureRecognitionNode()
    
    try:
        gesture_node.process_video_feed()
    finally:
        gesture_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
