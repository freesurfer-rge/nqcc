int main(void) {
    int a = V0;
    if( a>1) {
        int b = a;
        b = b + 1;
        a = b - 2;
    } else {
        // Note RHS will be from outer scope
        int a = a;
        a = a + 10;
    }

    return a;
}