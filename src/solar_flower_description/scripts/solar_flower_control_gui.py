#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


class SolarFlowerControlGUI(Node):
    def __init__(self):
        super().__init__("solar_flower_control_gui")

        self.service_clients = {
            "Deploy": self.create_client(Trigger, "/deploy_flower"),
            "Fold": self.create_client(Trigger, "/fold_flower"),
            "Track Sun": self.create_client(Trigger, "/track_sun"),
            "Stop": self.create_client(Trigger, "/stop_motion"),
        }

        self.root = tk.Tk()
        self.root.title("Solar Flower Control")
        self.root.geometry("520x420")
        self.root.minsize(420, 320)
        self.root.resizable(True, True)

        title = tk.Label(
            self.root,
            text="Solar Flower Control",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=15)

        subtitle = tk.Label(
            self.root,
            text="Gazebo Motion Commands",
            font=("Arial", 10)
        )
        subtitle.pack(pady=2)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        self.create_button(button_frame, "Deploy", 0, 0)
        self.create_button(button_frame, "Fold", 0, 1)
        self.create_button(button_frame, "Track Sun", 1, 0)
        self.create_button(button_frame, "Stop", 1, 1)

        self.status_label = tk.Label(
            self.root,
            text="Status: Ready",
            font=("Arial", 10),
            fg="green"
        )
        self.status_label.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def create_button(self, parent, label, row, col):
        button = tk.Button(
            parent,
            text=label,
            width=12,
            height=2,
            command=lambda: self.call_service(label)
        )
        button.grid(row=row, column=col, padx=10, pady=10)

    def call_service(self, label):
        client = self.service_clients[label]

        if not client.wait_for_service(timeout_sec=1.0):
            self.status_label.config(
                text=f"Status: {label} service unavailable",
                fg="red"
            )
            return

        request = Trigger.Request()
        future = client.call_async(request)
        future.add_done_callback(lambda f: self.handle_response(label, f))

        self.status_label.config(
            text=f"Status: Sending {label} command...",
            fg="blue"
        )

    def handle_response(self, label, future):
        try:
            response = future.result()
            if response.success:
                self.status_label.config(
                    text=f"Status: {response.message}",
                    fg="green"
                )
            else:
                self.status_label.config(
                    text=f"Status: {label} failed",
                    fg="red"
                )
        except Exception as error:
            self.status_label.config(
                text=f"Status: Error calling {label}",
                fg="red"
            )
            self.get_logger().error(str(error))

    def spin_once(self):
        rclpy.spin_once(self, timeout_sec=0.01)
        self.root.after(20, self.spin_once)

    def close(self):
        self.root.destroy()
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    gui = SolarFlowerControlGUI()
    gui.root.after(20, gui.spin_once)
    gui.root.mainloop()


if __name__ == "__main__":
    main()
