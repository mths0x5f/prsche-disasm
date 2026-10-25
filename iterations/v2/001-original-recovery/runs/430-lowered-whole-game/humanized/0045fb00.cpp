/* 0045fb00: returns element [index] of the dword array the object starts with. */
struct Array_0045fb00 {
    unsigned long item[1];
    unsigned long fn_0045fb00(unsigned long index);
};

unsigned long Array_0045fb00::fn_0045fb00(unsigned long index)
{
    return item[index];
}
