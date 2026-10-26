/* 0041dd20: stores (argument == 0) in the byte at +0xb0. */
struct Object_0041dd20 {
    unsigned char unknown_00[0xb0];
    unsigned char flag;
    void set(unsigned long a);
};

void Object_0041dd20::set(unsigned long a)
{
    flag = (a == 0);
}
