#!/usr/bin/env python3

import math
import os
import subprocess
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from std_srvs.srv import Trigger


class SolarFlowerGazeboMotion(Node):
    def __init__(self):
        super().__init__("solar_flower_gazebo_motion")

        self.command_topics = {
            "azimuth_joint": "/azimuth_cmd_pos",
            "tilt_joint": "/tilt_cmd_pos",
            "red_petal_joint": "/red_petal_cmd_pos",
            "blue_petal_joint": "/blue_petal_cmd_pos",
            "green_petal_joint": "/green_petal_cmd_pos",
            "sun_joint": "/sun_cmd_pos",
        }

        self.cmd_publishers = {
            joint: self.create_publisher(Float64, topic, 10)
            for joint, topic in self.command_topics.items()
        }

        self.positions = {
            "azimuth_joint": 0.0,
            "tilt_joint": 0.0,
            "red_petal_joint": 0.0,
            "blue_petal_joint": 0.0,
            "green_petal_joint": 0.0,
            "sun_joint": 0.0,
        }

        self.deployed_pose = {
            "azimuth_joint": 0.0,
            "tilt_joint": 0.0,
            "red_petal_joint": 0.0,
            "blue_petal_joint": 0.0,
            "green_petal_joint": 0.0,
            "sun_joint": 0.0,
        }

        self.folded_pose = {
            "azimuth_joint": 0.0,
            "tilt_joint": 0.0,
            "red_petal_joint": -3.142,
            "blue_petal_joint": -2.094,
            "green_petal_joint": -1.309,
            "sun_joint": 0.0,
        }

        self.mode = "stop"
        self.target_pose = self.deployed_pose.copy()
        self.time = 0.0
        self.sun_update_counter = 0
        self.external_azimuth_command = 0.0
        self.external_tilt_command = 0.25
        self.use_external_tracking = True

        self.create_service(Trigger, "/deploy_flower", self.deploy_callback)
        self.create_service(Trigger, "/fold_flower", self.fold_callback)
        self.create_service(Trigger, "/track_sun", self.track_callback)
        self.create_service(Trigger, "/stop_motion", self.stop_callback)

        self.create_subscription(
            Float64,
            "/servo1/command_rad",
            self.servo1_command_callback,
            10
        )

        self.create_subscription(
            Float64,
            "/servo2/command_rad",
            self.servo2_command_callback,
            10
        )

        self.timer = self.create_timer(0.02, self.update)

        self.get_logger().info("Solar flower Gazebo motion node started.")
        self.get_logger().info("Services: /deploy_flower, /fold_flower, /track_sun, /stop_motion")

    def servo1_command_callback(self, msg):
        self.external_azimuth_command = msg.data

    def servo2_command_callback(self, msg):
        self.external_tilt_command = msg.data

    def deploy_callback(self, request, response):
        self.mode = "pose"
        self.target_pose = self.deployed_pose.copy()
        response.success = True
        response.message = "Deploying flower in Gazebo."
        return response

    def fold_callback(self, request, response):
        self.mode = "pose"
        self.target_pose = self.folded_pose.copy()
        response.success = True
        response.message = "Folding flower in Gazebo."
        return response

    def track_callback(self, request, response):
        self.mode = "track"
        self.time = 0.0

        self.positions["red_petal_joint"] = 0.0
        self.positions["blue_petal_joint"] = 0.0
        self.positions["green_petal_joint"] = 0.0
        self.positions["sun_joint"] = 0.7 * math.sin(0.25 * self.time)

        response.success = True
        response.message = "Starting Gazebo sun-tracking motion."
        return response

    def stop_callback(self, request, response):
        self.mode = "stop"
        response.success = True
        response.message = "Stopping Gazebo motion."
        return response

    def move_toward_target(self, step=0.015):
        for joint, target in self.target_pose.items():
            current = self.positions[joint]
            error = target - current

            if abs(error) < step:
                self.positions[joint] = target
            else:
                self.positions[joint] += step if error > 0 else -step

    def update_sun_tracking(self):
        self.time += 0.02

        # Move visible sun marker in Gazebo
        self.move_sun_marker()

        if self.use_external_tracking:
            # Use commands from tracking_controller_node
            self.positions["azimuth_joint"] = self.external_azimuth_command
            self.positions["tilt_joint"] = self.external_tilt_command
        else:
            # Fallback scripted tracking motion
            self.positions["azimuth_joint"] = 1.2 * math.sin(0.25 * self.time)
            self.positions["tilt_joint"] = 0.25 + 0.18 * math.sin(0.25 * self.time + 0.8)

        # Petals remain deployed during tracking
        self.positions["red_petal_joint"] = 0.0
        self.positions["blue_petal_joint"] = 0.0
        self.positions["green_petal_joint"] = 0.0

    def move_sun_marker(self):
     self.sun_update_counter += 1

     # Run pose update at 10 Hz instead of every control tick
     if self.sun_update_counter % 5 != 0:
        return

     sun_x = 1.4 * math.sin(0.25 * self.time)
     sun_y = -0.8
     sun_z = 1.3 + 0.4 * math.cos(0.25 * self.time)

     request = (
        f'name: "moving_sun" '
        f'position {{x: {sun_x:.3f} y: {sun_y:.3f} z: {sun_z:.3f}}}'
     )

     subprocess.run(
        [
            "gz", "service",
            "-s", "/world/green_solar_world/set_pose",
            "--reqtype", "gz.msgs.Pose",
            "--reptype", "gz.msgs.Boolean",
            "--timeout", "100",
            "--req", request,
        ],
        env={**os.environ, "GZ_PARTITION": "solar_flower_test"},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
     )

    def publish_commands(self):
        for joint, publisher in self.cmd_publishers.items():
            msg = Float64()
            msg.data = float(self.positions[joint])
            publisher.publish(msg)

    def update(self):
        if self.mode == "pose":
            self.move_toward_target()
        elif self.mode == "track":
            self.update_sun_tracking()

        self.publish_commands()


def main(args=None):
    rclpy.init(args=args)
    node = SolarFlowerGazeboMotion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
