#pragma once

#include "AStar.h"
#include "Check.h"

typedef unsigned char byte;


#ifdef __linux__ 	//Linux platform
#define PATH_C	extern
#elif _WIN64
#ifndef PATH_C	//如果没有定义DLLH 就定义 DLLH __declspec(dllexport)
#define PATH_C __declspec(dllimport)	//导出
#else
#define PATH_C __declspec(dllexport)//导入
#endif // DLLH__//如果没有定义DLLH 就定义 DLLH
#endif

namespace jna_path {
	struct Point {
		double x, y;
	};

	struct Line
	{
		Point start;
		Point end;
	};

	struct Result
	{
		/* data */
		Point* path = nullptr;
		int* sizePerLine = nullptr;
		int pathSize = 0;
		int sizePerLineSize = 0;
	};

	struct Args {
		float max_slope = 60.0f;
		float object_width = 3.3;
		float object_length = 7.2;
		float meter_per_pixel = 0.5;
		float threshold = 0.05;
	};

	static AStar::Vec2i upper_left;	// solpe表的左上角点
	static AStar::Vec2i lower_right; // solpe表的右下角点

	static Point upper_left_latlng;
	static Point lower_right_latlng;

	// static AStar::Preprocess preprocess;
	// static AStar::Generator generator;

	// static Transform transform;

	static Coordinate lat;
	static Coordinate lon;

}




#ifdef __cplusplus
extern "C" {
#endif
	PATH_C jna_path::Result* getPathFromMem(byte* accessibleRoadMap, int accessibleRoadMapLength, byte* weightedMap, int weightedMapLength, jna_path::Args* args, jna_path::Point startPoint, jna_path::Point endPoint, int* errcode, byte* DEMTiffData, int DEMDataSize);
	PATH_C void* GetStream(const char* pszFile, int& nSize);

#ifdef __cplusplus
}
#endif