/* 005ac154: one-time initialisation under lock 11. */
#define done_005ac154 (*(long *)0x006aff90)
#define lock_005ac154_005a4ba4 ((void (__cdecl *)(long))0x005a4ba4)
#define unlock_005ac154_005a4c05 ((void (__cdecl *)(long))0x005a4c05)
#define init_005ac154_005ac182 ((void (__cdecl *)(void))0x005ac182)

void __cdecl init_once_005ac154(void)
{
    if (done_005ac154 == 0) {
        lock_005ac154_005a4ba4(11);
        if (done_005ac154 == 0) {
            init_005ac154_005ac182();
            done_005ac154++;
        }
        unlock_005ac154_005a4c05(11);
    }
}
