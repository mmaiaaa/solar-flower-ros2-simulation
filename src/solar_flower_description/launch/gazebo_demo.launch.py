from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, SetEnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    world_file = "/home/maia/solar_flower_ws/src/solar_flower_description/worlds/green_solar_world.sdf"
    sdf_file = "/home/maia/solar_flower_ws/solar_flower_gazebo.sdf"

    return LaunchDescription([

        SetEnvironmentVariable(
            name="GZ_PARTITION",
            value="solar_flower_test"
        ),

        SetEnvironmentVariable(
            name="GZ_SIM_RESOURCE_PATH",
            value="/home/maia/solar_flower_ws/src:/home/maia/solar_flower_ws/install/solar_flower_description/share"
        ),

        ExecuteProcess(
            cmd=["gz", "sim", world_file],
            output="screen"
        ),

        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package="ros_gz_sim",
                    executable="create",
                    arguments=[
                        "-world", "green_solar_world",
                        "-file", sdf_file,
                        "-name", "solar_flower",
                        "-x", "0",
                        "-y", "0",
                        "-z", "0.5"
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

        TimerAction(
            period=6.0,
            actions=[
                Node(
                    package="solar_flower_description",
                    executable="solar_flower_gazebo_motion.py",
                    output="screen"
                )
            ]
        ),
    ])
