#include"comm/listen_odom_topic.h"

listen_odom_topic::listen_odom_topic() : Node("listen_odom_topic")
{
    RCLCPP_INFO(this->get_logger(), "listen odom topic is created");

    last_point.x = 0.0;
    last_point.y = 0.0;
    last_point.z = 0.0;

    conn_topic();
}

void listen_odom_topic::conn_topic()
{
    _odom = this->create_subscription<nav_msgs::msg::Odometry>(
        "/odom",
        10,
        std::bind(&listen_odom_topic::listen_odom, this, std::placeholders::_1)
    );

    _pose = this->create_publisher<geometry_msgs::msg::Twist>(
        "/turtle1/cmd_vel",
        10
    );
}

void listen_odom_topic::listen_odom(nav_msgs::msg::Odometry::SharedPtr odom)
{
    rclcpp::Rate rate(1);

    auto orient = odom->pose.pose.orientation;
    auto point = odom->pose.pose.position;
    // auto linear = odom->twist.twist.linear;
    // auto angular = odom->twist.twist.angular;

    tf2::Quaternion qtn(orient.x, orient.y, orient.z, orient.w);

    double roll, pitch, yaw;//定义存储r\p\y的容器
    tf2::Matrix3x3 m(qtn);
    m.getRPY(roll, pitch, yaw);//进行转换

    RCLCPP_INFO(this->get_logger(), "position   x:%.2f, y:%.2f, z:%.2f", point.x, point.y, point.z);
    RCLCPP_INFO(this->get_logger(), "direction  roll:%.2f, pitch:%.2f, yaw:%.2f", roll, pitch, yaw);
    // RCLCPP_INFO(this->get_logger(), "direction  linear.x:%.2f, linear.y:%.2f, linear.z:%.2f", linear.x, linear.y, linear.z);
    // RCLCPP_INFO(this->get_logger(), "direction  angular.x:%.2f, angular.y:%.2f, angular.z:%.2f", angular.x, angular.y, angular.z);

    double distance = std::sqrt(std::pow(point.x - last_point.x, 2) + std::pow(point.y - last_point.y, 2));

    geometry_msgs::msg::Twist twist;
    twist.linear.x = distance;
    twist.angular.z = yaw - last_angle;

    last_angle = yaw;
    last_point = point;

    _pose->publish(twist);

    rate.sleep();

    // geometry_msgs::msg::Twist twist;
    // twist.linear.x = odom->twist.twist.linear.x;
    // twist.angular.z = odom->twist.twist.angular.z;

    // _pose->publish(twist);
}

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto listen = std::make_shared<listen_odom_topic>();
    rclcpp::spin(listen);
    rclcpp::shutdown();

    return 0;
}