#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <ctime>
#include <thread>
#include <iomanip>
#include <opencv2/core/core.hpp> 
#include <opencv2/highgui/highgui.hpp> 
#include <opencv2/imgproc.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/core.hpp> 
#include <opencv2/highgui/highgui.hpp>
#include <gdal.h>
#include <gdal_utils.h>
#include <gdal_priv.h>
#include <gdalwarper.h>
#include <gdal_alg_priv.h>
#include "Check.h"
#include "AStar.h"
#include "PATH.h"
#include "Trans.h"

using namespace std;
using namespace std::chrono;

#define THREAD 1

int ALPHA = 17;

const int SIZE_X = 0;
const int SIZE_Y = 0;

double clacPathLen(AStar::CoordinateList allPath, std::vector<std::vector<float>> DEMData) {
	double res = 0;
	for (int i = 1; i < allPath.size(); ++i) {
		float z1, z2;
		z1 = DEMData[-allPath[i].y][allPath[i].x];
		z2 = DEMData[-allPath[i - 1].y][allPath[i - 1].x];
		res += sqrt(pow((allPath[i].x - allPath[i - 1].x) * 0.5, 2) + pow((allPath[i].y - allPath[i - 1].y) * 0.5, 2) + pow((z2 - z1), 2));
	}
	return res;
}

void zoom(cv::Mat input, cv::Mat& output, int X, int Y) {
	cout << "input.col:" << input.cols << ' ' << "input.row" << input.rows << endl;
	cout << "output.col:" << output.cols << ' ' << "output.row" << output.rows << endl;
	cout << "X:" << X << ' ' << "Y:" << Y << endl;
	for (int i = 0; i < Y; ++i) {
		for (int j = 0; j < X; ++j) {
			output.at<uchar>(i, j) = input.at<uchar>(i, j);
		}
	}
}

int check_point(AStar::Vec2i upper_left_, AStar::Vec2i lower_right_, int& x_, int& y_, AStar::Generator& generator) {
	uint y = x_ - upper_left_.x;	// 获得相对solpe的索引
	uint x = upper_left_.y - y_;

	if ((BAR == generator.getSolpe()[x][y] || BOUNDARY == generator.getSolpe()[x][y])) {	// solpe为250的为障碍，为255的为边界
		uint x_s, x_e, y_s, y_e;
		x_s = (x - 10) > 0 ? (x - 10) : 0;
		y_s = (y - 10) > 0 ? (y - 10) : 0;
		x_e = (x + 10) < std::abs(lower_right_.y) ? (x + 10) : 0;
		y_e = (y + 10) < std::abs(lower_right_.x) ? (y + 10) : 0;

		for (int i = x_s; i < x_e; ++i) {
			for (int j = y_s; j < y_e; ++j) {
				if ((BAR != generator.getSolpe()[i][j] && BOUNDARY != generator.getSolpe()[i][j])) {
					x_ = j + upper_left_.x;
					y_ = upper_left_.y - i;
					cout << x_ << ' ' << y_ << endl;
					return 0;
				}
			}
		}
		return -1;
	}
	return 0;
}

std::vector<std::vector<byte>> mat2vec2(cv::Mat mat) {
	int rows = mat.rows;
	int cols = mat.cols;
	std::vector<std::vector<byte>> res(rows, std::vector<byte>(cols));
	for (int i = 0; i < rows; i++) {
		for (int j = 0; j < cols; j++) {
			res[i][j] = mat.at<uchar>(i, j);
		}
	}
	return res;
}

void makeResultGeoJson(jna_path::Result* res, std::string filename) {
	std::ofstream ofs;
	ofs.open(filename);
	ofs << "{\"type\":\"FeatureCollection\",\"features\":[{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"LineString\",\"coordinates\":";
	ofs << "[";

	for (int i = 0; i < res->pathSize; ++i) {
		ofs << std::fixed << std::setprecision(8);
		//printf("[%.8f,%.8f]\n", res->path[i].x, res->path[i].y);
		ofs << "[" << res->path[i].x << "," << res->path[i].y << "]";
		if (i != res->pathSize - 1) {
			ofs << ",";
		}
	}
	ofs << "]}}]}";
	ofs.close();
}

