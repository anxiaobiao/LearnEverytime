#include <iostream>
#include <stdlib.h>
#include "Operation_plus.hpp"

using namespace std;



int main(){
    int a, b;
    char opera;
    cout << "���������֣�" << endl;
    cin >> a >> b;
    cout << "��������ţ�" << endl;
    cin >> opera;

    Operation operation(a, b, opera);
    // operation.setSymbol(opera);
    // operation.setValue(a, b);
    int res = operation.res();
    cout << a << opera << b << '=' << res << endl;

    return 0;
}