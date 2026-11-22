#include <iostream>
#include <vector>

using namespace std;

int main() {
    int t;
    cin >> t;
    
    while (t--) {
        int n;
        int k;
        cin >> n >> k;
        
        vector<int> result(n);
        
        if (n % 2 == 1) {
            // For odd n, fill the row with `k`
            for (int i = 0; i < n; ++i) {
                result[i] = k;
            }
        } else {
            // For even n, alternate between `k` and `0`
            for (int i = 0; i < n; ++i) {
                result[i] = (i % 2 == 0) ? k : 0;
            }
        }
        
        for (int i = 0; i < n; ++i) {
            cout << result[i] << " ";
        }
        cout << "\n";
    }
    
    return 0;
}