/* 00460eb0: frees the block an object holds at +4. */
struct OwnedBlock_00460eb0 {
    unsigned long unknown_00;
    void *block;
    void release();
};

#define game_free_0059f050 ((void (__cdecl *)(void *))0x0059f050)

void OwnedBlock_00460eb0::release()
{
    game_free_0059f050(block);
}