void* GetStream(const char* pszFile, int& nSize) {
	FILE* pFile = fopen(pszFile, "rb");

	//fopen_s(&pFile, pszFile, "rb");
	if (!pFile) {
		std::cerr << "open file error" << std::endl;
		exit(-1);
	}
	fseek(pFile, 0, SEEK_END);
	nSize = ftell(pFile);
	fseek(pFile, 0, SEEK_SET);

	char* pBuffer = new char[nSize];
	fread(pBuffer, nSize, 1, pFile);
	fclose(pFile);

	return pBuffer;
}

void run(AStar::Generator& generator, AStar::Preprocess& preprocess, const AStar::Vec2i& start, const AStar::Vec2i& end, const AStar::Vec2i& upper_left, const AStar::Vec2i& lower_right,
	AStar::CoordinateList& allPath, vector<int>& sizePerLin, std::vector<std::vector<unsigned char>>& road_weight)
{

	std::cout << "Generate path single ... \n";
	AStar::Worker w;
	allPath = w.findPathByPriority(start, end, upper_left, lower_right, ALPHA, generator, road_weight);
	//preprocess.save_data("data/path_1.txt", allPath);

	// return path;
}

std::mutex mt;

void runOnThread(AStar::Generator& generator, AStar::Preprocess& preprocess, const AStar::Vec2i& start, const AStar::Vec2i& end, const AStar::Vec2i& upper_left, const AStar::Vec2i& lower_right,
	AStar::CoordinateList& allPath, vector<int>& sizePerLine, std::vector<std::vector<unsigned char>>& road_weight) {
	std::cout << "Generate path double ... \n";

	AStar::CoordinateList fromStart;
	AStar::CoordinateList fromEnd;

	AStar::Worker w;

	std::thread t1(&AStar::Worker::findPathFromStart, &w,
		std::ref(start), std::ref(end), ALPHA, std::ref(fromStart), std::ref(upper_left), std::ref(lower_right), std::ref(generator), std::ref(road_weight));
	std::thread t2(&AStar::Worker::findPathFromEnd, &w,
		std::ref(end), std::ref(start), ALPHA, std::ref(fromEnd), std::ref(upper_left), std::ref(lower_right), std::ref(generator), std::ref(road_weight));
	t1.join();
	t2.join();

	if (fromStart.empty() || fromEnd.empty()) {
		std::lock_guard<std::mutex> a(mt);
		allPath.push_back(start);
		allPath.push_back(end);
		sizePerLine.push_back(2);
		std::cout << "目的地不可达" << std::endl;
		return;
	}

	using namespace AStar;
	AStar::CoordinateList path;
	/*for (auto it = fromStart.rbegin(); it != fromStart.rend()-1; ++it) {
		path.push_back(*it);
	}
	for (const AStar::Point& p : fromEnd) {
		path.push_back(p);
	}*/
	mt.lock();
	for (auto it = fromStart.rbegin(); it != fromStart.rend() - 1; ++it) {
		allPath.push_back(*it);
		// path.push_back(*it);
	}
	for (const AStar::Point& p : fromEnd) {
		allPath.push_back(p);
		// path.push_back(p);
	}
	sizePerLine.push_back(fromStart.size() - 1 + fromEnd.size());
	mt.unlock();
	/*auto begin = path.begin();
	while (begin != path.end())
	{
		allPath.push_back(*begin);
		++begin;
	}*/
}

