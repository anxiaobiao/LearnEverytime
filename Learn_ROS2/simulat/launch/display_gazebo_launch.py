import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import ExecuteProcess
import xacro

def generate_launch_description():
    gazebo_dir = os.path.join(get_package_share_directory('simulat'),'world', 'place.world')

    xacro_file = os.path.join(get_package_share_directory('simulat'),
                              'urdf',
                              'small_car_urdf.xacro')

    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    params = {'robot_description': doc.toxml()}

    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so','-s', 'libgazebo_ros_factory.so', gazebo_dir],
        output='screen')
    
    gazebo_load = Node(package='gazebo_ros', executable='spawn_entity.py',
            arguments=[
                '-x','0.0',
                '-y','0.0',
                '-z','2.0',
                '-Y','0.0',  #yaw
                '-entity', 'car',   #gazebo中机器命名
                '-topic','robot_description',
                ],
            output='screen')

    robtot_state_pub = Node(package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[params])

    # joint_state_pub = Node(package="joint_state_publisher", executable="joint_state_publisher")

    # rviz2 = Node(package="rviz2", executable="rviz2",
    #               arguments=["-d", get_package_share_directory("urdf_test") + "/rviz/display.rviz"])

    return LaunchDescription([gazebo,gazebo_load,robtot_state_pub])


