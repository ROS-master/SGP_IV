import rclpy
from rclpy.node import Node
import cv2
import tensorflow as tf
import numpy as np
from sensor_msgs.msg import Image
from std_msgs.msg import Bool
from cv_bridge import CvBridge

# Load TensorFlow model
MODEL_PATH = tf.keras.applications.MobileNetV2(weights="imagenet")  # Using MobileNetV2

class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection')

        # ROS 2: Subscribe to camera feed
        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)

        # ROS 2: Publish processed image & detection flag
        self.object_pub = self.create_publisher(Image, '/object_detection', 10)
        self.alert_pub = self.create_publisher(Bool, '/object_detected', 10)

    def image_callback(self, msg):
        # Convert ROS image to OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Preprocess image for TensorFlow
        img_resized = cv2.resize(cv_image, (224, 224))
        img_tensor = tf.convert_to_tensor(img_resized, dtype=tf.float32)
        img_tensor = tf.expand_dims(img_tensor, axis=0)  # Add batch dimension

        # Run object detection (MobileNetV2)
        predictions = MODEL_PATH(img_tensor)
        top_prediction = tf.keras.applications.mobilenet_v2.decode_predictions(predictions.numpy())[0][0]

        object_detected = top_prediction[2] > 0.5  # Confidence threshold

        # Draw detection result on image
        if object_detected:
            cv2.putText(cv_image, f"{top_prediction[1]}: {top_prediction[2]:.2f}",
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Publish processed image
        self.object_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8'))

        # Publish boolean flag if object detected
        alert_msg = Bool()
        alert_msg.data = object_detected
        self.alert_pub.publish(alert_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
