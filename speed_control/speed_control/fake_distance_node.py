"""Fake distance source that publishes synthetic readings on /distance."""

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Range


class FakeDistanceNode(Node):
    """Publish a sawtooth distance signal as sensor_msgs/Range."""

    MAX_RANGE = 5.0
    STEP = 0.1
    MIN_RANGE = 0.0
    TIMER_PERIOD = 0.1
    FIELD_OF_VIEW = 0.5

    def __init__(self):
        """Set up the publisher and the periodic timer."""
        super().__init__('fake_distance_node')
        self.current_range = self.MAX_RANGE
        self.publisher = self.create_publisher(Range, '/distance', 10)
        self.timer = self.create_timer(self.TIMER_PERIOD, self.publish_reading)

    def publish_reading(self):
        """Publish the current reading and advance the sawtooth."""
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'distance_sensor'
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = self.FIELD_OF_VIEW
        msg.min_range = self.MIN_RANGE
        msg.max_range = self.MAX_RANGE
        msg.range = self.current_range
        self.publisher.publish(msg)
        self.current_range = self.current_range - self.STEP
        if self.current_range < self.MIN_RANGE:
            self.current_range = self.MAX_RANGE


def main():
    """Run the node until it is interrupted."""
    rclpy.init()
    node = FakeDistanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
