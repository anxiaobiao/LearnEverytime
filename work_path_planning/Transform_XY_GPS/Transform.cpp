#include<math.h>
#include <utility>
#include"Transform.hpp"

#define PI 3.1415926

Transform::Transform(float _lon, float _lat) {
	ref_lon = _lon;
	ref_lat = _lat;
}

float Transform::radians(float _deg) {
	return _deg * PI / 180;
}
float Transform::degrees(float _rad) {
	return _rad * 180 / PI;
}
float Transform::clip(float a, float a_min, float a_max) {
	if (a < a_min) {
		return a_min;
	}
	else if (a > a_max) {
		return a_max;
	}
	else {
		return a;
	}
}

pFloat Transform::GPStoXY(float lon, float lat) {
	float lat_rad = radians(lat);
	float lon_rad = radians(lon);
	float ref_lat_rad = radians(ref_lat);
	float ref_lon_rad = radians(ref_lon);

	float sin_lat = sin(lat_rad);
	float cos_lat = cos(lat_rad);
	float ref_sin_lat = sin(ref_lat_rad);
	float ref_cos_lat = cos(ref_lat_rad);

	float cos_d_lon = cos(lon_rad - ref_lon_rad);

	float arg = clip(ref_sin_lat * sin_lat + ref_cos_lat * cos_lat * cos_d_lon, -1.0, 1.0);
	float c = acos(arg);

	float k = 1.0;
	if (abs(c) > 0) {
		k = (c / sin(c));
	}
	float x = float(k * (ref_cos_lat * sin_lat - ref_sin_lat * cos_lat * cos_d_lon) * CONSTANTS_RADIUS_OF_EARTH);
	float y = float(k * cos_lat * sin(lon_rad - ref_lon_rad) * CONSTANTS_RADIUS_OF_EARTH);

	return { x, y };
}
pFloat Transform::XYtoGPS(int x_int, int y_int) {
	float x = (float)x_int;
	float y = (float)y_int;

	pFloat temp = GPStoXY(ref_lon, ref_lat);
	float ref_x = temp.first;
	float ref_y = temp.second;
	if (x == ref_x and y == ref_y) {
		return { ref_lon, ref_lat };
	}

	float x_rad = float(x) / CONSTANTS_RADIUS_OF_EARTH;
	float y_rad = float(y) / CONSTANTS_RADIUS_OF_EARTH;
	float c = sqrt(x_rad * x_rad + y_rad * y_rad);

	float ref_lat_rad = radians(ref_lat);
	float ref_lon_rad = radians(ref_lon);

	float ref_sin_lat = sin(ref_lat_rad);
	float ref_cos_lat = cos(ref_lat_rad);

	float lat, lon;
	if (abs(c) > 0) {
		float sin_c = sin(c);
		float cos_c = cos(c);

		float lat_rad = asin(cos_c * ref_sin_lat + (x_rad * sin_c * ref_cos_lat) / c);
		float lon_rad = (ref_lon_rad + atan2(y_rad * sin_c, c * ref_cos_lat * cos_c - x_rad * ref_sin_lat * sin_c));

		lat = degrees(lat_rad);
		lon = degrees(lon_rad);
	}
	else {
		lat = degrees(ref_lat);
		lon = degrees(ref_lon);
	}
	
	return { lon, lat };
	
}