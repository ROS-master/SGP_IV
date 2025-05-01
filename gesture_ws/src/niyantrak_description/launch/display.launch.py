from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare 

def generate_launch_description():

    urdf_path = PathJoinSubstitution([
        FindPackageShare("niyantrak_description"),
        "urdf",
        "my_robot.urdf.xacro"
    ])
    
    gazebo_params_file = PathJoinSubstitution([
        FindPackageShare("niyantrak_description"),
        "config",
        "gazebo_params.yaml"
    ])

    world_file = PathJoinSubstitution([
        FindPackageShare("turtlebot3_gazebo"),
        "worlds",
        "turtlebot3_house.world"
    ])

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[{
                'robot_description': Command(['xacro ', urdf_path])
            }]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])]),
            launch_arguments={
                'world': world_file
            }.items(),
        ),

        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=['-topic', 'robot_description', '-entity', 'my_robot','-x', '1.0', '-y', '-5.0','-z', '0.1'],
            output='screen'
        ),

        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["diff_cont"],
            output="screen"
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_broad"],
            output="screen"
        ),
    ])
