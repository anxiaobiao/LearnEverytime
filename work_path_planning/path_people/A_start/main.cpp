#include <iostream>
#include<string>

#include "AStar.hpp"
#include <vector>

#define pi 3.14

AStar::CoordinateList run(std::string data_path, std::string barr_path, std::string world_path, std::vector<float> P_start, std::vector<float> P_end)
{
	AStar::CoordinateList data, barr, world;
	AStar::Preprocess preprocess;
	data = preprocess.read_data(data_path);
	barr = preprocess.read_data(barr_path);
	world = preprocess.read_data(world_path);

	auto start = preprocess.match({ P_start[0], P_start[1], P_start[2] }, data);
	auto end = preprocess.match({ P_end[0], P_end[1], P_end[2] }, data);

	AStar::Generator generator(1, 1);	// 栅格的长宽
	generator.setCoordinatesMap(data);
	generator.addCollision(barr);
	generator.addCollision(world);

	generator.setHeuristic(AStar::Heuristic::euclidean);
    generator.setDiagonalMovement(true);

	//std::cout << "Generate path ... \n";
	auto path = generator.findPath(start, end, 10, pi / 18);
	preprocess.save_data("D:/code/path_planning/path_people/txt/path_C.txt", path);

	return path;
}

int main()
{
	//AStar::CoordinateList data, barr, world;
	//AStar::Preprocess preprocess;
	//data = preprocess.read_data("D:/code/path_planning/path_people/txt/data.txt");
	//barr = preprocess.read_data("D:/code/path_planning/path_people/txt/barrier.txt");
	//world = preprocess.read_data("D:/code/path_planning/path_people/txt/world.txt");

	//auto start = preprocess.match({ -147.096855443276, 194.314711895158, 1.01719104920375 }, data);
	//auto end = preprocess.match({ 90.8449160806757, - 128.119323623137, 2.32741954230797 }, data);
	////std::cout << "start:" << start.x << ", " << start.y << ", " << start.z << std::endl;
	////std::cout << "end:" << end.x << ", " << end.y << ", " << end.z << std::endl;
	////save_data("D:/code/path_planning/path_people/txt/path_C.txt", world);

	//AStar::Generator generator(1, 1);	// 栅格的长宽
 //   //generator.setWorldSize({25.6, 25.4, 0.5});	// 不需要设置边界，将边界设置为障碍
	//generator.setCoordinatesMap(data);
	//generator.addCollision(barr);
	//generator.addCollision(world);

 //   generator.setHeuristic(AStar::Heuristic::euclidean);
 //   generator.setDiagonalMovement(true);

 //   std::cout << "Generate path ... \n";
 //   //auto path = generator.findPath({0.4, 0.2, 0.3}, {20.4, 20.2, 0.3}, 10, pi/4);
	////auto path = generator.findPath({ -93.50000, 182.50000, 3.60209 }, { 31.50000, - 70.50000,	 2.84070 }, 10, pi / 18);
	//auto path = generator.findPath(start, end, 10, pi / 18);

	//preprocess.save_data("D:/code/path_planning/path_people/txt/path_C.txt", path);
 //   /*for(auto& coordinate : path) {
 //       std::cout << coordinate.x << " " << coordinate.y << "\n";
 //   }*/

	std::string data_path, barr_path, world_path;
	data_path = "D:/code/path_planning/path_people/optimize/data.txt";
	barr_path = "D:/code/path_planning/path_people/optimize/barr.txt";
	world_path = "D:/code/path_planning/path_people/optimize/world.txt";

	std::vector<float> P_start, P_end;
	P_start = { -139.5, -99.5, 0.0891 };
	P_end = { 278.5, 344.5 ,3.269 };

	AStar::CoordinateList path = run(data_path, barr_path, world_path, P_start, P_end);
	for (auto it : path) {
		std::cout << it.x << " " << it.y << " " << it.z << std::endl;
	}
}


