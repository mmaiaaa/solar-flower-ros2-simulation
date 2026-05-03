#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from std_srvs.srv import Trigger


class DeploymentControllerNode(Node):
    def __init__(self):
        super().__init__("deployment_controller_node")

        # Petal command publishers
        self.red_pub = self.create_publisher(Float64, "/red_petal_cmd_pos", 10)
        self.blue_pub = self.create_publisher(Float64, "/blue_petal_cmd_pos", 10)
        self.green_pub = self.create_publisher(Float64, "/green_petal_cmd_pos", 10)

        # Services
        self.create_service(Trigger, "/deploy_flower", self.deploy_callback)
        self.create_service(Trigger, "/fold_flower", self.fold_callback)
        self.create_service(Trigger, "/stop_deployment", self.stop_callback)

        # Current joint positions, rad
        self.red_position = 0.0
        self.blue_position = 0.0
        self.green_position = 0.0

        # Target joint positions, rad
        self.red_target = 0.0
        self.blue_target = 0.0
        self.green_target = 0.0

        # Motion state
        self.active = False
        self.mode = "idle"

        # Motion speed per update step
        self.step_size = 0.025

        # 50 Hz update loop
        self.timer = self.create_timer(0.02, self.update)

        self.get_logger().info("Deployment controller node started.")
        self.get_logger().info("Services available: /deploy_flower, /fold_flower, /stop_deployment")

    def deploy_callback(self, request, response):
        # Deployed state from Fusion export
        self.red_target = 0.0
        self.blue_target = 0.0
        self.green_target = 0.0

        self.active = True
        self.mode = "deploying"

        response.success = True
        response.message = "Deploying flower petals."
        self.get_logger().info(response.message)
        return response

    def fold_callback(self, request, response):
        # Folded state based on your required petal rotations:
        # red: -180 deg = -3.142 rad
        # blue: -120 deg = -2.094 rad
        # green: -75 deg = -1.309 rad
        self.red_target = -3.142
        self.blue_target = -2.094
        self.green_target = -1.309

        self.active = True
        self.mode = "folding"

        response.success = True
        response.message = "Folding flower petals."
        self.get_logger().info(response.message)
        return response

    def stop_callback(self, request, response):
        self.active = False
        self.mode = "stopped"

        response.success = True
        response.message = "Deployment motion stopped."
        self.get_logger().info(response.message)
        return response

    def move_towards(self, current, target):
        error = target - current

        if abs(error) <= self.step_size:
            return target

        if error > 0:
            return current + self.step_size

        return current - self.step_size

    def publish_positions(self):
        red_msg = Float64()
        blue_msg = Float64()
        green_msg = Float64()

        red_msg.data = float(self.red_position)
        blue_msg.data = float(self.blue_position)
        green_msg.data = float(self.green_position)

        self.red_pub.publish(red_msg)
        self.blue_pub.publish(blue_msg)
        self.green_pub.publish(green_msg)

    def update(self):
        if self.active:
            self.red_position = self.move_towards(self.red_position, self.red_target)
            self.blue_position = self.move_towards(self.blue_position, self.blue_target)
            self.green_position = self.move_towards(self.green_position, self.green_target)

            all_reached = (
                self.red_position == self.red_target and
                self.blue_position == self.blue_target and
                self.green_position == self.green_target
            )

            if all_reached:
                self.active = False
                self.get_logger().info(f"Deployment motion complete: {self.mode}")
                self.mode = "idle"

        self.publish_positions()


def main(args=None):
    rclpy.init(args=args)
    node = DeploymentControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
