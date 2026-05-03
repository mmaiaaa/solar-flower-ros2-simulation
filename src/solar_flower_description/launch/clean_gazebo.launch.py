from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, SetEnvironmentVariable
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    world_file = PathJoinSubstitution([
        FindPackageShare("solar_flower_description"),
        "worlds",
        "clean_solar_flower_world.sdf"
    ])

    xacro_file = PathJoinSubstitution([
        FindPackageShare("solar_flower_description"),
        "urdf",
        "solar_flower_clean_gazebo.urdf.xacro"
    ])

    robot_description = {
        "robot_description": ParameterValue(
            Command(["xacro ", xacro_file]),
            value_type=str
        )
    }

    return LaunchDescription([
        SetEnvironmentVariable(
            name="GZ_SIM_RESOURCE_PATH",
            value="/home/maia/solar_flower_ws/src:/home/maia/solar_flower_ws/install/solar_flower_description/share"
        ),

        ExecuteProcess(
            cmd=["gz", "sim", "-r", world_file],
            output="screen"
        ),

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[robot_description],
            output="screen"
        ),

        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package="ros_gz_sim",
                    executable="create",
                    arguments=[
                        "-topic", "robot_description",
                        "-name", "solar_flower_clean",
                        "-x", "0",
                        "-y", "0",
                        "-z", "0.0"
                    ],
                    output="screen"
                )
            ]
        ),

        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package="ros_gz_bridge",
                    executable="parameter_bridge",
                    arguments=[
                        "/azimuth_cmd_pos@std_msgs/msg/Float64@gz.msgs.Double",
                        "/tilt_cmd_pos@std_msgs/msg/Float64@gz.msgs.Double",
                        "/red_petal_cmd_pos@std_msgs/msg/Float64@gz.msgs.Double",
                        "/blue_petal_cmd_pos@std_msgs/msg/Float64@gz.msgs.Double",
                        "/green_petal_cmd_pos@std_msgs/msg/Float64@gz.msgs.Double",
                    ],
                    output="screen"
                )
            ]
        ),
    ])
