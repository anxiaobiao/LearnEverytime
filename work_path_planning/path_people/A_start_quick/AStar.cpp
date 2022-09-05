#include "AStar.hpp"
#include "ThreadPool.h"
#include <algorithm>
#include <math.h>
#include <iostream>
#include <sstream>
#include <fstream>
#include <stdlib.h>
#include <limits.h>

using namespace std::placeholders;

bool AStar::Vec2i::operator == (const Vec2i& coordinates_)
{
    return (x == coordinates_.x && y == coordinates_.y);
}

AStar::Vec2i operator + (const AStar::Vec2i& left_, const AStar::Vec2i& right_)
{
    return{ left_.x + right_.x, left_.y + right_.y }; // 修改为二维
}

AStar::Node::Node(Vec2i coordinates_, Node *parent_)
{
    parent = parent_;
    coordinates = coordinates_;
    G = H = 0;
}

AStar::uint AStar::Node::getScore()
{
    return G + H;
}

AStar::Generator::Generator()
{
    setDiagonalMovement(false);
    setHeuristic(&Heuristic::manhattan);
    direction = {
        { 0, 1 }, { 1, 0 }, { 0, -1 }, { -1, 0 },
        { -1, -1 }, { 1, 1 }, { -1, 1 }, { 1, -1 }
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
    heuristic = std::bind(heuristic_, _1, _2);
}

// 将数据导入类中
void AStar::Generator::setSolpe(SolpeSet solpe_)
{
	solpe = solpe_;
}

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
	//std::cout << "设置障碍成功" << std::endl;
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

AStar::CoordinateList AStar::Generator::findPath(Vec2i source_, Vec2i target_, Vec2i upper_left_, Vec2i lower_right_, int alpha)
{
	std::cout << "worker thread ID:" << std::this_thread::get_id() << std::endl;

	if (detectCollision(source_, upper_left_, lower_right_) || detectCollision(target_, upper_left_, lower_right_)){
		std::cout << "起点或终点在障碍中！！！" << std::endl;
		exit(0);
	}
    Node *current = nullptr;
    NodeSet openSet, closedSet;
    openSet.reserve(100);
    closedSet.reserve(100);
    openSet.push_back(new Node(source_));

	auto cmp = [](Node* x, Node* y) { return x->getScore() > y->getScore(); };
	std::make_heap(openSet.begin(), openSet.end(), cmp);

	int abc = 1;
    while (!openSet.empty()) {
		if (abc % 50000 == 1) {
			std::cout << abc << std::endl;
		}
		abc++;
		current = openSet.front();

        if (current->coordinates == target_) {
            break;
        }

        closedSet.push_back(current);
		std::pop_heap(openSet.begin(), openSet.end(), cmp);
		openSet.pop_back();

        for (uint i = 0; i < directions; ++i) {
            Vec2i newCoordinates(current->coordinates + direction[i]);
			uint y = newCoordinates.x - upper_left_.x;	// 获得相对solpe的索引
			uint x = upper_left_.y - newCoordinates.y;

			if ((solpe[x][y] >= 200 && solpe[x][y] <= 255) || findNodeOnList(closedSet, newCoordinates)) {	// solpe为200的为障碍，为255的为边界
				continue;
			}
			
            uint totalCost = current->G + (int)(((i < 4) ? 10 : 14) * pow((float)((solpe[x][y])/100+1), alpha) * 100); // 仅根据solpe得到其坡度。G和H需要时一个量级，所以所了乘除操作
			//uint totalCost = current->G + ((i < 4) ? 10 : 14) * solpe[x][y];

            Node *successor = findNodeOnList(openSet, newCoordinates);
            if (successor == nullptr) {
                successor = new Node(newCoordinates, current);
                successor->G = totalCost;
                successor->H = heuristic(successor->coordinates, target_) * 100;	// 需要G和H处于一个量级
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
	Node *backtrack;
	if (findNodeOnList(closedSet, target_) != nullptr) {
		backtrack = current;
	}
	else {
		backtrack = findNodeRecentList(closedSet, target_); // 可以在没有路径时强制结束并输出
		//std::cout << "没有路径，停止程序" << std::endl;
		//exit(0);   // 程序非正常退出
	}
	while (backtrack != nullptr) {
		path.push_back(backtrack->coordinates);
		backtrack = backtrack->parent;
	}

	releaseNodes(openSet);
	releaseNodes(closedSet);

	//all_path.push_back(path);
	/*AStar::Preprocess preprocess;
	std::string pwd = "D:/code/path_planning/path_people/data/matlab/path";
	pwd += std::to_string(num);
	pwd += ".txt";
	preprocess.save_data(pwd, path);
	std::cout << pwd << " 保存成功！" << std::endl;*/

	return path;
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

// 寻找最近节点
AStar::Node* AStar::Generator::findNodeRecentList(NodeSet& nodes_, Vec2i coordinates_)
{
	AStar::Heuristic heurustic;
	Node* ans = nodes_[0];
	float dis = heurustic.euclidean(ans->coordinates, coordinates_);
	for (auto node : nodes_) {
		if (heurustic.euclidean(node->coordinates, coordinates_) < dis) {
			ans = node;
			dis = heurustic.euclidean(node->coordinates, coordinates_);
		}
	}
	return ans;
}

void AStar::Generator::releaseNodes(NodeSet& nodes_)
{
    for (auto it = nodes_.begin(); it != nodes_.end();) {
        delete *it;
        it = nodes_.erase(it);
    }
}

bool AStar::Generator::detectCollision(Vec2i coordinates_, Vec2i upper_left_, Vec2i lower_right_)	// 判断障碍仅需要判断索引处于是否等于200/255
{
	uint y = coordinates_.x - upper_left_.x;
	uint x = upper_left_.y - coordinates_.y;

	return (solpe[x][y] >= 200 && solpe[x][y] <= 255);
}

AStar::Vec2i AStar::Heuristic::getDelta(Vec2i source_, Vec2i target_)
{
    return{ abs(source_.x - target_.x),  abs(source_.y - target_.y) };
}

AStar::uint AStar::Heuristic::manhattan(Vec2i source_, Vec2i target_)
{
    auto delta = std::move(getDelta(source_, target_));
    return static_cast<uint>(10 * (delta.x + delta.y));
}

AStar::uint AStar::Heuristic::euclidean(Vec2i source_, Vec2i target_)
{
    auto delta = std::move(getDelta(source_, target_));
    return static_cast<uint>(10 * sqrt(pow(delta.x, 2) + pow(delta.y, 2)));
}

AStar::uint AStar::Heuristic::octagonal(Vec2i source_, Vec2i target_)
{
    auto delta = std::move(getDelta(source_, target_));
    return 10 * (delta.x + delta.y) + (-6) * std::min(delta.x, delta.y);
}

AStar::SolpeSet AStar::Preprocess::read_data(std::string str_Path)	
{
	std::ifstream myfile(str_Path);
	std::string temp;
	AStar::SolpeSet result;
	std::vector<AStar::uint> res;
	if (!myfile)
	{
		std::cout << "error" << std::endl;
		system("pause");
		return result;
	}
	while (std::getline(myfile, temp))
	{
		std::stringstream input(temp);
		AStar::uint out;
		while (input >> out) {	// 读取文件选用了逐字读取，生成二维vector
			res.push_back(out);
		}
		result.push_back(res);
		res.clear();
	}
	/*for (int i = 0; i < result.size(); i++) {
		for (int j = 0; j < result[i].size(); j++) {
			std::cout << result[i][j] << " ";
			if (j == result[i].size() - 1) std::cout << std::endl;
		}
	}*/
	return result;
}

void AStar::Preprocess::save_data(std::string str_Path, AStar::CoordinateList data)
{
	std::ofstream outFile;
	//打开文件
	outFile.open(str_Path);
	auto begin = data.begin();
	auto end = data.end();
	while (begin != end)
	{
		//float arr[3] = { begin->x, begin->y ,begin->z };
		outFile << begin->x << ' ' << begin->y << std::endl;
		++begin;
	}
	//std::cout << "写入成功" << std::endl;
	//关闭文件
	outFile.close();
}

void AStar::Preprocess::save_data(std::string str_Path, std::vector<AStar::CoordinateList> data)
{
	std::ofstream outFile;
	//打开文件
	outFile.open(str_Path);

	for (int i = 0; i < data.size(); ++i) {
		auto begin = data[i].begin();
			auto end = data[i].end();
			while (begin != end)
			{
				//float arr[3] = { begin->x, begin->y ,begin->z };
				outFile << begin->x << ' ' << begin->y << std::endl;
				++begin;
			}
	}

	
	//std::cout << "写入成功" << std::endl;
	//关闭文件
	outFile.close();
}

AStar::Vec2i AStar::Preprocess::match(std::vector<float> point, int side_x, int side_y)
{
	AStar::Vec2i res;
	res.x = (int)point[0] + side_x;	// 匹配问题，由于相邻点距离为1，所以只需强制转型为int即可
	res.y = (int)point[1] + side_x;
	return res;
}

AStar::CoordinateList AStar::GeneratorAdapter::operator()(Vec2i source_, Vec2i target_, Vec2i upper_left_, Vec2i lower_right_, int alpha)
{
	return t->findPath(source_, target_, upper_left_, lower_right_, alpha);
}
