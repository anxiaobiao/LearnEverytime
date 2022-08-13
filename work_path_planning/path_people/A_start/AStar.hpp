/*
    Copyright (c) 2015, Damian Barczynski <daan.net@wp.eu>
    Following tool is licensed under the terms and conditions of the ISC license.
    For more information visit https://opensource.org/licenses/ISC.
*/
#ifndef __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__
#define __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__

#include<queue>
#include <vector>
#include <functional>
#include <set>
#include <map>

namespace AStar
{
    struct Vec2i	//定义坐标和重载等号
    {
		float x, y, z;	//从int改为float。原因：输入的数据为浮点型，所以后面的分数也要改为float

        bool operator == (const Vec2i& coordinates_);
    };

	using uint = float;	// 所有结果不是int，是float。从unsigned int改为float
    using HeuristicFunction = std::function<uint(Vec2i, Vec2i)>;	//函数包装器，通用多态
    using CoordinateList = std::vector<Vec2i>;
	using CoordinateMap = std::map<std::pair<float, float>, float>;

    struct Node
    {
        uint G, H;
        Vec2i coordinates;
        Node *parent;

        Node(Vec2i coord_, Node *parent_ = nullptr);
        uint getScore() const;
    };

    using NodeSet = std::vector<Node*>;
	//using Nodeheapq = std::priority_queue<Node, std::vector<Node*>, cmp>;


    class Generator
    {
		bool detectCollision(Vec2i coordinates_);	//检测碰撞
        Node* findNodeOnList(NodeSet& nodes_, Vec2i coordinates_);
        void releaseNodes(NodeSet& nodes_);

    public:
        Generator(float n_, float m_);
        void setWorldSize(Vec2i worldSize_);
        void setDiagonalMovement(bool enable_);	//设置对角线移动
        void setHeuristic(HeuristicFunction heuristic_);

		void setCoordinatesMap(CoordinateList coordinatesmap_);	//设置坐标字典
		uint cost(Vec2i begin_, Vec2i end_, int alpha, float angle);		// 代价函数

        CoordinateList findPath(Vec2i source_, Vec2i target_, int alpha, float angle);
		//void addCollision(Vec2i coordinates_);//添加碰撞
		void addCollision(CoordinateList coordinates_);//添加碰撞
        void removeCollision(Vec2i coordinates_);
        void clearCollisions();

    private:
        HeuristicFunction heuristic;
        CoordinateList direction, walls;
        Vec2i worldSize;
        uint directions;
		CoordinateMap coordinatemap;
    };

    class Heuristic	//距离方程
    {
        static Vec2i getDelta(Vec2i source_, Vec2i target_);

    public:
        static uint manhattan(Vec2i source_, Vec2i target_);
        static uint euclidean(Vec2i source_, Vec2i target_);
        static uint octagonal(Vec2i source_, Vec2i target_);
    };
}

#endif // __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__
