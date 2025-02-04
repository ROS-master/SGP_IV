from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare  # Use from launch_ros

def generate_launch_description():

    # Define paths to URDF, RViz, Gazebo files
    urdf_path = PathJoinSubstitution([
        FindPackageShare("niyantrak_description"),
        "urdf",
        "my_robot.urdf.xacro"
    ])
    
    rviz_config_path = PathJoinSubstitution([
        FindPackageShare("niyantrak_description"),
        "rviz",
        "urdf.rviz"
    ])
    
    gazebo_params_file = PathJoinSubstitution([
        FindPackageShare("niyantrak_description"),
        "config",
        "gazebo_params.yaml"
    ])

    world_file = PathJoinSubstitution([
        FindPackageShare("niyantrak_description"),
        "world",
        "charusat.world"
    ])

    # Define the launch description
    return LaunchDescription([
        # Robot state publisher node
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[{
                'robot_description': Command(['xacro ', urdf_path])
            }]
        ),

        # Uncomment to use RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_path]
        ),

        # Include Gazebo launch file
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

        # Spawn entity in Gazebo
        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=['-topic', 'robot_description', '-entity', 'my_robot'],
            output='screen'
        ),

        # Spawner nodes for controllers
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
