import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState


class MyFirstNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.counter = 0
        self.get_logger().info('Node is running!')

        self.battery_pub = self.create_publisher(BatteryState, 'battery_state', 10)

        self.create_timer(1.0, self.timer_callback)
        self.create_timer(5.0, self.battery_callback)

        # Simulated battery level (100% at start)
        self.battery_percentage = 1.0

    def timer_callback(self):
        self.counter += 1
        self.get_logger().info(f'Hello - count: {self.counter}')

    def battery_callback(self):
        msg = BatteryState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.voltage = 12.6 * self.battery_percentage          # Volts
        msg.percentage = self.battery_percentage               # 0.0 - 1.0
        msg.power_supply_status = BatteryState.POWER_SUPPLY_STATUS_DISCHARGING
        msg.power_supply_health = BatteryState.POWER_SUPPLY_HEALTH_GOOD
        msg.power_supply_technology = BatteryState.POWER_SUPPLY_TECHNOLOGY_LION
        msg.present = True

        self.battery_pub.publish(msg)
        self.get_logger().info(
            f'Battery: {self.battery_percentage * 100:.1f}%  |  '
            f'Voltage: {msg.voltage:.2f}V'
        )

        # Simulate slow drain
        self.battery_percentage = max(0.0, self.battery_percentage - 0.01)

        if self.battery_percentage < 0.2:
            self.get_logger().warn('Low battery!')


def main(args=None):
    rclpy.init(args=args)
    node = MyFirstNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
