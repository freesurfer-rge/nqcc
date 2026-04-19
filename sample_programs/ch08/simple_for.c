int main(void) {
    int i = V0;
    int counter = 0;
    for( int i=V0; i < V1; i = i + V2) {
        if( i==1 ) continue;
        counter = counter + 1;
    }
    return counter;
}