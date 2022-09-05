/*
    Copyright (c) 2015, Damian Barczynski <daan.net@wp.eu>
    Following tool is licensed under the terms and conditions of the ISC license.
    For more information visit https://opensource.org/licenses/ISC.
*/
#ifndef __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__
#define __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__

#include <vector>
#include <functional>
#include <set>

namespace AStar
{
    struct Vec2i
    {
        int x, y;

        bool operator == (const Vec2i& coordinates_);
    };

    using uint = unsigned int;
    using HeuristicFunction = std::function<uint(Vec2i, Vec2i)>;
    using CoordinateList = std::vector<Vec2i>;

    struct Node
    {
        uint G, H;
        Vec2i coordinates;
        Node *parent;

        Node(Vec2i coord_, Node *parent_ = nullptr);
        uint getScore();
    };

	using NodeSet = std::vector<Node*>;
	using SolpeSet = std::vector<std::vector<uint>>;

    class Generator
    {
        bool detectCollision(Vec2i coordinates_, Vec2i upper_left_, Vec2i lower_right_);
        Node* findNodeOnList(NodeSet& nodes_, Vec2i coordinates_);
		Node* findNodeRecentList(NodeSet& nodes_, Vec2i coordinates_);
        void releaseNodes(NodeSet& nodes_);

    public:
        Generator();
        void setWorldSize(Vec2i worldSize_);
        void setDiagonalMovement(bool enable_);
        void setHeuristic(HeuristicFunction heuristic_);
        CoordinateList findPath(Vec2i source_, Vec2i target_, Vec2i upper_left_, Vec2i lower_right_, int alpha);
        void addCollision(CoordinateList coordinates_);
        void removeCollision(Vec2i coordinates_);
        void clearCollisions();

		void setSolpe(SolpeSet solpe_);

    private:
        HeuristicFunction heuristic;
        CoordinateList direction, walls;
        Vec2i worldSize;
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

	// 预处理及处理文件操作
	class Preprocess
	{
	public:
		SolpeSet read_data(std::string str_Path);
		void save_data(std::string str_Path, CoordinateList data);
		void save_data(std::string str_Path, std::vector<AStar::CoordinateList> data);
		Vec2i match(std::vector<float> point, int side_x, int side_y);
	};

	// 针对泛函方式的this做补充
	class GeneratorAdapter
	{
	private:
		Generator *t;
	public:
		GeneratorAdapter(Generator *t_) :t(t_) {}
		CoordinateList operator()(Vec2i source_, Vec2i target_, Vec2i upper_left_, Vec2i lower_right_, int alpha);
	};

}

// 定义全局变量放路径
//extern std::vector<AStar::CoordinateList> all_path;

#endif // __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__
