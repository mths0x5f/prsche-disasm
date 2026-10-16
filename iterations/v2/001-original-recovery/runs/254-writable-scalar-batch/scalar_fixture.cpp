extern unsigned int DAT_0060c9ec;
extern int DAT_0061bc4c;
extern unsigned int DAT_0069c9f0;
extern unsigned int DAT_0069c9f4;
extern unsigned int DAT_0069c9f8;
extern unsigned int DAT_0069c9fc;
extern int DAT_0069e0ac;
extern unsigned int DAT_006a6420;
extern int DAT_005e7530;
extern int DAT_0060c7ec;
extern int DAT_0060c7f0;
extern unsigned int DAT_0060c974;
extern unsigned int DAT_00628f88;
extern unsigned int DAT_0065b940;
extern unsigned int DAT_006907e4;
extern int DAT_00690ad4;
extern int DAT_00699d58;
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned int);
static unsigned int raw_word(const void*p){const unsigned char*b=static_cast<const unsigned char*>(p);return b[0]|(static_cast<unsigned int>(b[1])<<8)|(static_cast<unsigned int>(b[2])<<16)|(static_cast<unsigned int>(b[3])<<24);}
static void store_word(void*p,unsigned int v){unsigned char*b=static_cast<unsigned char*>(p);for(unsigned int i=0;i<4;++i)b[i]=static_cast<unsigned char>(v>>(8*i));}
extern "C" void __cdecl entry(){
 void*cells[17]={&DAT_0060c9ec,&DAT_0061bc4c,&DAT_0069c9f0,&DAT_0069c9f4,&DAT_0069c9f8,&DAT_0069c9fc,&DAT_0069e0ac,&DAT_006a6420,&DAT_005e7530,&DAT_0060c7ec,&DAT_0060c7f0,&DAT_0060c974,&DAT_00628f88,&DAT_0065b940,&DAT_006907e4,&DAT_00690ad4,&DAT_00699d58};
 const unsigned int patterns[6]={0,1,0x7fffffffu,0x80000000u,0x80000001u,0xffffffffu};
 for(unsigned int i=0;i<17;++i){if(raw_word(cells[i])!=0)ExitProcess(1);for(unsigned int j=i+1;j<17;++j)if(cells[i]==cells[j])ExitProcess(2);}
 for(unsigned int i=0;i<17;++i){for(unsigned int p=0;p<6;++p){store_word(cells[i],patterns[p]);if(raw_word(cells[i])!=patterns[p])ExitProcess(3);for(unsigned int j=0;j<17;++j)if(j!=i&&raw_word(cells[j])!=0)ExitProcess(4);}store_word(cells[i],0);}
 for(unsigned int i=0;i<17;++i)if(raw_word(cells[i])!=0)ExitProcess(5);ExitProcess(0);}
