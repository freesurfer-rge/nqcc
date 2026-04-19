int main(void) {
    int counter = 0;
    for( int a=0; a<V0; a=a+1) {
        if( a==4 ) break;

        int b=0;
        while(b<a) {
            b = b+1;
            if( b+3 == a) continue;
            counter=counter+1;
        }
    }

    return counter;
}