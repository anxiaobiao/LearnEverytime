#include"Check.h"
#include <sstream>
#include <fstream>

Coordinate read_data(std::string str_Path)
{
	std::ifstream infile;
	infile.open(str_Path);
	Coordinate data;
	if (!infile)
	{
		std::cout << "error" << std::endl;
		system("pause");
		return data;
	}

	double t1;
	while (infile >> t1)	//按空格读取，遇到空白符结束
	{
		data.push_back(t1);
		//std::cout << std::setprecision(9) <<t1 << std::endl;
	}
	//std::cout << "读取文件结束！" << std::endl;
	return data;
}