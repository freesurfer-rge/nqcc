static int call_count = 0;

int my_func(void) {
    call_count = call_count + 1;
    return 10;
}

int main(void) {
    for( int i=0; i<V0; i=i+1) {
        int a = my_func();
    }
    return call_count;
}