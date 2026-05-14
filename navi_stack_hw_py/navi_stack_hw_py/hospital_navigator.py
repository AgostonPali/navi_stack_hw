import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class HospitalNavigator(Node):
    def __init__(self):
        super().__init__('hospital_navigator')
        
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Defintion of waypoints: (x, y, w) where w is the orientation in quaternion
        self.waypoints = [
            (2.0, 1.0, 1.0),   
            (5.0, -1.0, 0.7),  
            (8.0, 2.0, 1.0),   
            (0.0, 0.0, 1.0)    
        ]
        self.current_wp_index = 0
        self.retry_count = 0
        
        self.get_logger().info('Waiting for Nav2 server to be available...')
        self.nav_client.wait_for_server()
        self.get_logger().info('The Nav2 server is available. Starting navigation...')
        
        self.send_next_goal()

    def send_next_goal(self):
        if self.current_wp_index < len(self.waypoints):
            x, y, w = self.waypoints[self.current_wp_index]
            
            goal_msg = NavigateToPose.Goal()
            goal_msg.pose.header.frame_id = 'map' 
            goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
            
            # Coordinates and orientation for the goal
            goal_msg.pose.pose.position.x = float(x)
            goal_msg.pose.pose.position.y = float(y)
            goal_msg.pose.pose.orientation.w = float(w)
            
            self.get_logger().info(f'[{self.current_wp_index + 1}/{len(self.waypoints)}] Indulás a célponthoz: x={x}, y={y}')
            
            self._send_goal_future = self.nav_client.send_goal_async(goal_msg)
            self._send_goal_future.add_done_callback(self.goal_response_callback)
        else:
            self.get_logger().info('*** All waypoints visited! ***')

    def goal_response_callback(self, future):
        """Check if the goal was accepted and if so, wait for the result."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('The Nav2 rejected the goal! (It might be that the point is behind a wall or obstacle?)')
            return

        self.get_logger().info('Goal accepted, the robot is on its way...')
        
        # If accepted, wait for the result (when it arrives)
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        status = future.result().status
        
        if status == 4:
            self.get_logger().info('Successfully reached the goal!')
            
            self.current_wp_index += 1
            self.retry_count = 0
            self.send_next_goal()
        else:
            self.get_logger().warn(f'The goal could not be reached. Status code: {status}')
            self.retry_count += 1

            self.timer = self.create_timer(2.0, self.timer_callback)

    def timer_callback(self):
        self.timer.cancel() 
        self.send_next_goal() 

def main(args=None):
    rclpy.init(args=args)
    
    node = HospitalNavigator()
    
    rclpy.spin(node)
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()