jna_path::Result* getPathFromMem(byte* accessibleRoadMap, int accessibleRoadMapLength, byte* weightedMap, int weightedMapLength, jna_path::Args* args, jna_path::Point startPoint, jna_path::Point endPoint, int* errcode, byte* DEMTiffData, int DEMDataSize) {
	srand(unsigned(time(0)));
	auto preProcessBegin = system_clock::now();
	GDALAllRegister();//注册所有的驱动
	CPLSetConfigOption("GDAL_FILENAME_IS_UTF8", "NO"); //设置支持中文路径和文件名

	VSIFCloseL(VSIFileFromMemBuffer("/vsimem/gtiff_1", (GByte*)accessibleRoadMap, accessibleRoadMapLength, FALSE));
	VSIFCloseL(VSIFileFromMemBuffer("/vsimem/gtiff_2", (GByte*)weightedMap, weightedMapLength, FALSE));

	GDALDataset* pADataSet = (GDALDataset*)GDALOpen("/vsimem/gtiff_1", GA_ReadOnly);//GA_Update和GA_ReadOnly两种模式
	GDALDataset* pBDataSet = (GDALDataset*)GDALOpen("/vsimem/gtiff_2", GA_ReadOnly);//GA_Update和GA_ReadOnly两种模式

	if (pADataSet == nullptr || pBDataSet == nullptr)
	{
		std::cout << "指定的文件不能打开!" << std::endl;
		return nullptr;
	}

	//#### 加载内存数据 #######
	// 获取仿射变换系数
	// ----------------
	double geotrans[6] = { 0,1,0,0,0,1 };
	CPLErr aaa = pADataSet->GetGeoTransform(geotrans);
	//std::cout << "trans = " << geotrans[0] << "," << geotrans[1] << "," << geotrans[2] << "," << geotrans[3] << "," << geotrans[4] << "," << geotrans[5] << std::endl;

	// 获取投影信息
	// ----------------
	//std::string proj = pADataSet->GetProjectionRef();
	//设置地理坐标系信息
	//poDataset->SetProjection(projs.c_str());
	//std::cout << "projs = " << proj << std::endl;

	// 获取行和列数
	// rows = Y , col = X
	int nAImgSizeX = pADataSet->GetRasterXSize();
	int nAImgSizeY = pADataSet->GetRasterYSize();
	std::cout << "ImageX = " << nAImgSizeX << ",	ImageY = " << nAImgSizeY << std::endl;

	cv::Mat AImageData(nAImgSizeY, nAImgSizeX, CV_8UC1);

	//int bandCount = pADataSet->GetRasterCount();
	GDALRasterBand* poBand1 = pADataSet->GetRasterBand(1);
	GDALDataType g_type = GDALDataType(poBand1->GetRasterDataType());
	std::cout << "g_type = " << g_type << std::endl;

	pADataSet->GetRasterBand(1)->RasterIO(GF_Read, 0, 0, nAImgSizeX, nAImgSizeY, AImageData.data, nAImgSizeX, nAImgSizeY, g_type, 0, 0);

	// printNdArray(semanticMapData);

	// 获取 坡度图 数据
	// ----------------
	// 获取行和列数
	// rows = Y , col = X
	int nBImgSizeX = pBDataSet->GetRasterXSize();
	int nBImgSizeY = pBDataSet->GetRasterYSize();
	std::cout << "Slope ImageX = " << nBImgSizeX << ",Slope	ImageY = " << nBImgSizeY << std::endl;

	cv::Mat BImageData(nBImgSizeY, nBImgSizeX, CV_8UC1);

	GDALRasterBand* poBand2 = pBDataSet->GetRasterBand(1);
	GDALDataType g_type2 = GDALDataType(poBand2->GetRasterDataType());
	std::cout << "g_type = " << g_type2 << std::endl;

	pBDataSet->GetRasterBand(1)->RasterIO(GF_Read, 0, 0, nBImgSizeX, nBImgSizeY, BImageData.data, nBImgSizeX, nBImgSizeY, g_type2, 0, 0);

	int maxImgSizeX, minImgSizeX, maxImgSizeY, minImgSizeY;
	maxImgSizeX = max(nAImgSizeX, nBImgSizeX);
	minImgSizeX = min(nAImgSizeX, nBImgSizeX);
	maxImgSizeY = max(nAImgSizeY, nBImgSizeY);
	minImgSizeY = min(nAImgSizeY, nBImgSizeY);
	cout << maxImgSizeX << ' ' << minImgSizeX << ' ' << maxImgSizeY << ' ' << minImgSizeY << endl;
	//cout << AImageData.cols << ' ' << AImageData.rows << endl;

	VSIFCloseL(VSIFileFromMemBuffer("/vsimem/gtiff_2", (GByte*)DEMTiffData, DEMDataSize, FALSE));
	GDALDataset* dataset2 = (GDALDataset*)GDALOpen("/vsimem/gtiff_2", GA_ReadOnly);//GA_Update和GA_ReadOnly两种模式
	if (dataset2 == nullptr)
	{
		std::cout << "can't open file!" << std::endl;
		return nullptr;
	}
	VSIUnlink("/vsimem/gtiff_2");

	int nImgSizeX2 = dataset2->GetRasterXSize();
	int nImgSizeY2 = dataset2->GetRasterYSize();
	std::cout << "ImageX2 = " << nImgSizeX2 << ", ImageY2 = " << nImgSizeY2 << std::endl;

	cv::Mat DEMatData(nImgSizeY2, nImgSizeX2, CV_32F);

	//int bandCount = dataset2->GetRasterCount();
	GDALRasterBand* poBand22 = dataset2->GetRasterBand(1);
	GDALDataType g_type22 = GDALDataType(poBand22->GetRasterDataType());
	std::cout << "g_type = " << g_type2 << std::endl;
	dataset2->GetRasterBand(1)->RasterIO(GF_Read, 0, 0, nImgSizeX2, nImgSizeY2, DEMatData.data, nImgSizeX2, nImgSizeY2, g_type22, 0, 0);

	int rows = DEMatData.rows;
	int cols = DEMatData.cols;
	cout << rows << ' ' << cols << endl;
	std::vector<std::vector<float>> DEMData(rows, std::vector<float>(cols));
	for (int i = 0; i < rows; i++) {
		for (int j = 0; j < cols; j++) {
			DEMData[i][j] = DEMatData.at<float>(i, j);
		}
	}

	// 对数据进行泛化性处理
	// --------------------
	cv::Mat AImageDataAfter(minImgSizeY, minImgSizeX, CV_8UC1), BImageDataAfter(minImgSizeY, minImgSizeX, CV_8UC1);
	zoom(AImageData, AImageDataAfter, minImgSizeX, minImgSizeY);
	zoom(BImageData, BImageDataAfter, minImgSizeX, minImgSizeY);

	// 生成lat 和 lon 数组
	// -------------------
	//Trans::Trans trans(geotrans, nAImgSizeY, nAImgSizeX);
	Trans::Trans trans(geotrans, minImgSizeY, minImgSizeX);
	trans.all_GPS();

	//Coordinate lat = read_data("data/lat.txt"); // 27左右 横坐标的经度，纵坐标维度的图
	//Coordinate lon = read_data("data/lon.txt"); // 91左右

	Coordinate lat = trans.all_lat;
	Coordinate lon = trans.all_lon;

	//#### 结束 加载内存数据 #######

	AStar::Preprocess preprocess;
	AStar::Generator generator;

	float max_slope = 60.0f;
	const float object_width = 3.3;
	const float object_length = 7.2;
	const float meter_per_pixel = 0.5;
	const float threshold = 0.05;
	//
	// 
	//std::vector<std::vector<byte>> trafficable_map = mat2vec2(AImageData);
	//std::vector<std::vector<byte>> road_weight = mat2vec2(BImageData);
	//std::vector<std::vector<byte>> trafficable_map = mat2vec2(AImageDataAfter);
	std::vector<std::vector<byte>> road_weight = mat2vec2(BImageDataAfter);

	preprocess.read_data_(generator, AImageDataAfter);

	generator.setHeuristic(AStar::Heuristic::euclidean);
	generator.setDiagonalMovement(true);

	AStar::Vec2i upper_left = { 0, 0 };	// solpe表的左上角点
	AStar::Vec2i lower_right = { lon.size() ,0 - lat.size() }; // solpe表的右下角点


	double st_lat = startPoint.y;
	double st_lon = startPoint.x;

	double en_lat = endPoint.y;
	double en_lon = endPoint.x;

	int st_x = 0;
	int st_y = 0;

	int en_x = 0;
	int en_y = 0;

	for (int i = 0; i < lat.size() - 1; ++i) {
		if (lat[i] > st_lat && lat[i + 1] <= st_lat) {
			st_y = -(i + 1);
			break;
		}
	}
	for (int i = 0; i < lon.size() - 1; ++i) {
		if (lon[i] < st_lon && lon[i + 1] >= st_lon) {
			st_x = i + 1;
			break;
		}
	}

	for (int i = 0; i < lat.size() - 1; ++i) {
		if (lat[i] > en_lat && lat[i + 1] <= en_lat) {
			en_y = -(i + 1);
			break;
		}
	}
	for (int i = 0; i < lon.size() - 1; ++i) {
		if (lon[i] < en_lon && lon[i + 1] >= en_lon) {
			en_x = i + 1;
			break;
		}
	}

	/*AStar::Vec2i start{ st.second, st.first };
	AStar::Vec2i end{ en.second, en.first };*/
	//cout << st_x << ' ' << st_y << ' ' << en_x << ' ' << en_y << endl;

	int st_check = check_point(upper_left, lower_right, st_x, st_y, generator);
	int en_check = check_point(upper_left, lower_right, en_x, en_y, generator);

	//cout << st_x << ' ' << st_y << ' ' << en_x << ' ' << en_y << endl;

	if (st_check == -1 || en_check == -1) {
		jna_path::Result* res = new jna_path::Result;

		jna_path::lat = lat;
		jna_path::lon = lon;

		res->pathSize = 2;
		res->sizePerLineSize = 1;

		res->path = new jna_path::Point[res->pathSize];
		res->sizePerLine = new int[res->sizePerLineSize];

		for (int i = 0; i < 2; ++i) {
			//auto xy = jna_path::transform.XYtoGPS(allPath[i].y, allPath[i].x);

			double output_lat, output_lon;
			output_lat = jna_path::lat[0];
			output_lon = jna_path::lon[0];

			res->path[i].x = output_lon;
			res->path[i].y = output_lat;
			//DUBUG
			// printf("%.8f %.8f\n", output_lon, output_lat);
		}

		for (int i = 0; i < 1; ++i) {
			res->sizePerLine[i] = 2;
		}
	}

	AStar::Vec2i start{ st_x,st_y };
	AStar::Vec2i end{ en_x, en_y };

	std::cout << st_x << " - " << st_y << std::endl;
	std::cout << en_x << " - " << en_y << std::endl;

	duration<double> preProcessTime = system_clock::now() - preProcessBegin;
	std::cout << "Preprocessing time:" << preProcessTime.count() << " seconds" << endl;
	std::cout << "Preprocessing time:" << preProcessTime.count() * 1000 << " ms" << endl;
	std::cout << "Preprocessing time:" << preProcessTime.count() * 1000000 << " us" << endl;
	cout << endl << endl;
	system("cls");

	vector< AStar::Vec2i> starts;
	vector< AStar::Vec2i> ends;
	starts.push_back(start);
	ends.push_back(end);


	auto begin = system_clock::now();

	vector<thread> mythreads;

	AStar::CoordinateList allPath;
	vector<int> sizePerLine;
	for (int i = 0; i < starts.size(); ++i)
	{
		// 双向
		// ---------------
		mythreads.push_back(thread(runOnThread, std::ref(generator), std::ref(preprocess), std::ref(starts[i]), std::ref(ends[i]), std::ref(upper_left), std::ref(lower_right), std::ref(allPath), std::ref(sizePerLine), std::ref(road_weight)));
		
		// 单向
		// ---------------
		//mythreads.push_back(thread(run, std::ref(generator), std::ref(preprocess), std::ref(starts[i]), std::ref(ends[i]), std::ref(upper_left), std::ref(lower_right), std::ref(allPath), std::ref(sizePerLine), std::ref(road_weight)));
	}
	for (auto iter = mythreads.begin(); iter != mythreads.end(); iter++)
	{
		iter->join();
	}

	// 封装返回值
	jna_path::Result* res = new jna_path::Result;

	jna_path::lat = lat;
	jna_path::lon = lon;

	res->pathSize = allPath.size();
	res->sizePerLineSize = sizePerLine.size();

	//cout << allPath.size() << ' ' << sizePerLine.size() << ' ' << sizePerLine[0] <<  endl;

	res->path = new jna_path::Point[res->pathSize];
	res->sizePerLine = new int[res->sizePerLineSize];

	for (int i = 0; i < allPath.size(); ++i) {
		//auto xy = jna_path::transform.XYtoGPS(allPath[i].y, allPath[i].x);

		double output_lat, output_lon;
		output_lat = jna_path::lat[-allPath[i].y];
		output_lon = jna_path::lon[allPath[i].x];

		res->path[i].x = output_lon;
		res->path[i].y = output_lat;
		//DUBUG
		// printf("%.8f %.8f\n", output_lon, output_lat);
	}

	for (int i = 0; i < sizePerLine.size(); ++i) {
		res->sizePerLine[i] = sizePerLine[i];
	}

	duration<double> diff = system_clock::now() - begin;
	std::cout << "elapsed :" << diff.count() << " seconds" << endl;
	std::cout << "elapsed :" << diff.count() * 1000 << " ms" << endl;
	std::cout << "elapsed :" << diff.count() * 1000000 << " us" << endl;
	cout << endl;

	cout << endl;
	auto PathLen = clacPathLen(allPath, DEMData);
	cout << "len of path:" << fixed << setprecision(4) << PathLen << endl;
	cout << endl;

	return res;
}

