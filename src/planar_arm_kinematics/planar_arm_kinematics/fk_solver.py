import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Point, TransformStamped
from tf2_ros import TransformBroadcaster
import math


class FKSolver(Node):

    def __init__(self):
        super().__init__('fk_solver')

        # Subscriber
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10)

        # Publisher
        self.publisher = self.create_publisher(Point, '/end_effector_position', 10)

        # TF Broadcaster
        self.br = TransformBroadcaster(self)

        # Link lengths
        self.L1 = 0.4
        self.L2 = 0.3
        self.L3 = 0.2

    def joint_callback(self, msg):

        if len(msg.position) < 3:
            return

        theta1 = msg.position[0]
        theta2 = msg.position[1]
        theta3 = msg.position[2]

        # Forward Kinematics
        x = self.L1 * math.cos(theta1) + \
            self.L2 * math.cos(theta1 + theta2) + \
            self.L3 * math.cos(theta1 + theta2 + theta3)

        y = self.L1 * math.sin(theta1) + \
            self.L2 * math.sin(theta1 + theta2) + \
            self.L3 * math.sin(theta1 + theta2 + theta3)

        # Publish position
        point = Point()
        point.x = x
        point.y = y
        point.z = 0.0
        self.publisher.publish(point)

        # Broadcast TF
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'computed_end_effector'

        t.transform.translation.x = x
        t.transform.translation.y = y
        t.transform.translation.z = 0.0

        t.transform.rotation.w = 1.0

        self.br.sendTransform(t)

        # Print output
        self.get_logger().info(f"Joint: [{theta1:.2f}, {theta2:.2f}, {theta3:.2f}] → (x={x:.3f}, y={y:.3f})")


def main(args=None):
    rclpy.init(args=args)
    node = FKSolver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
