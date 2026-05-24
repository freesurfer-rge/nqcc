int add_value(int a) {
    int b = V0;
    return a + b;
}

int main(void) {
    int c = V1;
    int d = c + add_value(V2);
    return d;
}