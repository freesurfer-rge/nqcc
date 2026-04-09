int main( void ) {
    int a = V0;
    int b = V1;

    if( a<4)
        if( b>=a+2 )
            b=b+V2;
        else
            b=a/2;
    
    return a + b;
}