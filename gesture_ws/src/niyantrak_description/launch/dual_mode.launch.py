import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node


def generate_launch_description():

    enable_autonomous = LaunchConfiguration('enable_autonomous', default='true')
    enable_gesture_control = LaunchConfiguration('enable_gesture_control', default='false')


    niyantrak_dir = get_package_share_directory('niyantrak_description')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')


    map_file = os.path.join(niyantrak_dir, 'map', 'bounded.yaml')
    param_file = os.path.join(niyantrak_dir, 'param', 'robo.yaml')
    rviz_config_file = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')


    display_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(niyantrak_dir, 'launch', 'display.launch.py'))
    )

 
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': map_file,
            'use_sim_time': 'true',
            'params_file': param_file
        }.items(),
        condition=IfCondition(enable_autonomous) 
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    gesture_detect_node = Node(
        package='gesture_control',
        executable='gesture_detect',
        name='gesture_detect',
        output='screen',
        condition=IfCondition(enable_gesture_control)  
    )

    gesture_control_node = Node(
        package='gesture_control',
        executable='gesture_control',
        name='gesture_control',
        output='screen',
        condition=IfCondition(enable_gesture_control)
    )

    log_autonomous = LogInfo(condition=IfCondition(enable_autonomous), msg="Launching Autonomous Navigation")
    log_gesture = LogInfo(condition=IfCondition(enable_gesture_control), msg="Launching Gesture Control")

    return LaunchDescription([
        DeclareLaunchArgument('enable_autonomous', default_value='true', description="Enable autonomous navigation"),
        DeclareLaunchArgument('enable_gesture_control', default_value='false', description="Enable gesture control"),

        display_launch,
        log_autonomous,
        navigation_launch,
        rviz_node,
        log_gesture,
        gesture_detect_node,
        gesture_control_node
    ])
