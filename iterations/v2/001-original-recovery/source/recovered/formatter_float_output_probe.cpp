#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <Windows.h>
#include <bcrypt.h>
#pragma comment(lib,"bcrypt.lib")
#include "porsche/formatter_float_output.hpp"
#include "porsche/formatter_strings.hpp"
#include "porsche/formatter_crt_runtime.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>
namespace porsche {
std::vector<unsigned char> float_trace;
std::uint32_t float_trace_events=0;
void formatter_float_output_trace(std::uint32_t tag,std::uint32_t phase,const void* p,std::uint32_t n){const std::uint32_t head[]={tag,phase,n};const auto* h=reinterpret_cast<const unsigned char*>(head);float_trace.insert(float_trace.end(),h,h+12);const auto* bytes=static_cast<const unsigned char*>(p);float_trace.insert(float_trace.end(),bytes,bytes+n);++float_trace_events;}
std::int32_t formatter_float_character_width_005e54dc=1;
std::uint32_t formatter_float_decimal_word_005e54e0='.';
// Link guards for unused functions in the canonical dependency translation units.
// Any unexpected traversal fails immediately; none are conversion substitutes.
const std::uint8_t formatter_crt_signal_table_005e5ec8[1]{};
void* __stdcall formatter_dialog_load_library(const char*){std::abort();}
void* __stdcall formatter_dialog_get_proc_address(void*,const char*){std::abort();}
[[noreturn]] void __cdecl formatter_fatal_005a2e22(int){std::abort();}
void __stdcall formatter_lowio_critical_initialize(void*){std::abort();}
void __stdcall formatter_lowio_critical_enter(void*){std::abort();}
void __stdcall formatter_lowio_critical_leave(void*){std::abort();}
void* __cdecl formatter_crt_small_allocate_005aad00(std::uint32_t){std::abort();}
void __cdecl formatter_crt_small_free_005aa9d5(std::uint8_t*,void*){std::abort();}
void* __stdcall formatter_crt_heap_allocate(std::uint32_t,std::uint32_t,std::uint32_t){std::abort();}
int __stdcall formatter_crt_heap_free(std::uint32_t,std::uint32_t,void*){std::abort();}
std::uint32_t __stdcall formatter_crt_tls_allocate(){std::abort();}
void* __stdcall formatter_crt_tls_get(std::uint32_t){std::abort();}
int __stdcall formatter_crt_tls_set(std::uint32_t,void*){std::abort();}
std::uint32_t __stdcall formatter_crt_get_last_error(){std::abort();}
void __stdcall formatter_crt_set_last_error(std::uint32_t){std::abort();}
std::uint32_t __stdcall formatter_crt_thread_id(){std::abort();}
}
namespace {
using U=std::uint32_t;
constexpr U BASE=0x23000000;
constexpr U ORIGINAL=0x30000000;
U op,a,b,c,d,decimal,control,prefix;
unsigned char* arena=reinterpret_cast<unsigned char*>(BASE);
const U vas[]={0x5a3f31,0x5a4054,0x5a4150,0x5abdcc,0x5adaae,0x5adacf,0x5adb2d,0x5adb5b,0x5adf5b,0x5ae17b,0x5adc4f,0x5abcf9,0x5a3f92,0x5a40a9,0x5a4234,0x5abd70};
U address(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
void write(U offset,U v){std::memcpy(arena+offset,&v,4);}
U read(U offset){U v;std::memcpy(&v,arena+offset,4);return v;}
std::string hex(const void* pointer,unsigned size){const auto* p=static_cast<const unsigned char*>(pointer);const char* digits="0123456789abcdef";std::string out;for(unsigned i=0;i<size;++i){out+=digits[p[i]>>4];out+=digits[p[i]&15];}return out;}
__declspec(noinline) U invoke(const void* function,U count,const U* args){
 U result,before,after,saved_bx,saved_si,saved_di,flags;
 __asm {
  push ebx
  push esi
  push edi
  mov before,esp
  mov ecx,count
  mov edx,args
 push_argument:
  test ecx,ecx
  jz invoke_body
  dec ecx
  push dword ptr [edx+ecx*4]
  jmp push_argument
 invoke_body:
  mov ebx,12345678h
  mov esi,12345678h
  mov edi,12345678h
  cld
  call function
  mov result,eax
  mov saved_bx,ebx
  mov saved_si,esi
  mov saved_di,edi
  pushfd
  pop eax
  mov flags,eax
  mov ecx,count
  lea esp,[esp+ecx*4]
  mov after,esp
  pop edi
  pop esi
  pop ebx
 }
 if(before!=after||saved_bx!=0x12345678||saved_si!=0x12345678||saved_di!=0x12345678||(flags&0x400))std::abort();return result;
}
void reset_fpu(){
 const unsigned short cw=static_cast<unsigned short>(control);const double value=7.25;
 __asm {fninit}
 for(int i=0;i<8;++i){__asm {fldz}}
 __asm {fninit}
 __asm {fldcw cw}
 for(U i=0;i<prefix;++i){__asm {fld qword ptr [value]}}
 if(control>>16){U environment[7];__asm {fnstenv environment}environment[1]|=(control>>16)&0x473f;__asm {fldenv environment}}
}
void execute(bool original,const std::vector<unsigned char>& payload){
 using namespace porsche;
 if(!original){float_trace.clear();float_trace_events=0;}
 std::memset(arena,0xa5,4096);std::memcpy(arena+16,payload.data(),payload.size());
 formatter_float_decimal_word_005e54e0=decimal;std::memcpy(reinterpret_cast<void*>(ORIGINAL+0x1e54e0),&decimal,4);
 U args[6]{};U count=0;
 const void* functions[]={reinterpret_cast<const void*>(formatter_float_scientific_005a3f31),reinterpret_cast<const void*>(formatter_float_fixed_005a4054),reinterpret_cast<const void*>(formatter_float_general_005a4150),reinterpret_cast<const void*>(formatter_float_expand64_005abdcc),reinterpret_cast<const void*>(formatter_float_add_word_005adaae),reinterpret_cast<const void*>(formatter_float_add96_005adacf),reinterpret_cast<const void*>(formatter_float_left96_005adb2d),reinterpret_cast<const void*>(formatter_float_right96_005adb5b),reinterpret_cast<const void*>(formatter_float_multiply96_005adf5b),reinterpret_cast<const void*>(formatter_float_scale96_005ae17b),reinterpret_cast<const void*>(formatter_float_extended_digits_005adc4f),reinterpret_cast<const void*>(formatter_float_round_digits_005abcf9),reinterpret_cast<const void*>(formatter_float_scientific_digits_005a3f92),reinterpret_cast<const void*>(formatter_float_fixed_digits_005a40a9),reinterpret_cast<const void*>(formatter_float_shift_text_005a4234),reinterpret_cast<const void*>(formatter_float_decimal_digits_005abd70)};
 if(op<=2){args[0]=BASE+16;args[1]=BASE+1024;args[2]=a;args[3]=b;count=op==1?3:4;}
 else if(op==3){args[0]=BASE+1024;args[1]=BASE+16;count=2;}
 else if(op==4){args[0]=a;args[1]=b;args[2]=BASE+1024;count=3;}
 else if(op==5||op==8){args[0]=BASE+16;args[1]=BASE+32;count=2;}
 else if(op==6||op==7){args[0]=BASE+16;count=1;}
 else if(op==9){args[0]=BASE+16;args[1]=a;args[2]=b;count=3;}
 else if(op==10){args[0]=read(16);args[1]=read(20);args[2]=read(24);args[3]=a;args[4]=b;args[5]=BASE+1024;count=6;}
 else if(op>=11&&op<=13){
  write(64,a);write(68,b);write(72,17);write(76,BASE+16);
  args[0]=BASE+1024;
  if(op==11){args[1]=c;args[2]=BASE+64;count=3;}
  else {std::memcpy(arena+1024,payload.data(),payload.size());args[1]=c;if(op==12){args[2]=d&255;args[3]=BASE+64;args[4]=d>>8;count=5;}else{args[2]=BASE+64;args[3]=d;count=4;}}
 }else if(op==14){std::memcpy(arena+1024,payload.data(),payload.size());args[0]=BASE+1024;args[1]=a;count=2;}
 else {args[0]=read(16);args[1]=read(20);args[2]=BASE+1024;args[3]=BASE+2048;count=4;}
 reset_fpu();const U result=invoke(original?reinterpret_cast<const void*>(ORIGINAL+vas[op]-0x400000):functions[op],count,args);
 unsigned char fpu[108];__asm {fnsave fpu}
 const bool meaningful=op<=2||op==4||op==10||op==12||op==13||op==15;
 std::printf("{\"return\":%u,\"arena\":\"%s\",\"fpu\":\"%s%s%s%s\"}",meaningful?result:0,hex(arena,4096).c_str(),hex(fpu,2).c_str(),hex(fpu+4,2).c_str(),hex(fpu+8,2).c_str(),hex(fpu+28,80).c_str());
}
}
int main(int argc,char** argv){
 if(argc!=2)return 2;std::ifstream file(argv[1],std::ios::binary);std::vector<unsigned char> image((std::istreambuf_iterator<char>(file)),{});if(image.size()<0x100)return 3;
 const auto* dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(image.data());const auto* pe=reinterpret_cast<const IMAGE_NT_HEADERS32*>(image.data()+dos->e_lfanew);
 auto* mapped=static_cast<unsigned char*>(VirtualAlloc(reinterpret_cast<void*>(ORIGINAL),0x300000,MEM_RESERVE|MEM_COMMIT,PAGE_EXECUTE_READWRITE));if(address(mapped)!=ORIGINAL)return 4;
 std::memcpy(mapped,image.data(),pe->OptionalHeader.SizeOfHeaders);const auto* section=IMAGE_FIRST_SECTION(pe);
 for(unsigned i=0;i<pe->FileHeader.NumberOfSections;++i)std::memcpy(mapped+section[i].VirtualAddress,image.data()+section[i].PointerToRawData,section[i].SizeOfRawData);
 const auto directory=pe->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];U position=0;
 while(position<directory.Size){const auto* block=reinterpret_cast<const IMAGE_BASE_RELOCATION*>(mapped+directory.VirtualAddress+position);if(!block->SizeOfBlock)break;const auto* entries=reinterpret_cast<const unsigned short*>(block+1);for(U i=0;i<(block->SizeOfBlock-8)/2;++i){if((entries[i]>>12)==IMAGE_REL_BASED_HIGHLOW){U value;auto* cell=mapped+block->VirtualAddress+(entries[i]&0xfff);std::memcpy(&value,cell,4);value+=ORIGINAL-pe->OptionalHeader.ImageBase;std::memcpy(cell,&value,4);}else if(entries[i]>>12)return 7;}position+=block->SizeOfBlock;}
 if(VirtualAlloc(arena,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=arena)return 5;
 std::string data;
 while(std::cin>>op>>a>>b>>c>>d>>decimal>>control>>prefix>>data){
  std::vector<unsigned char> payload;for(std::size_t i=0;i<data.size();i+=2)payload.push_back(static_cast<unsigned char>(std::stoul(data.substr(i,2),nullptr,16)));if(op>15||payload.size()>512)return 6;
  std::printf("{\"recovered\":");execute(false,payload);std::printf(",\"original\":");execute(true,payload);
  BCRYPT_ALG_HANDLE algorithm=nullptr;BCRYPT_HASH_HANDLE hash=nullptr;unsigned char digest[32];
  if(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0||BCryptCreateHash(algorithm,&hash,nullptr,0,nullptr,0,0)<0)std::abort();
  if(!porsche::float_trace.empty()&&BCryptHashData(hash,porsche::float_trace.data(),static_cast<U>(porsche::float_trace.size()),0)<0)std::abort();
  if(BCryptFinishHash(hash,digest,32,0)<0)std::abort();BCryptDestroyHash(hash);BCryptCloseAlgorithmProvider(algorithm,0);
  std::printf(",\"stage_events\":%u,\"stage_sha256\":\"%s\"}\n",porsche::float_trace_events,hex(digest,32).c_str());
 }
}
