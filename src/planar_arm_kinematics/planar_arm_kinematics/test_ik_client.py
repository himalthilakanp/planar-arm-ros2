import rclpy
from rclpy.node import Node
from planar_arm_interfaces.srv import ComputeIK

def main():
    rclpy.init()
    node = Node("ik_test_client")

    client = node.create_client(ComputeIK, '/compute_ik')

    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info("Waiting for service...")

    test_cases = [
        (0.5, 0.4),
        (0.0, 0.0),
        (1.5, 1.5)
    ]

    for x, y in test_cases:
        req = ComputeIK.Request()
        req.target_x = x
        req.target_y = y

        future = client.call_async(req)
        rclpy.spin_until_future_complete(node, future)

        res = future.result()

        print(f"\nTarget: ({x}, {y})")
        print("Success:", res.success)
        print("Message:", res.message)
        print("Theta1:", res.theta1)
        print("Theta2:", res.theta2)
        print("Theta3:", res.theta3)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
