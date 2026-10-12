#include "porsche/formatter_float_parse.hpp"
#include "porsche/formatter_crt_runtime.hpp"
#include <Windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

namespace {
using U=std::uint32_t;
constexpr U BASE=0x24000000,ORIGINAL=0x30000000;
U seq,op,a,b,c,d,e,width,decimal,control,prefix,variant;
bool original_mode;U class_calls;std::string events;
std::vector<unsigned char> stages;
unsigned char* arena=reinterpret_cast<unsigned char*>(BASE);
unsigned char* mapped=reinterpret_cast<unsigned char*>(ORIGINAL);
const U vas[]={0x5ac716,0x5abb07,0x5ab90d,0x5ab956,0x5ab9ac,0x5aba38,0x5aba53,0x5aba5f,0x5aba7a,0x5adb88,0x5abc9f,0x5abccc};
U address(const void* p) {return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(const void* p) {U v;std::memcpy(&v,p,4);return v;}
void put(void* p,U v) {std::memcpy(p,&v,4);}
std::string hx(U v) {char out[12];std::snprintf(out,sizeof(out),"%08x",v);return out;}
std::string hex(const void* data,unsigned n) {const auto* p=static_cast<const unsigned char*>(data);const char* digits="0123456789abcdef";std::string out;for(unsigned i=0;i<n;++i){out+=digits[p[i]>>4];out+=digits[p[i]&15];}return out;}
U* original_cell(U va) {return reinterpret_cast<U*>(mapped+va-0x400000);}
}
namespace porsche {
void formatter_float_parse_trace(U tag,U phase,const void* data,U bytes) {
    const U header[]={tag,phase,bytes};const auto* h=reinterpret_cast<const unsigned char*>(header);const auto* p=static_cast<const unsigned char*>(data);
    stages.insert(stages.end(),h,h+12);stages.insert(stages.end(),p,p+bytes);
}
const std::uint8_t* formatter_ctype_table_005e52d0;
int __cdecl formatter_float_classify_005a2eae(int value,int mask) {
    const auto* table=original_mode?reinterpret_cast<const std::uint8_t*>(*original_cell(0x5e52d0)):formatter_ctype_table_005e52d0;
    const int result=table[static_cast<U>(value)*2]&mask;
    events+="class:"+hx(static_cast<U>(value))+':'+hx(static_cast<U>(mask))+':'+hx(static_cast<U>(result))+';';
    if((variant&2) && ++class_calls==1) {
        if(original_mode) {*original_cell(0x5e54dc)=1;*original_cell(0x5e54e0)=',';*original_cell(0x5e52d0)=BASE+0x1200;}
        else {formatter_float_character_width_005e54dc=1;formatter_float_decimal_word_005e54e0=',';formatter_ctype_table_005e52d0=arena+0x1200;}
    }
    return result;
}
// Unused canonical translation-unit paths must never become conversion substitutes.
const std::uint8_t formatter_crt_signal_table_005e5ec8[1]{};
int formatter_float_lower_005a2248(int) {std::abort();}
void* __stdcall formatter_dialog_load_library(const char*) {std::abort();}
void* __stdcall formatter_dialog_get_proc_address(void*,const char*) {std::abort();}
[[noreturn]] void __cdecl formatter_fatal_005a2e22(int) {std::abort();}
void __stdcall formatter_lowio_critical_initialize(void*) {std::abort();}
void __stdcall formatter_lowio_critical_enter(void*) {std::abort();}
void __stdcall formatter_lowio_critical_leave(void*) {std::abort();}
void* __cdecl formatter_crt_small_allocate_005aad00(U) {std::abort();}
void __cdecl formatter_crt_small_free_005aa9d5(std::uint8_t*,void*) {std::abort();}
void* __stdcall formatter_crt_heap_allocate(U,U,U) {std::abort();}
int __stdcall formatter_crt_heap_free(U,U,void*) {std::abort();}
U __stdcall formatter_crt_tls_allocate() {std::abort();}
void* __stdcall formatter_crt_tls_get(U) {std::abort();}
int __stdcall formatter_crt_tls_set(U,void*) {std::abort();}
U __stdcall formatter_crt_get_last_error() {std::abort();}
void __stdcall formatter_crt_set_last_error(U) {std::abort();}
U __stdcall formatter_crt_thread_id() {std::abort();}
}
namespace {
__declspec(noinline) U invoke(const void* function,U count,const U* args) {
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
    if(before!=after || saved_bx!=0x12345678 || saved_si!=0x12345678 || saved_di!=0x12345678 || (flags&0x400))std::abort();
    return result;
}
void reset_fpu() {
    const unsigned short cw=static_cast<unsigned short>(control);const double value=7.25;
    __asm {fninit}
    for(int i=0;i<8;++i) {__asm {fldz}}
    __asm {fninit}
    __asm {fldcw cw}
    for(U i=0;i<prefix;++i) {__asm {fld qword ptr [value]}}
}
void execute(bool original,const std::vector<unsigned char>& payload,const std::vector<unsigned char>& ctype) {
    using namespace porsche;
    original_mode=original;events.clear();class_calls=0;
    if(!original)stages.clear();
    for(U i=0;i<8192;++i)arena[i]=static_cast<unsigned char>(i*13+seq*7+0x21);
    std::memcpy(arena+0x100,payload.data(),payload.size());
    std::memcpy(arena+0x1000,ctype.data(),512);std::memcpy(arena+0x1200,ctype.data(),512);
    if(variant&1) {arena[0x1000+'?'*2]|=4;arena[0x1000+255*2]|=4;arena[0x1200+'?'*2]|=4;}
    formatter_float_character_width_005e54dc=static_cast<int>(width);formatter_float_decimal_word_005e54e0=decimal;formatter_ctype_table_005e52d0=arena+0x1000;
    *original_cell(0x5e54dc)=width;*original_cell(0x5e54e0)=decimal;*original_cell(0x5e52d0)=BASE+0x1000;
    U args[7]{};U count=0;
    const void* functions[]={reinterpret_cast<const void*>(formatter_float_parse_words_005ac716),reinterpret_cast<const void*>(formatter_float_pack_words_005abb07),
        reinterpret_cast<const void*>(formatter_float_tail_zero_005ab90d),reinterpret_cast<const void*>(formatter_float_bump_bit_005ab956),
        reinterpret_cast<const void*>(formatter_float_round_words_005ab9ac),reinterpret_cast<const void*>(formatter_float_copy_words_005aba38),
        reinterpret_cast<const void*>(formatter_float_zero_words_005aba53),reinterpret_cast<const void*>(formatter_float_words_zero_005aba5f),
        reinterpret_cast<const void*>(formatter_float_shift_words_005aba7a),reinterpret_cast<const void*>(formatter_float_digits_words_005adb88),
        reinterpret_cast<const void*>(formatter_float_parse64_005abc9f),reinterpret_cast<const void*>(formatter_float_parse32_005abccc)};
    if(op==0) {args[0]=BASE+0x800;args[1]=BASE+0xc00;args[2]=BASE+0x100;args[3]=a;args[4]=b;args[5]=c;args[6]=d;count=7;}
    else if(op==1) {
        const auto* config=a==32?formatter_float_pack32_config_005e6140:formatter_float_pack64_config_005e6128;
        std::memcpy(arena+0x500,config,24);put(arena+0x510,a);
        args[0]=BASE+0x100;args[1]=BASE+0x800;args[2]=BASE+0x500;count=3;
    } else if(op>=2 && op<=4 || op==8) {args[0]=BASE+0x100;args[1]=a;count=2;}
    else if(op==5) {args[0]=BASE+0x100+a;args[1]=BASE+0x100;count=2;}
    else if(op==6 || op==7) {args[0]=BASE+0x100;count=1;}
    else if(op==9) {args[0]=BASE+0x100;args[1]=a;args[2]=BASE+0x800;count=3;}
    else {args[0]=BASE+0x800;args[1]=BASE+0x100;count=2;}
    reset_fpu();const U result=invoke(original?mapped+vas[op]-0x400000:functions[op],count,args);
    unsigned char fpu[108];__asm {fnsave fpu}
    const bool meaningful=op<=4 || op==7 || op>=10;
    const U final_width=original?*original_cell(0x5e54dc):static_cast<U>(formatter_float_character_width_005e54dc);
    const U final_decimal=original?*original_cell(0x5e54e0):formatter_float_decimal_word_005e54e0;
    const U final_table=original?*original_cell(0x5e52d0):address(formatter_ctype_table_005e52d0);
    std::printf("{\"case\":%u,\"result\":\"%08x\",\"events\":\"%s\",\"width\":\"%08x\",\"decimal\":\"%08x\",\"ctype\":\"%08x\",\"memory\":\"%s\",\"fpu\":\"%s%s%s%s\"}",
        seq,meaningful?result:0,events.c_str(),final_width,final_decimal,final_table,hex(arena,8192).c_str(),hex(fpu,2).c_str(),hex(fpu+4,2).c_str(),hex(fpu+8,2).c_str(),hex(fpu+28,80).c_str());
}
}
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    std::ifstream file(argv[1],std::ios::binary);std::vector<unsigned char> image((std::istreambuf_iterator<char>(file)),{});if(image.size()<0x100)return 3;
    const auto* dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(image.data());const auto* pe=reinterpret_cast<const IMAGE_NT_HEADERS32*>(image.data()+dos->e_lfanew);
    if(pe->Signature!=IMAGE_NT_SIGNATURE || pe->FileHeader.Machine!=IMAGE_FILE_MACHINE_I386)return 4;
    if(VirtualAlloc(mapped,0x300000,MEM_RESERVE|MEM_COMMIT,PAGE_EXECUTE_READWRITE)!=mapped)return 5;
    std::memcpy(mapped,image.data(),pe->OptionalHeader.SizeOfHeaders);const auto* section=IMAGE_FIRST_SECTION(pe);
    for(unsigned i=0;i<pe->FileHeader.NumberOfSections;++i)std::memcpy(mapped+section[i].VirtualAddress,image.data()+section[i].PointerToRawData,section[i].SizeOfRawData);
    const auto directory=pe->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];U position=0;
    while(position<directory.Size) {
        const auto* block=reinterpret_cast<const IMAGE_BASE_RELOCATION*>(mapped+directory.VirtualAddress+position);if(!block->SizeOfBlock)break;
        const auto* entries=reinterpret_cast<const unsigned short*>(block+1);
        for(U i=0;i<(block->SizeOfBlock-8)/2;++i) {
            if((entries[i]>>12)==IMAGE_REL_BASED_HIGHLOW) {auto* cell=mapped+block->VirtualAddress+(entries[i]&0xfff);put(cell,get(cell)+ORIGINAL-pe->OptionalHeader.ImageBase);}
            else if(entries[i]>>12)return 6;
        }
        position+=block->SizeOfBlock;
    }
    const auto* source_ctype=reinterpret_cast<const unsigned char*>(*original_cell(0x5e52d0));
    std::vector<unsigned char> ctype(source_ctype,source_ctype+512);
    // Only this explicit canonical classification boundary is redirected.
    auto* jump=mapped+0x5a2eae-0x400000;jump[0]=0xe9;put(jump+1,address(reinterpret_cast<const void*>(porsche::formatter_float_classify_005a2eae))-address(jump)-5);
    FlushInstructionCache(GetCurrentProcess(),mapped,0x300000);
    if(VirtualAlloc(arena,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=arena)return 7;
    std::string data;
    while(std::cin>>std::dec>>seq>>op>>std::hex>>a>>b>>c>>d>>e>>width>>decimal>>control>>prefix>>variant>>data) {
        if(op>11 || data.size()>1024)return 8;
        std::vector<unsigned char> payload;for(std::size_t i=0;i<data.size();i+=2)payload.push_back(static_cast<unsigned char>(std::stoul(data.substr(i,2),nullptr,16)));
        std::printf("{\"recovered\":");execute(false,payload,ctype);std::printf(",\"original\":");execute(true,payload,ctype);std::printf(",\"stages\":\"%s\"}\n",hex(stages.data(),static_cast<U>(stages.size())).c_str());
    }
}
