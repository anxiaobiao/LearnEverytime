#include <iostream>

using namespace std;

class Operation
{
private:
    int num1, num2;
    char o;

public:

    Operation(int a, int b, char opera);
    // void setValue(int a, int b){
    //     num1 = a;
    //     num2 = b;
    //     //cout << num1 << ',' << num2 << endl;
    // }

    // void setSymbol(char opera){
    //     o = opera;
    //     //cout << o << endl;
    // }

    int res(){
        // cout << "ÔËËãÖÐ...\n" << num1 << o << num2 << '=';

        if(o == '+'){
            // cout << num1 + num2 << endl;
            return num1 + num2;
        }else if (o == '-'){
            // cout << num1 - num2 << endl;
            return num1 - num2;
        }else{
            cout << "done" << endl;
            exit(100);
        }

}
};
Operation::Operation(int a, int b, char opera){
    num1 = a;
    num2 = b;
    o = opera;
}

