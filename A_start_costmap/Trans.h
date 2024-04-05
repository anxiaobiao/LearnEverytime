#pragma once
#include<vector>
#include<cmath>
#define M_PI 3.14159265358979323846

namespace Trans {

	// 定义经纬度结构体
	struct Point_GPS
	{
		double lon, lat;
	};

	// 定义图坐标结构体
	struct Point_XY
	{
		int x, y;
	};

	using List_GPS = std::vector<double>;
	using temp = std::vector<Point_XY>;
	using temp_gps = std::vector<Point_GPS>;


	class Trans {
	public:
		Trans(double* mercator_, int weight_, int hight_);			// 初始化：tiff的表头，6个值。tiff的大小：高宽。weight：宽（有几列）；hight：高（有几行）
		Point_GPS XY_GPS(int x, int y); // 图坐标转经纬度坐标
		Point_GPS XY_GPS(float x, float y); // 图坐标转经纬度坐标(重载)
		void all_GPS();// 求取tiff文件的经纬度索引坐标,
		Point_XY match(float lat, float lon);	// 匹配，即经纬度转图坐标，使用匹配的方法

	public:
		double mercator[6];	// 表头
		List_GPS all_lon;	// 经度的所有结果，90左右（测试用），列
		List_GPS all_lat;	// 纬度的所有结果，27左右（测试用），行
		bool all_flag = false;	// 是否得到全部经纬度结果，默认是否
		int weight;			// weight：宽（有几列）
		int hight;			// hight：高（有几行）

	};
}