/* 0045ccb0: Frees the two global blocks at 00627e38 / 00627e3c (the first one's first byte is cleared) and nulls both. */
#define free_0059f050 ((void (__cdecl *)(void *))0x0059f050)
#define block_a_00627e38 (*(void **)0x00627e38)
#define block_b_00627e3c (*(void **)0x00627e3c)

void __cdecl free_blocks_0045ccb0(void)
{
    void *block;

    if (block_a_00627e38 != 0) {
        *(char *)block_a_00627e38 = 0;
        free_0059f050(block_a_00627e38);
    }
    block = block_b_00627e3c;
    block_a_00627e38 = 0;
    free_0059f050(block);
    block_b_00627e3c = 0;
}
