#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class SunMotionNode(Node):
    def __init__(self):
        super().__init__("sun_motion_node")

        self.azimuth_pub = self.create_publisher(Float64, "/sun/azimuth_deg", 10)
        self.elevation_pub = self.create_publisher(Float64, "/sun/elevation_deg", 10)
        self.intensity_pub = self.create_publisher(Float64, "/sun/intensity", 10)

        self.time = 0.0
        self.timer = self.create_timer(0.02, self.update)

        self.get_logger().info("Sun motion node started.")

    def update(self):
        self.time += 0.02

        # Simulated sun path for presentation.
        azimuth_deg = 90.0 + 70.0 * math.sin(0.25 * self.time)
        elevation_deg = 35.0 + 20.0 * math.sin(0.25 * self.time + 0.8)
        intensity = 1.0

        az_msg = Float64()
        el_msg = Float64()
        intensity_msg = Float64()

        az_msg.data = azimuth_deg
        el_msg.data = elevation_deg
        intensity_msg.data = intensity

        self.azimuth_pub.publish(az_msg)
        self.elevation_pub.publish(el_msg)
        self.intensity_pub.publish(intensity_msg)


def main(args=None):
    rclpy.init(args=args)
    node = SunMotionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
