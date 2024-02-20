from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    simulat_dir = get_package_share_directory('simulat')
    # comm_dir = get_package_share_directory('comm')

    comm_topic = Node(
        package='comm',
        executable='listen_odom_topic',
        name='listen_odom_topic'
    )

    turtle1 = Node(
        package='turtlesim',
        executable='turtlesim_node',
    )

    simulat_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([simulat_dir,'/launch','/display_gazebo_launch.py']),
        )
    
    ld = LaunchDescription()
    ld.add_action(simulat_launch)
    ld.add_action(comm_topic)
    ld.add_action(turtle1)
    return ld