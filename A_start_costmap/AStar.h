/*
    Copyright (c) 2015, Damian Barczynski <daan.net@wp.eu>
    Following tool is licensed under the terms and conditions of the ISC license.
    For more information visit https://opensource.org/licenses/ISC.
*/
#ifndef __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__
#define __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__

#include <opencv2/core/core.hpp> 
#include <opencv2/highgui/highgui.hpp> 
#include <opencv2/imgproc.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/core.hpp> 
#include <opencv2/highgui/highgui.hpp> 
#include <opencv2/imgproc.hpp>
#include <opencv2/imgproc.hpp>

#include <vector>
#include <functional>
#include <set>
#include <string>
#include <deque>
#include <queue>

#include <mutex>
#include "NumCpp.hpp"
#include <unordered_map>

// 障碍
#define BAR 250
#define BOUNDARY 255 // 边界

namespace AStar
{
    struct Vec2i
    {
        int x, y;

        bool operator == (const Vec2i& coordinates_) const;
    };

    using Point = Vec2i;
    using uint = unsigned int;
    using byte = unsigned char;
    using HeuristicFunction = std::function<uint(Vec2i, Vec2i)>;
    using CoordinateList = std::vector<Vec2i>;

    struct Node
    {
        uint G, H;
        Vec2i coordinates;
        Node(const Point& coord_, uint _g, uint _h);
        Node(Vec2i coord_);
        uint getScore();
    };

    using SolpeSet = std::vector<std::vector<byte>>;

    struct hash_function
    {
        size_t  operator ()(const Vec2i& p) const
        {
            return std::hash<int>()(p.x) ^ std::hash<int>()(p.y);
        }
    };

    struct myCmp
    {
        bool operator()(const Node& a, const Node& b)
        {
            return (a.G + a.H) > (b.G + b.H);
        }
    };
    using priorityNodeSet = std::priority_queue<Node, std::vector<Node>, myCmp>;

    class Generator;
    class Worker {
    public:
        Worker() = default;
        Worker(const Worker&) = delete;
        void operator=(const Worker&) = delete;
        Worker(Worker&&) = delete;
        void operator=(Worker&&) = delete;

        AStar::CoordinateList findPathByPriority(const Point& _source, const Point& target_, const Point& upper_left_, const Point& lower_right_, int alpha, Generator& generator, std::vector<std::vector<unsigned char>>& road_weight);
        void clear_data();


        void findPathFromStart(const Point& _source, const Point& target_, int alpha, CoordinateList& path, const Point& upper_left_, const Point& lower_right_, Generator& generator, std::vector<std::vector<unsigned char>>& road_weight);
        void findPathFromEnd(const Point& _source, const Point& target_, int alpha, CoordinateList& path, const Point& upper_left_, const Point& lower_right_, Generator& generator, std::vector<std::vector<unsigned char>>& road_weight);

    private:

        // 线程用
        bool endFind = false;
        Point endTarge{ 0,0 };
        std::unordered_map<Point, uint, hash_function> dend_cost; // 相当于 closedSet 已经遍历 的结点
        std::mutex myTex;

        bool unreachable = false;
    };

    // 预处理及处理文件操作
    class Preprocess
    {
    public:
        SolpeSet read_data(const std::string& str_Path);
        void read_data_dire(Generator& generator, const std::string& dataFilename);
        void read_data_(Generator& generator, std::vector<std::vector<unsigned char>> res);
        void read_data_(Generator& generator, nc::NdArray<float> res);
        void read_data_(AStar::Generator& generator, cv::Mat res);
        void save_data(const std::string& str_Path, const AStar::CoordinateList& data);
        Vec2i match(const std::vector<double>& point, int side_x, int side_y);
    };

    class Generator
    {
        friend class Preprocess;
    public:
        Generator();
        Generator(const Generator&) = delete;
        void operator=(const Generator&) = delete;
        Generator(Generator&&) = delete;
        void operator=(Generator&&) = delete;

        void setDiagonalMovement(bool enable_);
        void setHeuristic(HeuristicFunction heuristic_);
        bool detectCollision(Vec2i coordinates_, Vec2i upper_left_, Vec2i lower_right_);
        const uint getDirections() const { return directions; };
        const SolpeSet& getSolpe() const { return solpe; }
        const CoordinateList& getDirection() const { return direction; }
        const HeuristicFunction& getHeuristic() const { return heuristic; }
        void Generator_clear() {
            std::vector<std::vector<byte>>().swap(solpe);  //清除容器并最小化它的容量，
        };
    private:
        HeuristicFunction heuristic;
        CoordinateList direction;
        uint directions;
        SolpeSet solpe;
    };

    class Heuristic
    {
        static Vec2i getDelta(Vec2i source_, Vec2i target_);

    public:
        static uint manhattan(Vec2i source_, Vec2i target_);
        static uint euclidean(Vec2i source_, Vec2i target_);
        static uint octagonal(Vec2i source_, Vec2i target_);
    };


}

#endif // __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__
