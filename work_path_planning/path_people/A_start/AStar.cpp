#include "AStar.hpp"
#include <algorithm>
#include <math.h>
#include <iostream>

using namespace std::placeholders;

bool AStar::Vec2i::operator == (const Vec2i& coordinates_)
{
    return (x == coordinates_.x && y == coordinates_.y && z == coordinates_.z);
}

AStar::Vec2i operator + (const AStar::Vec2i& left_, const AStar::Vec2i& right_)
{
    return{ left_.x + right_.x, left_.y + right_.y, left_.z + right_.z };
}

AStar::Node::Node(Vec2i coordinates_, Node *parent_)
{
    parent = parent_;
    coordinates = coordinates_;
    G = H = 0;
}

AStar::uint AStar::Node::getScore() const
{
    return G + H;
}

AStar::Generator::Generator(float n_, float m_)	// n表示x轴，m表示y轴，即（n, m）
{
    setDiagonalMovement(false);	//初试为四向，可以改为八向
    setHeuristic(&Heuristic::manhattan);
    direction = {
        { 0, m_ }, { n_, 0 }, { 0, -m_ }, { -n_, 0 },
        { -n_, -m_ }, { n_, m_ }, { -n_, m_ }, { n_, -m_ }
    };
}

void AStar::Generator::setWorldSize(Vec2i worldSize_)
{
    worldSize = worldSize_;
}

void AStar::Generator::setDiagonalMovement(bool enable_)
{
    directions = (enable_ ? 8 : 4);
}

void AStar::Generator::setHeuristic(HeuristicFunction heuristic_)
{
    heuristic = std::bind(heuristic_, _1, _2);	// _1, _2表示占位符，将被传入的参数代替
}

/*
自定义函数，将数据添加到类中,数据放在coordinatemap中。使用字典的方式查询z轴坐标
*/
void AStar::Generator::setCoordinatesMap(CoordinateList coordinatesmap_)
{
	//auto begin = coordinatesmap_.begin();
	//auto end = coordinatesmap_.end();
	//while (begin++ != end)
	//{
	//	auto temp = std::pair<float, float>(begin->x, begin->y);
	//	coordinatemap[temp] = begin->z;
	//	//begin++;
	//}

	for (auto it = coordinatesmap_.begin(); it != coordinatesmap_.end(); ++it) {
		auto temp = std::pair<float, float>(it->x, it->y);
		coordinatemap[temp] = it->z;
	}
	std::cout << "设置字典成功！" << std::endl;

}

/*
void AStar::Generator::addCollision(Vec2i coordinates_)
{
    walls.push_back(coordinates_);
}
*/

void AStar::Generator::addCollision(CoordinateList coordinates_)
{
	auto begin = coordinates_.begin();
	auto end = coordinates_.end();
	while (begin != end)
	{
		//Vec2i temp = begin;
		walls.push_back(*begin);
		++begin;
	}
	std::cout << "设置障碍成功" << std::endl;
}

void AStar::Generator::removeCollision(Vec2i coordinates_)
{
    auto it = std::find(walls.begin(), walls.end(), coordinates_);
    if (it != walls.end()) {
        walls.erase(it);
    }
}

void AStar::Generator::clearCollisions()
{
    walls.clear();
}

