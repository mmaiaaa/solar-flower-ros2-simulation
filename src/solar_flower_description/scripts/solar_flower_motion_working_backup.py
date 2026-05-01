#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_srvs.srv import Trigger


class SolarFlowerMotion(Node):
    def __init__(self):
        super().__init__("solar_flower_motion")

        self.publisher = self.create_publisher(JointState, "/joint_states", 10)

        self.joint_names = [
            "azimuth_joint",
            "tilt_joint",
            "red_petal_joint",
            "blue_petal_joint",
            "green_petal_joint",
        ]

        # Current joint positions in radians
        self.positions = {
            "azimuth_joint": 0.0,
            "tilt_joint": 0.0,
            "red_petal_joint": 0.0,
            "blue_petal_joint": 0.0,
            "green_petal_joint": 0.0,
        }

        # Deployed pose: your CAD was exported in deployed state, so petals = 0 rad
        self.deployed_pose = {
            "azimuth_joint": 0.0,
            "tilt_joint": 0.0,
            "red_petal_joint": 0.0,
            "blue_petal_joint": 0.0,
            "green_petal_joint": 0.0,
        }

        # Folded pose based on your petal angle limits
        self.folded_pose = {
            "azimuth_joint": 0.0,
            "tilt_joint": 0.0,
            "red_petal_joint": -3.142,
            "blue_petal_joint": -2.094,
            "green_petal_joint": -1.309,
        }

        self.mode = "stop"
        self.time = 0.0
        self.target_pose = self.deployed_pose.copy()

        self.create_service(Trigger, "/deploy_flower", self.deploy_callback)
        self.create_service(Trigger, "/fold_flower", self.fold_callback)
        self.create_service(Trigger, "/track_sun", self.track_callback)
        self.create_service(Trigger, "/stop_motion", self.stop_callback)

        self.timer = self.create_timer(0.02, self.update)  # 50 Hz

        self.get_logger().info("Solar flower motion node started.")
        self.get_logger().info("Available services: /deploy_flower, /fold_flower, /track_sun, /stop_motion")

    def deploy_callback(self, request, response):
        self.mode = "pose"
        self.target_pose = self.deployed_pose.copy()
        response.success = True
        response.message = "Deploying flower."
        return response

    def fold_callback(self, request, response):
        self.mode = "pose"
        self.target_pose = self.folded_pose.copy()
        response.success = True
        response.message = "Folding flower."
        return response

    def track_callback(self, request, response):
        self.mode = "track"
        self.time = 0.0

        # Keep flower deployed while sun tracking
        self.positions["red_petal_joint"] = 0.0
        self.positions["blue_petal_joint"] = 0.0
        self.positions["green_petal_joint"] = 0.0

        response.success = True
        response.message = "Starting simulated sun tracking."
        return response

    def stop_callback(self, request, response):
        self.mode = "stop"
        response.success = True
        response.message = "Stopping motion."
        return response

    def move_toward_target(self, step=0.015):
        for joint in self.joint_names:
            current = self.positions[joint]
            target = self.target_pose[joint]
            error = target - current

            if abs(error) < step:
                self.positions[joint] = target
            else:
                self.positions[joint] += step if error > 0 else -step

    def update_sun_tracking(self):
        self.time += 0.02

        # Simulated sun path
        # Azimuth sweeps left-right slowly
        self.positions["azimuth_joint"] = 1.2 * math.sin(0.25 * self.time)

        # Tilt moves up/down more gently
        self.positions["tilt_joint"] = 0.25 + 0.18 * math.sin(0.25 * self.time + 0.8)

        # Petals remain deployed during tracking
        self.positions["red_petal_joint"] = 0.0
        self.positions["blue_petal_joint"] = 0.0
        self.positions["green_petal_joint"] = 0.0

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [self.positions[name] for name in self.joint_names]
        self.publisher.publish(msg)

    def update(self):
        if self.mode == "pose":
            self.move_toward_target()

        elif self.mode == "track":
            self.update_sun_tracking()

        self.publish_joint_states()


def main(args=None):
    rclpy.init(args=args)
    node = SolarFlowerMotion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
