#include <iostream>
#include <vector>
#define MAX(a,b)	a > b ? a : b
using namespace std;

long int computeUtil(vector<long int> &a, vector<long int> &mem,long int sum, int i, int j){
	if(i >= j )
		return sum;
	// if(j - i <= 3){
	// 	long int sum1 = sum;
	// 	for(int k = i; k < j; k++){
	// 		sum1 += a[k];
	// 	}
	// 	if(mem[i] < sum1)
	// 		mem[i] = sum1;
	// }
	//if(mem[i] != -1)
	//	return mem[i];
	
	long int sum1 = computeUtil( a,mem,sum+a[i], i+2, j);
	if(i+1 < j){		
		sum1 = MAX(sum1,computeUtil( a,mem, sum+ a[i] + a[i+1], i+4, j));
	}
	if(i+2 < j){		
		sum1 = MAX(sum1,computeUtil( a,mem, sum +a[i] + a[i+1] +a[i+2], i+6, j));
	}
	
	//mem[i] = sum1;
	return sum1;
}
/*
2
4
5 4 3 2
6
10 8 7 11 15 20
*/
long int iterative(vector<long int> &a, vector<long int> &mem, int n){
	long int ans;
	int i;
	for( i = n-1; i >= 0; i--){
		if( n-1 - i  <= 2 ){
			long int tmp = 0;
			for( int j = i; j < n; j++){
				tmp+= a[j];
			}
			mem[i] = tmp;
		} else {
			long int max1, max2, max3;
			max1 = max2 = max3 = 0;			
			max1 = a[i]+ (i+2 < n ? mem[i+2] : 0);
			max2 = a[i]+a[i+1]+ (i+4 < n ? mem[i+4] : 0);
			max3 = a[i]+a[i+1]+a[i+2]+ (i+6 < n ? mem[i+6] : 0);
			max1 = MAX(max1,max2);
			max1 = MAX(max1,max3);
			mem[i] = max1;
		}
	}
	ans = mem[0];
	return ans;
}

void compute(vector<long int> &a, int n){
	vector<long int> mem(n, -1);
	//cout<<computeUtil(a, mem,0, 0, n)<<endl;
	cout<<iterative(a, mem, n)<<endl;
}

int main(){
	int t, n,i;
	cin>>t;
	while ( t-- > 0){
		cin>>n;
		vector<long int> a(n);
		for(i = 0; i < n; i++){
			cin>>a[i];
		}
		compute(a,n);
	}
	return 0;
}