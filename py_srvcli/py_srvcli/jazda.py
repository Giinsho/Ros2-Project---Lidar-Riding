from rclpy.qos import QoSProfile
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import LaserScan

from geometry_msgs.msg import Twist
from nav_msgs.msg import Path, Odometry
from rclpy.qos import HistoryPolicy, ReliabilityPolicy


from action_bot.action import Move
from rclpy.action import ActionServer
from geometry_msgs.msg import PoseStamped

import random 

class Jazda(Node):
    def __init__(self):
        super().__init__('jazda_node')  # name of the node
        self.prevValue = {}
        self.counter = 0
        self.checker = 0


        self.clock = None
        self.state_ = 0
        
        self.doors_X = None
        self.doors_Y = None
        
        self.prev_X = None
        self.prev_Y = None
        
        self.set_prev_value = False

        self.state_dict_ = {
            0: 'find the wall',
            1: 'turn left',
            2: 'follow the wall',
            3: 'backup',
            4: 'doors',
            5: 'doorsl',
        }
        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        # publisher
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
  
        
        self._publisher = self.create_publisher(PoseStamped, '/goal_pose', 30)
        
        #SERVER
        self._action_server = ActionServer(
            self,
            Move,
            'move',
            self.execute_callback)
        
        self.get_logger().info("Server is also running")
        
        # publisher 
        self.publisher_odom = self.create_publisher(
            Odometry, '/odometry/filtered', 20)
        # subscriber
        self.subscription_odom = self.create_subscription(Odometry, '/odometry/filtered', self.mapOdom, self.qos_profile)
        
        
        
        self.subscription = self.create_subscription(
                LaserScan, '/scan', self.get_scan_values, self.qos_profile)
        self._action_server = ActionServer(
                self,
                Move,
                'move',
                self.execute_callback)
       
        
       

        self.timer_period = 0.3
        
        self.timer = None
        # Initializing Global values

       
        self.velocity = Twist()

        self.regions = {'right': [], 'rfront': [],
                        'front': [],  'lfront': [], 'left': []}

        return

    def mapOdom(self, msg):
        self.mapPose = {
            "pose": msg.pose.pose,
            "x":msg.pose.pose.position.x,
            "y": msg.pose.pose.position.y
        }
        return 
    def destroyAndStop(self):
        self.linear_vel = 0.0
        for i in range(10):
            self.velocity.angular.z = 0.314
        self.velocity.linear.x = self.linear_vel
        self.publisher.publish(self.velocity)
        self.destroy_timer(self.timer)
        return
    def goToThePoint(self, type, goal_handle):
        
        status = False
        print("Akcja: " + str(type))
        if type.startswith("skanuj"):
            self.linear_vel = 0.22
            self.timer = self.create_timer(
                self.timer_period, self.send_cmd_vel)
        elif type.startswith("stop"):
            self.destroy_timer(self.timer)
        elif type.startswith("kanciapa"):
            self.destroy_timer(self.timer)
            status = self.move(goal_handle, 10.0, -6.0, 0.0)
        elif type.startswith("sypialnia"):
            self.destroy_timer(self.timer)
            status = self.move(goal_handle, 10.0, 6.0, 0.0)
        elif type.startswith("kuchnia"):
            self.destroy_timer(self.timer)
            status = self.move(goal_handle, -5.0, -6.0, 0.0)
        elif type.startswith("korytarz"):
            self.destroy_timer(self.timer)
            status = self.move(goal_handle, 0.0, 0.0, 0.0)
        elif type.startswith("goscinny"):
            self.destroy_timer(self.timer)
            status = self.move(goal_handle, -10.0, 5.0, 0.0)
        elif type.startswith("przedsionek"):
            self.destroy_timer(self.timer)
            status = self.move(goal_handle, 3.0, 12.0, 0.0)
        elif type.startswith("wyjscie"):
            self.destroy_timer(self.timer)
            status = self.move(goal_handle, 4.0, 16.0, 0.0)
        elif type[0].startswith('x'):
            
            variables = type.split(" ")
            x = variables[0].split(":")
            val_x = x[1]
            print(x)
            y = variables[1].split(":")
            val_y = y[1]
            print(y)
            status = self.move(goal_handle, float(val_x), float(val_y), 0.0)
        return status

    def execute_callback(self, goal_handle):
        status = False
        type = goal_handle.request.request

        status = self.goToThePoint(type, goal_handle)

        goal_handle.succeed()
        result = Move.Result()
        result.finish = status
        return result
    
    def move(self, goal_handle, x, y, z):
        msg = PoseStamped()
        msg.header.frame_id = "map"
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = z
        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = 0.0
        msg.pose.orientation.w = 1.0

        self._publisher.publish(msg)
        return True
    
    def get_scan_values(self, scan_data):
        
        if self.state_ == 0:
            self.find_wall()
        elif self.state_ == 1:
            self.turn_left()
        elif self.state_ == 2:
            self.follow_the_wall()
        elif self.state_ == 3:
            self.backup()
        elif self.state_ == 4:
            self.doors()
        elif self.state_ == 5:
            self.doorsl()
            pass
        else:
            print("Unknown state")
        
        self.counter += 1

        if(len(scan_data.ranges) == 0):
            print("Empty Values")
            return

        self.regions = {
            'right': min(min(scan_data.ranges[45:63]), 10),
            'fright': min(min(scan_data.ranges[54:81]), 10),
            'front': min(min(scan_data.ranges[82:99]), 10),
            'fleft': min(min(scan_data.ranges[100:117]), 10),
            'left': min(min(scan_data.ranges[118:135]), 10),
        }

        if(self.counter == 7):
            print("Subscribtion method triggered")
            print(self.regions['left'], " / ",
                  self.regions['front'], " / ", self.regions['right'])
            self.counter = 0

    def send_cmd_vel(self):
        if self.regions == {}:
            return
       
        # # if(self.cmp_dictionaries(self.prevValue, self.regions)):
        # #     self.linear_vel = -0.6
        # if(float(self.regions['left']) > 0.7 and float(self.regions['left-front']) > 0.7 and float(self.regions['mid']) > 0.8 and float(self.regions['right']) >  1.0):
        #     self.velocity.angular.z = -0.1
        #     self.linear_vel = 0.22
        # elif(float(self.regions['left']) > 3.0 and float(self.regions['left-front']) > 3.0 and float(self.regions['mid']) > 3.0 and float(self.regions['right-front']) > 3.0 and float(self.regions['right']) > 3.0):
        #     self.velocity.angular.z = 0.2
        #     self.linear_vel = 0.60

        # elif (float(self.regions['left']) > 0.9 and float(self.regions['left-front']) > 0.9 and float(self.regions['mid']) > 0.9 and float(self.regions['right-front']) > 0.9 and float(self.regions['right']) > 0.9):
        #     self.velocity.angular.z = 0.0  # condition in which area is total clear
        #     self.linear_vel = 0.22
        #     print("I'm goin' forward ")

        # elif(float(self.regions['left']) > 0.9 and float(self.regions['mid']) > 0.9 and float(self.regions['right']) < 0.9 and float(self.regions['left-front']) > 0.7) and float(self.regions['right-front']) > 0.7:
        #     self.velocity.angular.z = 0.1  # object on right,taking left
        #     self.linear_vel = 0.0
        #     print("I'm turnin' left ")

        # elif(float(self.regions['left']) < 0.9 and float(self.regions['mid']) > 0.9 and float(self.regions['right']) > 0.9 and float(self.regions['left-front']) > 0.7 and float(self.regions['right-front']) > 0.7):
        #     self.velocity.angular.z = -0.1  # object on left, taking right
        #     self.linear_vel = 0.0
        #     print("I'm turnin' right ")

        # elif(float(self.regions['left-front']) < 0.9 and float(self.regions['mid']) < 0.9 and float(self.regions['right-front']) > 0.9):
        #     self.velocity.angular.z = -0.1  # object on left, taking right
        #     self.linear_vel = 0.0
        #     print("I'm turnin' right a little ")

        # elif(float(self.regions['right-front']) < 0.9 and float(self.regions['mid']) < 0.9 and float(self.regions['left-front']) > 0.9):
        #     self.velocity.angular.z = 0.1  # object on left, taking right
        #     self.linear_vel = 0.0
        #     print("I'm turnin' left a little  ")

        # elif(float(self.regions['left']) < 0.8 and float(self.regions['mid']) < 0.8 and float(self.regions['right']) < 0.8 and float(self.regions['right-front']) < 0.8 and float(self.regions['right']) < 0.8):
        #     self.linear_vel = -0.6  # object ahead take bigger turn
        #     print("I need to backup :( ")
        # elif(float(self.regions['mid']) < 1.2 and float(self.regions['right']) < 1.2 and float(self.regions['right-front']) < 1.2 and float(self.regions['left']) > 2):
        #     print("Znaleziono kąt: po prawej stronie :))) ")
        # elif(float(self.regions['mid']) < 1.2 and float(self.regions['left']) < 1.2 and float(self.regions['left-front']) < 1.2 and float(self.regions['right']) > 2):
        #     print("Znaleziono kąt: po lewej stronie :))) ")
        # else:
        #     pass  # Code is not completed -> you have to add more conditions ot make it robust
        # self.velocity.linear.x = self.linear_vel
        state_description = ''

   

        d = 1.1

        if self.regions['front'] < 1.0 and (self.regions['fleft'] < 1.0 or self.regions['fright'] < 1.0):
            state_description = 'case 9 - backup'
            self.change_state(3)
        elif self.regions['left'] > 4.0 and ( self.regions['fright'] > 3.0 and self.regions['fright'] < 8.0 and (self.regions['right'] > 5.0 and self.regions['right'] < 8.0)):
            state_description = 'case 10 - doors migh be found on right '
            self.change_state(4)
        elif self.regions['right'] > 4.0 and (self.regions['fleft'] > 3.0 and self.regions['fleft'] < 8.0 and (self.regions['left'] > 5.0 and self.regions['left'] < 8.0)):
            state_description = 'case 10 - doors migh be found on left '
            self.change_state(5)
        elif self.regions['front'] > d and self.regions['fleft'] > d and self.regions['fright'] > d:
            state_description = 'case 1 - nothing'
            self.change_state(0)
        
        elif self.regions['front'] < d and self.regions['fleft'] > d and self.regions['fright'] > d:
            state_description = 'case 2 - front'
            self.change_state(1)
        elif self.regions['front'] > d and self.regions['fleft'] > d and self.regions['fright'] < d:
            state_description = 'case 3 - fright'
            self.change_state(2)
        elif self.regions['front'] > d and self.regions['fleft'] < d and self.regions['fright'] > d:
            state_description = 'case 4 - fleft'
            self.change_state(0)
        elif self.regions['front'] < d and self.regions['fleft'] > d and self.regions['fright'] < d:
            state_description = 'case 5 - front and fright'
            self.change_state(1)
        elif self.regions['front'] < d and self.regions['fleft'] < d and self.regions['fright'] > d:
            state_description = 'case 6 - front and fleft'
            self.change_state(1)
        elif self.regions['front'] < d and self.regions['fleft'] < d and self.regions['fright'] < d:
            state_description = 'case 7 - front and fleft and fright'
            self.change_state(1)
        elif self.regions['front'] > d and self.regions['fleft'] < d and self.regions['fright'] < d:
            state_description = 'case 8 - fleft and fright'
            self.change_state(0)
        
        else:
            state_description = 'unknown case'
            
        ## KĄT FOUNDING  KEKW    
        if(float(self.regions['front']) < d and float(self.regions['right']) < d and float(self.regions['fright']) < d and float(self.regions['left']) > 3.0):
            if(abs(self.mapPose['x'] - self.prev_X) > 0.8 or abs(self.mapPose['y']-self.prev_Y) > 0.8 or self.set_prev_value):
                self.prev_X = self.mapPose['x']
                self.prev_Y = self.mapPose['y']
                self.set_prev_value = False 
                print("Prawdopodobnie znaleziono kąt: po prawej stronie :))) ")
                
        elif(float(self.regions['front']) < d and float(self.regions['left']) < d and float(self.regions['fleft']) < d and float(self.regions['right']) > 3.0):
            if(abs(self.mapPose['x'] - self.prev_X) > 0.8 or abs(self.mapPose['y']-self.prev_Y) > 0.8 or self.set_prev_value):
                self.prev_X = self.mapPose['x']
                self.prev_Y = self.mapPose['y']
                self.set_prev_value = False
                print("Prawdopodobnie znaleziono kąt: po lewej stronie :))) ")
    
            
        if(float(self.regions['front']) < 1.0 and float(self.regions['right']) < 1.0 and float(self.regions['fright']) < 0.7 and float(self.regions['left']) > 3.0):
            print("Prawdopodobnie jestem przy ścianie po prawej stronie ^^ ")
        elif(float(self.regions['front']) < 1.0 and float(self.regions['left']) < 1.0 and float(self.regions['fleft']) < 0.7 and float(self.regions['right']) > 3.0):
            print("Prawdopodobnie jestem przy ścianie po lewej stronie ^^ ")
        
            
   
        
        self.prevValue = self.regions
        print(state_description)

    def change_state(self, state):

        if state is not self.state_:
            print('Wall follower - [%s] - %s' %
                  (state, self.state_dict_[state]))
            self.state_ = state

    def find_wall(self):

        self.linear_vel = 0.22
        
        k = random.randint(0, 1)
        if(k == 1):
            self.velocity.angular.z = 0.34
        else:
            self.velocity.angular.z = -0.34
        self.velocity.linear.x = self.linear_vel
        self.publisher.publish(self.velocity)
        
        
    def backup(self):
        self.linear_vel = -0.4
        self.velocity.angular.z = 0.0
        self.velocity.linear.x = self.linear_vel
        self.publisher.publish(self.velocity)
    
    def doors(self):
        self.linear_vel = 0.0
        self.velocity.angular.z = -1.0
        self.velocity.linear.x = self.linear_vel
        self.publisher.publish(self.velocity)
    
    def doorsl(self):
        self.linear_vel = 0.0
        self.velocity.angular.z = 1.0
        self.velocity.linear.x = self.linear_vel
        self.publisher.publish(self.velocity)
     
        
    def turn_left(self):


        self.linear_vel = 0.0
        self.velocity.angular.z = 0.2
        self.velocity.linear.x = self.linear_vel
        self.publisher.publish(self.velocity)
        

    def follow_the_wall(self):

        self.linear_vel = 0.12
        self.velocity.linear.x = self.linear_vel
        self.velocity.angular.z = 0.0
        self.publisher.publish(self.velocity)
        
        self.prev_X = self.mapPose['x']
        self.prev_Y = self.mapPose['y']
        
        self.set_prev_value = True
        
       

    def cmp_dictionaries(self, d1, d2):
        for key in d1.keys() & d2.keys():
            # print("Value D1 | "+str(d1[key]))
            # print("Value D2 | "+str(d2[key]))
            # print("Key | "+str(key))
            if(abs(d1[key]-d2[key]) < 0.2):
                return True
            else:
                return False


def main(args=None):
    rclpy.init(args=args)
    oab = Jazda()
    rclpy.spin(oab)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
