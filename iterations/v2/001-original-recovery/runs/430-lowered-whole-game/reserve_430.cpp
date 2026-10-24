// Reserves 0x00401000..0x006e3000 of the host EXE (based at 0x00400000) for the original
// Porsche.exe sections. This object is linked first, so its section is the first one, at RVA
// 0x1000; the runtime copies the original sections over it and makes it non-executable.
#pragma data_seg(".text")
extern "C" char reserve430[0x2e2000] = { 1 };
#pragma data_seg()
