#include "porsche/heap.hpp"
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
extern unsigned int DAT_006b4f20;
using U=std::uint32_t;
U fail272=0;
volatile U canary_before272=0x1234abcd,canary_after272=0xfedc4321;
alignas(16) unsigned char safe272[256];
static U load272(const unsigned char* p){return U(p[0])|(U(p[1])<<8)|(U(p[2])<<16)|(U(p[3])<<24);}
static void store272(unsigned char* p,U value){for(U i=0;i<4;++i)p[i]=static_cast<unsigned char>(value>>(i*8));}
extern "C" void __cdecl entry(){
 static_assert(sizeof(void*)==4&&sizeof(porsche::heaps_006b4f20)==64,"one original 64B table");
 unsigned char* typed=reinterpret_cast<unsigned char*>(&porsche::heaps_006b4f20[0]);
 volatile U* raw=reinterpret_cast<volatile U*>(&DAT_006b4f20);
 if(reinterpret_cast<const void*>(&DAT_006b4f20)!=reinterpret_cast<const void*>(&porsche::heaps_006b4f20[0]))++fail272;
 for(U i=0;i<64;++i)if(typed[i]!=0)++fail272;
 for(U i=0;i<16;++i){
  U bits=0x80000000u^(0x01020304u*i)^i;
  raw[i]=bits;
  if(load272(typed+i*4)!=bits)++fail272;
  for(U j=0;j<i;++j)if(load272(typed+j*4)!=(0x80000000u^(0x01020304u*j)^j))++fail272;
 }
 for(U i=0;i<16;++i){
  porsche::heaps_006b4f20[i]=reinterpret_cast<porsche::OriginalHeap*>(safe272+i*16);
  if(raw[i]!=reinterpret_cast<U>(safe272+i*16))++fail272;
 }
 for(U i=0;i<16;++i){
  U bits=0xf0000000u|(i<<20)|0x000abcdu;
  store272(typed+i*4,bits);
  if(raw[i]!=bits)++fail272;
 }
 if(canary_before272!=0x1234abcdu||canary_after272!=0xfedc4321u)++fail272;
 ExitProcess(fail272?1:0);
}
