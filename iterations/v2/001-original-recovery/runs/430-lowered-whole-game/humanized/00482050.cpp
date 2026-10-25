/* 00482050: copies 0xe dwords from the source to the destination when the destination is not null. */
struct Block_00482050 {
    unsigned long data[0xe];
};

void __cdecl copy_block_00482050(Block_00482050 *dest, const Block_00482050 *src)
{
    if (dest != 0)
        *dest = *src;
}
