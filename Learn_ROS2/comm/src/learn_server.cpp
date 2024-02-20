#include"comm/learn_server.h"

learn_server::learn_server() : Node("server")
{
    RCLCPP_INFO(this->get_logger(), "server is create");

    listen_odom_topic listen;
}


int main(int argc, char** argv)
{



    return 0;
}