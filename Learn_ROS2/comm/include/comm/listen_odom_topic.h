#include"rclcpp/rclcpp.hpp"
#include"geometry_msgs/msg/twist.hpp"
#include"geometry_msgs/msg/quaternion.hpp"
#include"geometry_msgs/msg/point.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include"nav_msgs/msg/odometry.hpp"
#include "tf2_geometry_msgs/tf2_geometry_msgs.h"
#include"turtlesim/msg/pose.hpp"

class listen_odom_topic : public rclcpp::Node
{
private:
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr _odom;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr _pose;

    double last_angle = 0.0;
    geometry_msgs::msg::Point last_point;

public:
    listen_odom_topic();

    void conn_topic();
    void listen_odom(nav_msgs::msg::Odometry::SharedPtr odom);
};
