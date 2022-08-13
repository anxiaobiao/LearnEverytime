#include <iostream>
#include<string>
#include<fstream>
#include "AStar.hpp"

#define pi 3.14

AStar::CoordinateList read_data(std::string str_Path)
{
	std::ifstream infile;
	infile.open(str_Path);
	AStar::CoordinateList data;
	if (!infile)
	{
		std::cout << "error" << std::endl;
		system("pause");
		return data;
	}
	std::string str;
	double t1, t2, t3, t4, t5;
	AStar::Vec2i Pt;
	while (infile >> t1 >> t2 >> t3)	//按空格读取，遇到空白符结束
	{
		Pt.x = t1;
		Pt.y = t2;
		Pt.z = t3;
		data.push_back(Pt);
		//std::cout << Pt.x << " " << Pt.y << " " << Pt.z << std::endl;
	}
	std::cout << "读取文件结束！" << std::endl;
	return data;
}

void save_data(std::string str_Path, AStar::CoordinateList data)
{
	std::ofstream outFile;
	//打开文件
	outFile.open(str_Path);
	auto begin = data.begin();
	auto end = data.end();
	while (begin != end)
	{
		//float arr[3] = { begin->x, begin->y ,begin->z };
		outFile << begin->x << ' ' << begin->y << ' ' << begin->z << std::endl;
		++begin;
	}
	std::cout << "写入成功" << std::endl;
	//关闭文件
	outFile.close();
}

int main()
{
	AStar::CoordinateList data, barr, world;
	data = read_data("D:/code/path_planning/path_people/txt/data.txt");
	barr = read_data("D:/code/path_planning/path_people/txt/barrier.txt");
	world = read_data("D:/code/path_planning/path_people/txt/world.txt");

	//save_data("D:/code/path_planning/path_people/txt/path_C.txt", world);

	AStar::Generator generator(1, 1);	// 栅格的长宽
    //generator.setWorldSize({25.6, 25.4, 0.5});	// 不需要设置边界，将边界设置为障碍
	generator.setCoordinatesMap(data);
	generator.addCollision(barr);
	generator.addCollision(world);

    generator.setHeuristic(AStar::Heuristic::euclidean);
    generator.setDiagonalMovement(false);

    std::cout << "Generate path ... \n";
    //auto path = generator.findPath({0.4, 0.2, 0.3}, {20.4, 20.2, 0.3}, 10, pi/4);
	auto path = generator.findPath({ -93.3827136397538,182.482189169476,3.34697756390315 }, { 31.3021007271463,-70.8673974811307,2.75040293291228 }, 10, pi / 18);

	save_data("D:/code/path_planning/path_people/txt/path_C.txt", path);
    /*for(auto& coordinate : path) {
        std::cout << coordinate.x << " " << coordinate.y << "\n";
    }*/
}