int main(int argc, char* argv[]) {

	std::string accmap_data_path = "D:\\code\\graduate\\zzz_Graduate\\data\\car_2.tif";//可通行性图
	int accmap_data_size = 0;
	std::string weightmap_data_path2 = "D:\\code\\graduate\\zzz_Graduate\\data\\weight_2.tif";//地物分类图
	int weightmap_data_size = 0;

	byte* accMap = (byte*)GetStream(accmap_data_path.c_str(), accmap_data_size);
	byte* weightMap = (byte*)GetStream(weightmap_data_path2.c_str(), weightmap_data_size);

	//std::string dem_path = "D:\\code\\graduate\\zzz_Graduate\\data\\dem.tif";
	std::string dem_path = "D:\\code\\graduate\\zzz_Graduate\\data\\car_2.tif";
	int dem_size = 0;

	byte* dem = (byte*)GetStream(dem_path.c_str(), dem_size);

	jna_path::Line* point = new jna_path::Line;

	// 100*100
	// --------
	point->start.x = 91.957207;
	point->start.y = 27.624718;
	point->end.x = 91.956214;
	point->end.y = 27.623480;

	// 250*250
	// --------
	//point->start.x = 91.962657;
	//point->start.y = 27.619506;
	//point->end.x = 91.965817;
	//point->end.y = 27.621240;

	// 500*500
	// --------
	//point->start.x = 91.9571;
	//point->start.y = 27.624845;
	//point->end.x = 91.95417947;
	//point->end.y = 27.623128;

	// 750*750
	// --------
	//point->start.x = 91.955180;
	//point->start.y = 27.625643;
	//point->end.x = 91.964680;
	//point->end.y = 27.619608;

	// 1500*1500
	// ----------
	//point->start.x = 91.96207;
	//point->start.y = 27.62938;
	//point->end.x = 91.95417947;
	//point->end.y = 27.623128;

	// 分图对比
	point->start.x = 91.972699;
	point->start.y = 27.601722;
	point->end.x = 91.976333;
	point->end.y = 27.595103;

	jna_path::Point stPoint = { point->start.x,
				point->start.y };

	jna_path::Point edPoint = { point->end.x,
			point->end.y };

	int errcode = -1;
	jna_path::Args* args = new jna_path::Args;

	jna_path::Result* res = getPathFromMem(accMap, accmap_data_size, weightMap, weightmap_data_size, args, stPoint, edPoint, &errcode, dem, dem_size);

	cout << "size of path point:" << res->pathSize << endl;
	makeResultGeoJson(res, "D:\\code\\graduate\\zzz_Graduate\\data\\car_street_2.json");
	return 0;
}