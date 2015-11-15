#include <iostream>
#include <cstdio>
#include <vector>
using namespace std;

int main(){
	int k,l,m,n,prev = 0;
	cin>>k>>l>>m;
	vector<int> a(1000001, 0);
	vector<int> f(3);
	a[1] = a[k] = a[l] = 1;
	f[0] = 1;
	f[1] = k;
	f[2] = l;
	while(m-- > 0){
		cin>>n;
		if(n < prev){
			char c = a[n] == 0 ? 'B' : 'A';
			cout<<c;
		}
		for(int i = prev + 1; i <= n; i++){
			if(i == k || i == l){
				a[i] = 1;
				//cout<<a[i];
				continue;
			}
			int x,y,z,j = -1, marker = 0;
			if( i < k && i < l){
				if(i%2 == 0){
					a[i] = 0;
				} else {
					a[i] = 1;
				}
				continue;
			}
			while( ++j < 3){
				x = f[j]+ 1;
				y = f[j]+ k;
				z = f[j]+ l;								
				if( i-x >= 0 && a[i - x] == 0 ){
					continue;
				} else if( i-y >= 0 && a[i - y] == 0 ){
					continue;
				} else if( i-z >= 0 && a[i - z] == 0 ){
					continue;
				} else if( !(x > i && y > i && z > i) ){
					marker++;
				}
			}
			if(marker == 0){
				a[i] = 0;
			} else {
				a[i] = 1;
			}
			//cout<<a[i];
		}
		//cout<<endl;		
		char c = a[n] == 0 ? 'B' : 'A';
		cout<<c;
	}
	//cout<<endl;
	return 0;
}