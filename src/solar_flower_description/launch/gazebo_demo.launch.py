from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, SetEnvironmentVariable
from launch.substitutions import Command, PathJoinSubstitution, EnvironmentVariable
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = "solar_flower_description"

    package_share = FindPackageShare(package_name)

    world_file = PathJoinSubstitution([
        package_share,
        "worlds",
        "green_solar_world.sdf"
    ])

    xacro_file = PathJoinSubstitution([
        package_share,
        "urdf",
        "solar_flower.urdf.xacro"
    ])

    robot_description = {
        "robot_description": Command(["xacro ", xacro_file])
    }

    # Gazebo needs this path to resolve model://solar_flower_description/meshes/...
    gz_resource_path = [
        EnvironmentVariable("HOME"),
        "/solar_flower_ws/src:",
        EnvironmentVariable("HOME"),
        "/solar_flower_ws/install/solar_flower_description/share"
    ]

    return LaunchDescription([

        SetEnvironmentVariable(
            name="GZ_PARTITION",
            value="solar_flower_test"
        ),

        SetEnvironmentVariable(
            name="GZ_SIM_RESOURCE_PATH",
            value=gz_resource_path
        ),

        ExecuteProcess(
            cmd=["gz", "sim", world_file],
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
                        "-world", "green_solar_world",
                        "-topic", "robot_description",
                        "-name", "solar_flower",
                        "-x", "0",
                        "-y", "0",
                        "-z", "0.5"
                    ],
                    output="screen"
                )
            ]
        )
    ])
