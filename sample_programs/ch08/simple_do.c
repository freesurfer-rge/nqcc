int main(void) {
    int i = V0;
    int counter = 0;
    do {
        counter = counter + 1;
        i = i + V2;
    } while( i < V1 ) ;
    return counter;
}