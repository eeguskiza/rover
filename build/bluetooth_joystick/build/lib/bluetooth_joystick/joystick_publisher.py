#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class JoystickPublisher(Node):
    def __init__(self):
        super().__init__('joystick_publisher')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # Configuración de /dev/rfcomm1
        self.serial_port = "/dev/rfcomm1"

        # Frecuencia de publicación
        self.timer = self.create_timer(0.1, self.publish_twist)

    def publish_twist(self):
        try:
            # Lee los datos de /dev/rfcomm1
            with open(self.serial_port, 'r') as serial_file:
                data = serial_file.readline().strip()  # Ejemplo: "1234/5678\r\n"

            # Divide los datos en x e y
            try:
                x_str, y_str = data.split('/')
                x = int(x_str)
                y = int(y_str)

                # Normaliza los valores de 0-4095 a -1.0 a 1.0 (asumiendo un ADC de 12 bits)
                linear_x = (x - 2048) / 2048.0
                angular_z = (y - 2048) / 2048.0

                # Crea y publica el mensaje Twist
                twist = Twist()
                twist.linear.x = max(min(linear_x, 1.0), -1.0)  # Limita entre -1 y 1
                twist.angular.z = max(min(angular_z, 1.0), -1.0)  # Limita entre -1 y 1

                self.publisher.publish(twist)

                self.get_logger().info(f"Publicado Twist: linear.x={twist.linear.x}, angular.z={twist.angular.z}")

            except ValueError as e:
                self.get_logger().warn(f"Error al procesar los datos recibidos: {data}. Error: {e}")

        except Exception as e:
            self.get_logger().error(f"Error leyendo /dev/rfcomm1: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = JoystickPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
