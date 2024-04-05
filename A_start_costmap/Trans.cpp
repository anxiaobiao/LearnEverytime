#include"Trans.h"

Trans::Trans::Trans(double* mercator_, int weight_, int hight_) {
	for (int i = 0; i < 6; ++i) {
		mercator[i] = mercator_[i];
	}

	weight = weight_;
	hight = hight_;
}

// 图坐标为整数
Trans::Point_GPS Trans::Trans::XY_GPS(int x, int y) {
	y = std::abs(y);
	x = std::abs(x);

	double XY_x = mercator[0] + x * mercator[1] + y * mercator[2];
	double XY_y = mercator[3] + x * mercator[4] + y * mercator[5];

	double lon = XY_x / 20037508.34 * 180;
	double lat_temp = XY_y / 20037508.34 * 180;
	double lat = 180 / M_PI * (2 * std::atan(std::exp(lat_temp * M_PI / 180)) - M_PI / 2);

	return { lon, lat };
}

// 图坐标为浮点数
Trans::Point_GPS Trans::Trans::XY_GPS(float x, float y) {
	y = std::abs(y);
	x = std::abs(x);

	double XY_x = mercator[0] + x * mercator[1] + y * mercator[2];
	double XY_y = mercator[3] + x * mercator[4] + y * mercator[5];

	double lon = XY_x / 20037508.34 * 180;
	double lat_temp = XY_y / 20037508.34 * 180;
	double lat = 180 / M_PI * (2 * std::atan(std::exp(lat_temp * M_PI / 180)) - M_PI / 2);

	return { lon, lat };
}

void Trans::Trans::all_GPS() {
	double temp, temp_lon, temp_lat;
	// lon的求取
	for (int i = 0; i < hight; ++i) {
		temp = mercator[0] + i * mercator[1];
		temp_lon = temp / 20037508.34 * 180;
		all_lon.push_back(temp_lon);
	}
	// lat的求取
	for (int i = 0; i < weight; ++i) {
		temp = mercator[3] + i * mercator[5];
		double temp1 = temp / 20037508.34 * 180;
		temp_lat = 180 / M_PI * (2 * std::atan(std::exp(temp1 * M_PI / 180)) - M_PI / 2);
		all_lat.push_back(temp_lat);
	}
}

Trans::Point_XY Trans::Trans::match(float lat, float lon) {
	int x = 0;
	int y = 0;

	for (int i = 0; i < all_lat.size() - 1; ++i) {
		if (all_lat[i] > lat && all_lat[i + 1] <= lat) {
			y = -(i + 1);
			break;
		}
	}
	for (int i = 0; i < all_lon.size() - 1; ++i) {
		if (all_lon[i] < lon && all_lon[i + 1] >= lon) {
			x = i + 1;
			break;
		}
	}

	return { x, y };
}
