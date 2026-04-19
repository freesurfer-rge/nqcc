int main(void) {
    int i = V0;
    int counter = 0;
    while( i < V1 ) {
        counter = counter + 1;
        i = i + V2;
    }
    return counter;
}