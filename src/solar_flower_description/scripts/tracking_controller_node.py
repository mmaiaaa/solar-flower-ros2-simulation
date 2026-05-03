#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class TrackingControllerNode(Node):
    def __init__(self):
        super().__init__("tracking_controller_node")

        self.sun_azimuth_deg = 90.0
        self.sun_elevation_deg = 35.0

        self.servo1_pub = self.create_publisher(Float64, "/servo1/command_rad", 10)
        self.servo2_pub = self.create_publisher(Float64, "/servo2/command_rad", 10)

        self.create_subscription(
            Float64,
            "/sun/azimuth_deg",
            self.azimuth_callback,
            10
        )

        self.create_subscription(
            Float64,
            "/sun/elevation_deg",
            self.elevation_callback,
            10
        )

        self.timer = self.create_timer(0.02, self.update)

        self.get_logger().info("Tracking controller node started.")

    def azimuth_callback(self, msg):
        self.sun_azimuth_deg = msg.data

    def elevation_callback(self, msg):
        self.sun_elevation_deg = msg.data

    def clamp(self, value, lower, upper):
        return max(lower, min(value, upper))

    def update(self):
        # Servo 1 physical range: 20 to 180 deg.
        servo1_deg = self.clamp(self.sun_azimuth_deg, 20.0, 180.0)

        # Convert physical servo angle into Gazebo joint angle.
        # Your current Gazebo azimuth motion uses about -1.2 to +1.2 rad.
        servo1_rad = math.radians(servo1_deg - 90.0)
        servo1_rad = self.clamp(servo1_rad, -1.2, 1.2)

        # Servo 2 physical range: 90 to 120 deg.
        # Map sun elevation into 90–120 deg.
        servo2_deg = 90.0 + (self.sun_elevation_deg / 90.0) * 30.0
        servo2_deg = self.clamp(servo2_deg, 90.0, 120.0)

        # Convert to Gazebo tilt joint range.
        # Your current Gazebo tilt motion is around 0.07 to 0.43 rad.
        servo2_rad = math.radians(servo2_deg - 90.0)
        servo2_rad = self.clamp(servo2_rad, 0.0, 0.52)

        servo1_msg = Float64()
        servo2_msg = Float64()

        servo1_msg.data = servo1_rad
        servo2_msg.data = servo2_rad

        self.servo1_pub.publish(servo1_msg)
        self.servo2_pub.publish(servo2_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TrackingControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
