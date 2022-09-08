#include<iostream>
#include <iomanip> 
#include"Transform.hpp"

int main() {
	Transform transform(112.920345, 28.063696);

	//auto res = transform.GPStoXY(112.920633, 28.063395);
	auto res = transform.XYtoGPS(-33, 28);
	std::cout << std::setprecision(9) << res.first << ' ' << res.second << std::endl;
}