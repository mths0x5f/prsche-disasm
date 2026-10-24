/* 00556640: size in bytes of a block from the EA heap.
 *
 * allocate_00531ca0 puts a 16-byte header in front of every allocation (magic 'MB' = 0x424d,
 * written by heap_block_005320b0); the requested size sits at offset 4 of that header, which
 * is 12 bytes before the data the caller gets. install_paths_load_004b6ff0 calls this on the
 * install.txt blob to find where its text ends.
 *
 * Original (cdecl, 8 bytes):  mov eax,[esp+4] / mov eax,[eax-0Ch] / ret
 */
struct HeapBlockHeader {
    unsigned short magic;          /* 0x424d */
    unsigned short flags;
    long bytes;                    /* size requested by the caller */
    HeapBlockHeader *next;
    HeapBlockHeader *previous;
};

long __cdecl install_paths_size_00556640(const void *data)
{
    const HeapBlockHeader *block = (const HeapBlockHeader *)((const char *)data - sizeof(HeapBlockHeader));
    return block->bytes;
}

/* Called from lowered code: argument on the guest stack, result in EAX, cdecl RET. */
void install_paths_size_00556640_430(Machine257 &s)
{
    U esp = s.r[4];
    s.r[0] = (U)install_paths_size_00556640((const void *)read257(esp + 4, 4));
    s.pc = read257(esp, 4);
    s.r[4] = esp + 4;
    s.stop = STOP257_RETURNED;
}
