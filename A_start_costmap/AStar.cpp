#include "AStar.h"
#include <algorithm>
#include <math.h>
#include <iostream>
#include <sstream>
#include <fstream>
#include <stdlib.h>
#include <limits.h>
#include <map>
#include <unordered_map>

using namespace std::placeholders;

AStar::Node::Node(const Point& coord_, uint _g, uint _h) {
	coordinates = coord_;
	G = _g;
	H = _h;
}

bool AStar::Vec2i::operator == (const Vec2i& coordinates_) const
{
	return (x == coordinates_.x && y == coordinates_.y);
}

AStar::Vec2i operator + (const AStar::Vec2i& left_, const AStar::Vec2i& right_)
{
	return{ left_.x + right_.x, left_.y + right_.y }; // 修改为二维
}

AStar::Node::Node(Vec2i coordinates_)
{
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



void AStar::Generator::setDiagonalMovement(bool enable_)
{
	directions = (enable_ ? 8 : 4);
}

void AStar::Generator::setHeuristic(HeuristicFunction heuristic_)
{
	heuristic = std::bind(heuristic_, _1, _2);
}


AStar::CoordinateList AStar::Worker::findPathByPriority(const Point& _source, const Point& target_, const Point& upper_left_, const Point& lower_right_, int alpha, Generator& generator, std::vector<std::vector<unsigned char>>& road_weight)
{

	//std::cout << angle << std::endl;
	if (generator.detectCollision(_source, upper_left_, lower_right_)) {
		std::cout << "起点或终点在障碍中！！！" << std::endl;
		return {};
	}


	priorityNodeSet openSet; // 没有遍历的结点	
	std::unordered_map<Point, Point, hash_function> cameFrom; // child -> parent;
	std::unordered_map<Point, uint, hash_function> costSoFar; // 相当于 closedSet 已经遍历 的结点


	openSet.push(std::move(Node(_source, 0, 0)));

	std::cout << _source.x << " - " << _source.y << std::endl;

	//建立最小堆
	while (!openSet.empty()) {
		Node current = openSet.top();
		openSet.pop();
		if (current.coordinates == target_) {

			break;
		}

		for (size_t i = 0; i < generator.getDirections(); ++i) {
			Point newCoordinates(current.coordinates + generator.getDirection()[i]);	// 引入数据坐标
			uint y = newCoordinates.x - upper_left_.x;	// 获得相对solpe的索引
			uint x = upper_left_.y - newCoordinates.y;


			// 判断边界
			if ((x <= 0 || y <= 0) || x >= (upper_left_.y - lower_right_.y) || y >= (lower_right_.x - upper_left_.x)) {
				continue;
			}

			if ((250 == generator.getSolpe()[x][y] || 255 == generator.getSolpe()[x][y])) {	// solpe为200的为障碍，为255的为边界
				continue;
			}
			uint g_cost = 0;
			uint newCost = 0;
			uint h_cost = 0;
			g_cost = current.G + road_weight[x][y] * (uint)(((i < 4) ? 10 : 14) * pow((double)((generator.getSolpe()[x][y]) / 100 + 1), alpha) * 100);
			// 新代价
			h_cost = generator.getHeuristic()(newCoordinates, target_) * 100;
			// std::cout << std::sqrt(std::sqrt(h_cost)) << std::endl;
			h_cost = uint(std::sqrt(std::sqrt(h_cost)) * h_cost);

			newCost = g_cost + h_cost;
			// || (newCost < costSoFar[newCoordinates])
			if ((costSoFar.find(newCoordinates) == costSoFar.end())) {
				costSoFar[newCoordinates] = newCost;
				cameFrom[newCoordinates] = current.coordinates;

				openSet.push(Node(newCoordinates, g_cost, h_cost));
			}
		}
	}

	if (openSet.empty() || (costSoFar.find(target_) == costSoFar.end())) {
		return {};
	}

	CoordinateList path;
	Point backtrack = target_;

	while (!(backtrack == _source))
	{
		//std::cout << backtrack.x << " - " << backtrack.y << std::endl;
		path.push_back(backtrack);
		backtrack = cameFrom[backtrack];

	}
	path.push_back(backtrack);
	return path;
}

void AStar::Worker::findPathFromStart(const Point& _source, const Point& target_, int alpha, CoordinateList& path, const Point& upper_left_, const Point& lower_right_, Generator& generator, std::vector<std::vector<unsigned char>>& road_weight)
{

	//std::cout << angle << std::endl;
	if (generator.detectCollision(_source, upper_left_, lower_right_)) {

		// std::cout << "起点或终点在障碍中！！！" << std::endl;
		myTex.lock();
		unreachable = true;
		myTex.unlock();
		return;
	}

	priorityNodeSet openSet; // 没有遍历的结点	
	std::unordered_map<Point, Point, hash_function> cameFrom; // child -> parent;
	std::unordered_map<Point, uint, hash_function> costSoFar; // 相当于 closedSet 已经遍历 的结点

	openSet.push(std::move(Node(_source, 0, 0)));

	//建立最小堆
	while (!openSet.empty()) {
		Node current = openSet.top();
		openSet.pop();


		myTex.lock();
		if (unreachable) {
			myTex.unlock();
			return;
		}
		myTex.unlock();

		myTex.lock();
		auto it = dend_cost.find(current.coordinates);
		myTex.unlock();
		if (it != dend_cost.end()) {
			myTex.lock();
			endFind = true;
			endTarge = current.coordinates;
			myTex.unlock();
			break;
		}

		for (size_t i = 0; i < generator.getDirections(); ++i) {
			Point newCoordinates(current.coordinates + generator.getDirection()[i]);	// 引入数据坐标
			uint y = newCoordinates.x - upper_left_.x;	// 获得相对solpe的索引
			uint x = upper_left_.y - newCoordinates.y;

			// 判断边界  待修改
			if ((x <= 0 || y <= 0) || x >= (upper_left_.y - lower_right_.y) || y >= (lower_right_.x - upper_left_.x)) {
				continue;
			}

			if ((BAR == generator.getSolpe()[x][y] || BOUNDARY == generator.getSolpe()[x][y])) {	// solpe为250的为障碍，为255的为边界
				continue;
			}
			uint g_cost = 0;
			uint newCost = 0;
			uint h_cost = 0;

			g_cost = current.G + (road_weight[x][y]) * (uint)(((i < 4) ? 10 : 14) * pow((double)((generator.getSolpe()[x][y]) / 100 + 1), alpha) * 100);
			// 新代价  可能需要修改，另外，需衡量h_cost的影响
			h_cost = generator.getHeuristic()(newCoordinates, target_) * 100;
			// h_cost = uint(std::sqrt(std::sqrt(h_cost)) * h_cost);
			newCost = g_cost + h_cost;
			//  || 
			if ((costSoFar.find(newCoordinates) == costSoFar.end())) {
				costSoFar[newCoordinates] = newCost;
				cameFrom[newCoordinates] = current.coordinates;
				openSet.push(Node(newCoordinates, g_cost, h_cost));
			}
			/*else if ((newCost < costSoFar[newCoordinates])) {

				if (!(cameFrom[current.coordinates] == newCoordinates)) {
					cameFrom[newCoordinates] = current.coordinates;
					costSoFar[newCoordinates] = newCost;
				}
			}*/
		}
	}

	if (openSet.empty()) {
		myTex.lock();
		unreachable = true;
		myTex.unlock();
		return;
	}

	Point backtrack = endTarge;

	while (!(backtrack == _source))
	{
		path.push_back(backtrack);
		backtrack = cameFrom[backtrack];
		// std::cout << backtrack.x << " - " << backtrack.y << " - " << costSoFar[backtrack] << std::endl; 

	}
	path.push_back(backtrack);
}

void AStar::Worker::findPathFromEnd(const Point& _source, const Point& target_, int alpha, CoordinateList& path, const Point& upper_left_, const Point& lower_right_, Generator& generator, std::vector<std::vector<unsigned char>>& road_weight)
{

	if (generator.detectCollision(_source, upper_left_, lower_right_)) {
		// std::cout << "起点或终点在障碍中！！！" << std::endl;
		myTex.lock();
		unreachable = true;
		myTex.unlock();
		return;
	}

	priorityNodeSet openSet; // 没有遍历的结点	
	std::unordered_map<Point, Point, hash_function> cameFrom; // child -> parent;
	// 	std::unordered_map<Point, double, hash_function> costSoFar; // 相当于 closedSet 已经遍历 的结点

	openSet.push(std::move(Node(_source, 0, 0)));

	//建立最小堆
	while (!openSet.empty()) {
		Node current = openSet.top();
		openSet.pop();


		myTex.lock();
		if (unreachable) {
			myTex.unlock();
			return;
		}
		myTex.unlock();


		myTex.lock();
		if (endFind) {
			myTex.unlock();
			break;
		}
		myTex.unlock();

		for (size_t i = 0; i < generator.getDirections(); ++i) {
			Point newCoordinates(current.coordinates + generator.getDirection()[i]);	// 引入数据坐标
			uint y = newCoordinates.x - upper_left_.x;	// 获得相对solpe的索引
			uint x = upper_left_.y - newCoordinates.y;

			// 判断边界 待修改
			if ((x <= 0 || y <= 0) || x >= (upper_left_.y - lower_right_.y) || y >= (lower_right_.x - upper_left_.x)) {
				continue;
			}

			if ((BAR == generator.getSolpe()[x][y] || BOUNDARY == generator.getSolpe()[x][y])) {	// solpe为 250的为障碍，为255的为边界
				continue;
			}

			uint g_cost = 0;
			uint newCost = 0;
			uint h_cost = 0;

			g_cost = current.G + (road_weight[x][y]) * (uint)(((i < 4) ? 10 : 14) * pow((double)((generator.getSolpe()[x][y]) / 100 + 1), alpha) * 100);
			// 新代价  可能需要修改
			h_cost = generator.getHeuristic()(newCoordinates, target_) * 100;
			// std::cout << std::sqrt(std::sqrt(h_cost)) << std::endl;
			// h_cost = uint(std::sqrt(std::sqrt(h_cost)) * h_cost);

			newCost = g_cost + h_cost;

			if ((dend_cost.find(newCoordinates) == dend_cost.end())) {
				myTex.lock();
				dend_cost[newCoordinates] = newCost;
				myTex.unlock();

				cameFrom[newCoordinates] = current.coordinates;
				openSet.push(Node(newCoordinates, g_cost, h_cost));
			}
			/*else if ((newCost < dend_cost[newCoordinates])) {

				if (!(cameFrom[current.coordinates] == newCoordinates)) {
					dend_cost[newCoordinates] = newCost;
					cameFrom[newCoordinates] = current.coordinates;
				}
			}*/
		}
	}

	if (openSet.empty()) {
		myTex.lock();
		unreachable = true;
		myTex.unlock();
		return;
	}

	Point backtrack = endTarge;

	while (!(backtrack == _source))
	{
		path.push_back(backtrack);
		backtrack = cameFrom[backtrack];
	}
	path.push_back(backtrack);
}

bool AStar::Generator::detectCollision(Vec2i coordinates_, Vec2i upper_left_, Vec2i lower_right_)	// 判断障碍仅需要判断索引处于是否等于200/255
{
	uint y = coordinates_.x - upper_left_.x;
	uint x = upper_left_.y - coordinates_.y;

	return (solpe[x][y] >= 250 && solpe[x][y] <= 255);
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

AStar::SolpeSet AStar::Preprocess::read_data(const std::string& str_Path)
{
	std::ifstream myfile(str_Path);
	std::string temp;
	AStar::SolpeSet result;
	std::vector<AStar::byte> res;
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
	return result;
}

void AStar::Preprocess::read_data_(AStar::Generator& generator, std::vector<std::vector<unsigned char>> res) {
	for (int i = 0; i < res.size(); ++i) {
		generator.solpe.push_back(res[i]);
	}
}

void AStar::Preprocess::read_data_(AStar::Generator& generator, cv::Mat res) {
	std::vector<AStar::byte> row_data;
	for (int i = 0; i < res.rows; ++i)
	{
		for (int j = 0; j < res.cols; ++j) {
			row_data.push_back(res.at<uchar>(i, j));
		}
		generator.solpe.push_back(row_data);
		row_data.clear();
	}
}

void AStar::Preprocess::read_data_(AStar::Generator& generator, nc::NdArray<float> res) {
	nc::Shape res_size = res.shape();
	std::vector<AStar::byte> row_data;
	for (int i = 0; i < res_size.rows; ++i)
	{
		for (int j = 0; j < res_size.cols; ++j) {
			row_data.push_back(res(i, j));
		}
		generator.solpe.push_back(row_data);
		row_data.clear();
	}
}

void AStar::Preprocess::read_data_dire(AStar::Generator& generator, const std::string& dataFilename) {
	std::ifstream myfile(dataFilename);
	std::string temp;
	std::vector<AStar::byte> res;
	if (!myfile)
	{
		std::cout << "文件错误" << std::endl;
		system("pause");
		exit(-1);
	}
	while (std::getline(myfile, temp))
	{
		std::stringstream input(temp);
		AStar::uint out;
		while (input >> out) {	// 读取文件选用了逐字读取，生成二维vector
			res.push_back(out);
		}
		generator.solpe.push_back(res);
		res.clear();
	}
}

void AStar::Preprocess::save_data(const std::string& str_Path, const AStar::CoordinateList& data)
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

AStar::Vec2i AStar::Preprocess::match(const std::vector<double>& point, int side_x, int side_y)
{
	AStar::Vec2i res;
	res.x = (uint)point[0] + side_x;	// 匹配问题，由于相邻点距离为1，所以只需强制转型为int即可
	res.y = (uint)point[1] + side_x;
	return res;
}