/* 0044fe70: fills a small record (word, byte 1, 16-bit value) and returns it. */
struct Record_0044fe70 {
    unsigned long value;
    unsigned char flag;
    unsigned char unknown_05;
    unsigned short extra;
    Record_0044fe70 *set(unsigned long v, unsigned short e);
};

Record_0044fe70 *Record_0044fe70::set(unsigned long v, unsigned short e)
{
    value = v;
    flag = 1;
    extra = e;
    return this;
}
