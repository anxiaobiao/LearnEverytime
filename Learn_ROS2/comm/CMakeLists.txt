cmake_minimum_required(VERSION 3.5)
project(comm)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(turtlesim REQUIRED)

# target_include_directories(listen_odom_topic PUBLIC src/comm/include)
include_directories(include)

add_executable(listen_odom_topic src/listen_odom_topic.cpp)
add_executable(learn_server src/learn_server.cpp)
add_executable(learn_cilent src/learn_cilent.cpp)


ament_target_dependencies(
  listen_odom_topic
  "rclcpp"
  "geometry_msgs"
  "nav_msgs"
  "tf2"
  "tf2_geometry_msgs"
  "turtlesim"
)

ament_target_dependencies(
  learn_server
  "rclcpp"
  "geometry_msgs"
  "nav_msgs"
  "tf2"
  "tf2_geometry_msgs"
  "turtlesim"
  "interface_learn"
)

ament_target_dependencies(
  learn_cilent
  "rclcpp"
  "geometry_msgs"
  "nav_msgs"
  "tf2"
  "tf2_geometry_msgs"
  "turtlesim"
  "interface_learn"
)

install(TARGETS listen_odom_topic learn_cilent learn_server
  DESTINATION lib/${PROJECT_NAME})
  
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # uncomment the line when a copyright and license is not present in all source files
  #set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # uncomment the line when this package is not in a git repo
  #set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
