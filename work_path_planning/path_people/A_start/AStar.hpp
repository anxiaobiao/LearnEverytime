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
    struct Vec2i	//������������صȺ�
    {
		float x, y, z;	//��int��Ϊfloat��ԭ�����������Ϊ�����ͣ����Ժ���ķ���ҲҪ��Ϊfloat

        bool operator == (const Vec2i& coordinates_);
    };

	using uint = float;	// ���н������int����float����unsigned int��Ϊfloat
    using HeuristicFunction = std::function<uint(Vec2i, Vec2i)>;	//������װ����ͨ�ö�̬
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
		bool detectCollision(Vec2i coordinates_);	//�����ײ
        Node* findNodeOnList(NodeSet& nodes_, Vec2i coordinates_);
        void releaseNodes(NodeSet& nodes_);

    public:
        Generator(float n_, float m_);
        void setWorldSize(Vec2i worldSize_);
        void setDiagonalMovement(bool enable_);	//���öԽ����ƶ�
        void setHeuristic(HeuristicFunction heuristic_);

		void setCoordinatesMap(CoordinateList coordinatesmap_);	//���������ֵ�
		uint cost(Vec2i begin_, Vec2i end_, int alpha, float angle);		// ���ۺ���

        CoordinateList findPath(Vec2i source_, Vec2i target_, int alpha, float angle);
		//void addCollision(Vec2i coordinates_);//�����ײ
		void addCollision(CoordinateList coordinates_);//�����ײ
        void removeCollision(Vec2i coordinates_);
        void clearCollisions();

    private:
        HeuristicFunction heuristic;
        CoordinateList direction, walls;
        Vec2i worldSize;
        uint directions;
		CoordinateMap coordinatemap;
    };

    class Heuristic	//���뷽��
    {
        static Vec2i getDelta(Vec2i source_, Vec2i target_);

    public:
        static uint manhattan(Vec2i source_, Vec2i target_);
        static uint euclidean(Vec2i source_, Vec2i target_);
        static uint octagonal(Vec2i source_, Vec2i target_);
    };
}

#endif // __ASTAR_HPP_8F637DB91972F6C878D41D63F7E7214F__