AStar::CoordinateList AStar::Generator::findPath(Vec2i source_, Vec2i target_, int alpha, float angle)
{
	//std::cout << angle << std::endl;
	if (std::find(walls.begin(), walls.end(), source_) != walls.end() || std::find(walls.begin(), walls.end(), target_) != walls.end()) {
		std::cout << "起点或终点在障碍中！！！" << std::endl;
		
	}

    Node *current = nullptr;
    NodeSet openSet, closedSet;
    openSet.reserve(100);
    closedSet.reserve(100);
    openSet.push_back(new Node(source_));
	//建立最小堆
	auto cmp = [](Node* x, Node* y) { return x->getScore() > y->getScore(); };
	std::make_heap(openSet.begin(), openSet.end(), cmp);
	int i12 = 1;
    while (!openSet.empty()) {
  //      auto current_it = openSet.begin();
  //      current = *current_it;
		i12 = i12 + 1;
		std::cout << i12 << std::endl;

  //      for (auto it = openSet.begin(); it != openSet.end(); it++) {
  //          auto node = *it;
  //          if (node->getScore() <= current->getScore()) {
  //              current = node;
  //              current_it = it;
  //          }
  //      }

		auto current = openSet.front();

        if (current->coordinates == target_) {
            break;
        }

        closedSet.push_back(current);
        //openSet.erase(current_it);
		std::pop_heap(openSet.begin(), openSet.end(), cmp);
		openSet.pop_back();

        for (uint i = 0; i < directions; ++i) {
			Vec2i newCoordinates(current->coordinates + direction[i]);	// 引入数据坐标
			auto temp = std::pair<float, float>(newCoordinates.x, newCoordinates.y);
			newCoordinates.z = coordinatemap[temp];

            if (detectCollision(newCoordinates) || findNodeOnList(closedSet, newCoordinates)) {
                continue;
            }

            //uint totalCost = current->G + ((i < 4) ? 10 : 14);	//修改cost
			uint totalCost = current->G + cost(current->coordinates, newCoordinates, alpha, angle);	//起点 当前点 下一个可能点

            Node *successor = findNodeOnList(openSet, newCoordinates);
            if (successor == nullptr) {
                successor = new Node(newCoordinates, current);
                successor->G = totalCost;
                successor->H = heuristic(successor->coordinates, target_);
                openSet.push_back(successor);
				std::push_heap(openSet.begin(), openSet.end(), cmp);

            }
            else if (totalCost < successor->G) {
                successor->parent = current;
                successor->G = totalCost;
            }
        }
    }

    CoordinateList path;
    while (current != nullptr) {
        path.push_back(current->coordinates);
        current = current->parent;
    }

    releaseNodes(openSet);
    releaseNodes(closedSet);

    return path;
}

/*
计算添加坡度的代价函数
*/
AStar::uint AStar::Generator::cost(Vec2i begin_, Vec2i end_, int alpha, float angle)
{
	auto dis = heuristic(end_, begin_);

	auto h = abs(begin_.z - end_.z);
	auto side = 10 * sqrt(pow((begin_.x - end_.x), 2) + pow((begin_.y - end_.y), 2));
	auto res = h / side + 1;
	if (res - 1 < tan(angle)) {
		res = 1;
	}

	return dis * pow(res, alpha);
}

AStar::Node* AStar::Generator::findNodeOnList(NodeSet& nodes_, Vec2i coordinates_)
{
    for (auto node : nodes_) {
        if (node->coordinates == coordinates_) {
            return node;
        }
    }
    return nullptr;
}

void AStar::Generator::releaseNodes(NodeSet& nodes_)
{
    for (auto it = nodes_.begin(); it != nodes_.end();) {
        delete *it;
        it = nodes_.erase(it);
    }
}

/*
	coordinates_.x < 0 || coordinates_.x >= worldSize.x ||
    coordinates_.y < 0 || coordinates_.y >= worldSize.y ||
    判断边界时仅使用障碍判断，即将边界也设置为障碍
*/
bool AStar::Generator::detectCollision(Vec2i coordinates_)
{
    if (std::find(walls.begin(), walls.end(), coordinates_) != walls.end()) {	
        return true;
    }
    return false;
}

//AStar::Node * AStar::Generator::findNodeOnList(NodeSet & nodes_, Vec2i coordinates_)
//{
//	return nullptr;
//}

AStar::Vec2i AStar::Heuristic::getDelta(Vec2i source_, Vec2i target_)
{
    return{ abs(source_.x - target_.x),  abs(source_.y - target_.y),  abs(source_.z - target_.z) };
}

AStar::uint AStar::Heuristic::manhattan(Vec2i source_, Vec2i target_)
{
    auto delta = std::move(getDelta(source_, target_));
    return static_cast<uint>(10 * (delta.x + delta.y));
}

AStar::uint AStar::Heuristic::euclidean(Vec2i source_, Vec2i target_)
{
    auto delta = std::move(getDelta(source_, target_));	// move作用，强制转化
    return static_cast<uint>(10 * sqrt(pow(delta.x, 2) + pow(delta.y, 2)));
}

AStar::uint AStar::Heuristic::octagonal(Vec2i source_, Vec2i target_)
{
    auto delta = std::move(getDelta(source_, target_));
    return 10 * (delta.x + delta.y) + (-6) * std::min(delta.x, delta.y);
}
