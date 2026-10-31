/* 00443250: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00443250 {
    U function_00443250(U a0);
};

U Object_00443250::function_00443250(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)a0;
    *(unsigned long *)self = (unsigned long)t1;
    U t2 = *(unsigned char *)(a0 + 0x4u);
    U t3 = (t1 & 0xffffff00u) | (t2 & 0xffu);
    *(unsigned char *)(self + 0x4u) = (unsigned char)(t3 & 0xffu);
    U t4 = *(unsigned short *)(a0 + 0x6u);
    U t5 = (a0 & 0xffff0000u) | (t4 & 0xffffu);
    *(unsigned short *)(self + 0x6u) = (unsigned short)(t5 & 0xffffu);
    return self;
}
