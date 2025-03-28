from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node

def generate_launch_description():
    gesture_detect_node = Node(
        package='gesture_control',
        executable='gesture_detect',
        name='gesture_detect',
        output='screen'
    )

    gesture_control_node = Node(
        package='gesture_control',
        executable='gesture_control',
        name='gesture_control',
        output='screen'
    )

    # obj_detection_node = Node(
    #     package='gesture_control',
    #     executable='object_detector',
    #     name='object_detector',
    #     output='screen'
    # )
    return LaunchDescription([
        gesture_detect_node,
        gesture_control_node,
        # obj_detection_node,
        # Ensure gesture_control stops if gesture_detect exits
        RegisterEventHandler(
            OnProcessExit(
                target_action=gesture_detect_node,
                on_exit=[gesture_control_node]
            )
        ),
    ])
