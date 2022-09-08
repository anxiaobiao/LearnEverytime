

typedef std::pair<float, float> pFloat;

class Transform {
public:
	Transform(float _lon, float _lat);

	float radians(float _deg);
	float degrees(float _rad);
	float clip(float a, float a_min, float a_max);

	pFloat GPStoXY(float _lon, float _lat);
	pFloat XYtoGPS(int _x, int _y);

private:
	int CONSTANTS_RADIUS_OF_EARTH = 6371000;
	float ref_lon;
	float ref_lat;

};