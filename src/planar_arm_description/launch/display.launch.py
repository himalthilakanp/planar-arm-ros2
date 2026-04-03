from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
import os


def generate_launch_description():

    # Get package path
    pkg_share = FindPackageShare('planar_arm_description').find('planar_arm_description')

    # Path to xacro file
    xacro_file = os.path.join(pkg_share, 'urdf', 'planar_arm.urdf.xacro')

    # RViz config path (MOVE THIS OUTSIDE LIST ✅)
    rviz_config = os.path.join(pkg_share, 'rviz', 'display.rviz')

    # Convert xacro → robot_description
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),  # also removed extra space ✔
        value_type=str
    )

    return LaunchDescription([

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description
            }]
        ),

        # Joint State Publisher GUI
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),

        # RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config]   # comma fixed ✔
        )
    ])
