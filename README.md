"# Ros2-Project---Lidar-Riding" 
BUILD:
cd /workspace/action_ws
colcon construction
source install/setup.bash
cd /workspace/dev_ws
colcon build --packages-select basic_mobile_robot
colcon build --packages-select py_srvcli
source install/setup.bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/workspace/dev_ws/src/basic_mobile_robot/models/
STARTING:
SERVER:
ros2 run py_srvcli ride
CLIENT:
cd /workspace/dev_ws
python client_bot.py
ROS:
ros2 run basic_mobile_robot basic_mobile_bot_v5.launch.py
If we want to fire from RVIZ, there was a command on some labs that works, I don't remember this addition
MAP EDIT:
gazebo /workspace/dev_ws/src/basic_mobile_robot/worlds/basic_mobile_bot_world/projectWorldEnd.world
ROBOT:
dev_ws\src\basic_mobile_robot\models\basic_mobile_bot_description\model.sdf
ROBOT TEXTURE:
dev_ws\src\basic_mobile_robot\models\basic_mobile_bot_description\meshes.sdf
