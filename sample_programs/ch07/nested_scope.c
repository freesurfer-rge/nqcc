int main(void) {
    int a = V0 * 3;
    int b;
    {
        int a = 60 / V1;
        b = a + V2;
    }
    return b % a;
}