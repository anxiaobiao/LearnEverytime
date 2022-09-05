#include <iostream>
#include <sstream>
#include <fstream>
#include<vector>
#include<cstdlib>
#include<ctime>

#include "source/AStar.hpp"
#include "source/ThreadPool.h"

AStar::CoordinateList run(AStar::SolpeSet data, std::vector<float> P_start, std::vector<float> P_end, AStar::Vec2i upper_left, AStar::Vec2i lower_right, int side_x, int side_y, int alpha)
{
	AStar::Preprocess preprocess;

	//AStar::SolpeSet data;
	//data = preprocess.read_data(data_path);
	//int side[] = { lower_right.x - upper_left.x, upper_left.y - lower_right.y };

	AStar::Generator generator;
	generator.setSolpe(data);
	generator.setHeuristic(AStar::Heuristic::euclidean);
	generator.setDiagonalMovement(true);

	AStar::Vec2i start = preprocess.match({ P_start[0], P_start[1] }, side_x, side_y);
	AStar::Vec2i end = preprocess.match({ P_end[0], P_end[1] }, side_x, side_y);

	std::cout << "Generate path ... \n";
	clock_t start_t = clock();
	auto path = generator.findPath(start, end, upper_left, lower_right, alpha);
	clock_t end_t = clock();
	std::cout << "time = " << double(end_t - start_t) / CLOCKS_PER_SEC << "s" << std::endl;

	preprocess.save_data("D:/code/path_planning/path_people/data/path.txt", path);
	preprocess.save_data("D:/code/path_planning/path_people/data/matlab/path.txt", path);

	return path;
}

void run(AStar::SolpeSet data, std::vector<float> P_start, std::vector <std::vector<float>> P_end, AStar::Vec2i upper_left, AStar::Vec2i lower_right, int side_x, int side_y, int alpha)
{
	AStar::Preprocess preprocess;

	// 建立线程池
	ThreadPool pool(4);

	//AStar::SolpeSet data;
	//data = preprocess.read_data(data_path);
	//int side[] = { lower_right.x - upper_left.x, upper_left.y - lower_right.y };

	AStar::Generator generator;
	generator.setSolpe(data);
	generator.setHeuristic(AStar::Heuristic::euclidean);
	generator.setDiagonalMovement(true);

	AStar::Vec2i start = preprocess.match({ P_start[0], P_start[1] }, side_x, side_y);
	std::vector<AStar::Vec2i> end;
	for (int i = 0; i < P_end.size(); ++i) {
		end.push_back(preprocess.match({ P_end[i][0], P_end[i][1] }, side_x, side_y));
	}
	 

	std::cout << "Generate path ... \n";
	std::vector<AStar::CoordinateList> all_path;

	AStar::GeneratorAdapter ad(&generator);
	clock_t start_t = clock();

	std::vector<std::future<AStar::CoordinateList>> path;
	for (int i = 0; i < end.size(); ++i) {
		path.push_back(pool.enqueue(ad, start, end[i], upper_left, lower_right, alpha));
		//auto path = generator.findPath(start, end[i], upper_left, lower_right, alpha);
	}
	for (int i = 0; i < end.size(); ++i) {
		auto a = path[i].get();
		all_path.push_back(a);

	}
	clock_t end_t = clock();
	std::cout << "time = " << double(end_t - start_t) / CLOCKS_PER_SEC << "s" << std::endl;

	//preprocess.save_data("D:/code/path_planning/path_people/data/path3.txt", path);
	//preprocess.save_data("D:/code/path_planning/path_people/data/matlab/path3.txt", a);
	preprocess.save_data("D:/code/path_planning/path_people/data/matlab/path.txt", all_path);

	//return path;
}

int main()
{
	AStar::Preprocess preprocess;

	std::string data_path = "D:/code/path_planning/path_people/data/second.txt";
	AStar::SolpeSet data = preprocess.read_data(data_path);

	AStar::Vec2i upper_left = { 41, 408 };	// solpe表的左上角点
	AStar::Vec2i lower_right = { 302, 66 }; // solpe表的右下角点

	std::vector<float> P_start, P_end;
	P_start = { -147.096855443276, 194.314711895158 };
	P_end = { 90.8449160806757, -128.119323623137 };

	// 多目标
	std::vector <std::vector<float>> P_end_more;
	P_end_more = { { 90.8449160806757, -128.119323623137 }, { 29.3143527800825, 142.818729571630 }, {96.3692199856346, 30.8683783945616} };

	int side_x, side_y;
	side_x = 200;	// 相对之前的坐标都+200，使得坐标范围都为正数
	side_y = 200;

	int alpha = 10;
	
	//auto path = run(data, P_start, P_end, upper_left, lower_right, side_x, side_y, alpha);
	run(data, P_start, P_end_more, upper_left, lower_right, side_x, side_y, alpha);

    /*for(auto& coordinate : path) {
        std::cout << coordinate.x << " " << coordinate.y << "\n";
    }*/
}