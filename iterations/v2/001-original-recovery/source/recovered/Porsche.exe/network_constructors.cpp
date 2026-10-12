#include "porsche/network_constructors.hpp"
#include "porsche/network_groups.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/formatter_bootstrap.hpp"
#include "porsche/formatter_entry.hpp"
#include <cstring>
namespace porsche {
const std::uint32_t network_connection_port_005b4990=0x24e2;
namespace {
using U=std::uint32_t;
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U raw(const void*p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(const void*p,U off=0){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+off,4);return v;}
void put(void*p,U off,U v){std::memcpy(static_cast<std::uint8_t*>(p)+off,&v,4);}
U byte(const void*p,U off){return static_cast<const std::uint8_t*>(p)[off];}
void pb(void*p,U off,U v){static_cast<std::uint8_t*>(p)[off]=static_cast<std::uint8_t>(v);}
// Original SCASB then forward MOVSD/MOVSB, including the terminator. Unbounded
// copies preserve original preconditions; no clamp or invented failure path.
void copy_string(char* out,const char* in){U n=0;while(in[n])++n;++n;U i=0;for(;i+4<=n;i+=4)put(out,i,get(in,i));for(;i<n;++i)out[i]=in[i];}
void append(char*out,const char*in){while(*out)++out;copy_string(out,in);}
void* sentinel(U kind,U offset){
 auto* pool=static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8())+0x28;
 heap_enter_005322b0(ptr(get(pool)));if(!get(pool,offset))application_context_new_head_0059eeb0(kind,0);
 void* node=ptr(get(pool,offset));put(pool,offset,get(node,4));heap_leave_005322c0(ptr(get(pool)));return node;
}
using ProviderTriple=U (__cdecl*)(U,U,U,U);
using ProviderCompare=U (__cdecl*)(U,const void*,const void*);
}
// 0048aa10..0048ac44, thiscall RET32. Native table ownership replaces only
// relocated pointer words; callbacks observe both original initialization stages.
void* __fastcall network_client_construct_0048aa10(void* object,void*,U first,U second,U third,const char* left,const char* right,const char* suffix,const char* left_suffix,U last){
 put(object,8,raw(heap_lock_create_005321f0()));put(object,0,raw(&network_vtable_owner_005b4970.send));
 void* node=sentinel(31,0x88);put(object,0xc,raw(node));put(node,0,raw(node));node=ptr(get(object,0xc));put(node,4,raw(node));
 pb(object,0x10,1);pb(object,0x11,0);put(object,0,raw(&network_vtable_owner_005b4968.send));
 char packet[92];heap_fill_0053c290(packet,0,92);copy_string(packet+20,left);
 if(*left_suffix){append(packet+20,"~");append(packet+20,left_suffix);}
 copy_string(packet+72,right);if(packet[72])append(packet+72,"~");append(packet+72,"3.5");
 if(*suffix){append(packet+72,"~");append(packet+72,suffix);}
 put(object,4,raw(network_client_worker_construct_0055c370(second,first,network_connection_identity_005b4980,packet,third,last)));return object;
}
// 0048af80..0048b1b5, thiscall RET28. Failed worker creation retries once;
// address consumers still run when requested, with no added null guard.
void* __fastcall network_host_construct_0048af80(void* object,void*,U first,U second,U query,U fourth,const void* settings,const char* server,U port){
 put(object,8,raw(heap_lock_create_005321f0()));put(object,0,raw(&network_vtable_owner_005b4970.send));put(object,0xc,0);put(object,0x10,0);
 pb(object,0x14,0);pb(object,0x15,0);pb(object,0x16,0);void* node=sentinel(1,0x10);put(object,0x18,raw(node));put(node,0,raw(node));node=ptr(get(object,0x18));put(node,4,raw(node));
 put(object,0x1c,query);put(object,0x20,first);put(object,0x24,fourth);put(object,0,raw(&network_vtable_owner_005b4978.send));
 char bytes[52];heap_fill_0053c290(bytes,0,52);if(settings)heap_copy_dispatch_005323e0(bytes,settings,52);else copy_string(bytes,"NfsNet");
 if(query)port=network_connection_port_005b4990;
 put(object,4,raw(network_host_worker_construct_0055aaa0(second,first,network_connection_identity_005b4980,bytes,fourth,port,0)));
 if(!get(object,4))put(object,4,raw(network_host_worker_construct_0055aaa0(second,first,network_connection_identity_005b4980,bytes,fourth,0,0)));
 pb(object,0x16,1);
 if(query){
  U first_address[5],second_address[5];char address[32];
  network_address_current_0055d650(ptr(get(object,4)),first_address);
  network_address_get_0055d5a0(ptr(get(object,4)),first_address,address,&port);
  copy_string(static_cast<char*>(object)+0x128,server?server:"porsche-entry.earacing.com");
  network_address_parse_0055d5e0(ptr(get(object,4)),static_cast<char*>(object)+0x128,network_connection_port_005b4990,second_address);
  if(network_address_equal_0055d6e0(ptr(get(object,4)),first_address,second_address))pb(object,0x14,1);else pb(object,0x15,1);
  formatter_entry_005a0fbf(static_cast<char*>(object)+0x28,"%c%s.%d.%s",byte(object,0x14)?'p':'s',address,port,bytes);
 }
 return object;
}
namespace {
void start_client(void* object){
 void* value=startup_network_allocate_0059ef90(20);
 if(value)value=network_client_construct_0048aa10(value,nullptr,get(object,0x20),get(object,0x1c),get(object,0x24),static_cast<char*>(object)+0x28,network_group_text_005e8e50,network_group_text_005e8e50,network_group_text_005e8e50,0);
 put(object,0xc,raw(value));network_client_connect_0048ac90(ptr(get(object,0xc)),nullptr,static_cast<char*>(object)+0x128,network_connection_port_005b4990);
 value=startup_network_allocate_0059ef90(8);if(value){put(value,4,0);put(value,0,get(object,0xc));}put(object,0x10,raw(value));
}
}
void __fastcall network_host_start_client_0048b3c0(void* object,void*){if(get(object,0xc)||!byte(object,0x14))return;start_client(object);}
void __fastcall network_host_restart_client_0048b450(void* object,void*){if(!byte(object,0x15))return;if(!get(object,0xc))start_client(object);pb(object,0x15,0);}
U __cdecl network_address_provider_mode_0055d730(void* worker){return get(worker,0xbc)>3u?1:0;}
U __cdecl network_address_text_mode_0055d750(void* worker){return get(worker,0xbc)==1u?1:0;}
U __cdecl network_address_get_0055d5a0(void* worker,void* first,void* second,void* third){
 if(!network_address_provider_mode_0055d730(worker))return 0;
 return network_address_get_dispatch_005805e0(static_cast<std::uint8_t*>(worker)+8,raw(first),raw(second),raw(third));
}
U __cdecl network_address_parse_0055d5e0(void* worker,const char* text,U port,void* output){
 if(network_address_provider_mode_0055d730(worker))return network_address_parse_dispatch_005805b0(static_cast<std::uint8_t*>(worker)+8,raw(text),port,raw(output));
 if(!network_address_text_mode_0055d750(worker))return 0;
 formatter_error_copy_n_005a28a0(static_cast<char*>(output),text,19);pb(output,19,0);return 1;
}
U __cdecl network_address_equal_0055d6e0(void* worker,const void* first,const void* second){
 if(network_address_provider_mode_0055d730(worker))return network_address_compare_dispatch_00580590(static_cast<std::uint8_t*>(worker)+8,first,second);
 for(U i=0;i<5;++i)if(get(first,i*4)!=get(second,i*4))return 0;return 1;
}
U __cdecl network_address_compare_dispatch_00580590(void* receiver,const void* first,const void* second){
 void* table=ptr(get(receiver,0xc));auto callback=reinterpret_cast<ProviderCompare>(static_cast<std::uintptr_t>(get(table,0x40)));return callback(get(receiver,0x10),first,second);
}
U __cdecl network_address_parse_dispatch_005805b0(void* receiver,U first,U second,U third){
 void* table=ptr(get(receiver,0xc));const U target=get(table,0x38);if(!target)return 0;return reinterpret_cast<ProviderTriple>(static_cast<std::uintptr_t>(target))(get(receiver,0x10),first,second,third);
}
U __cdecl network_address_get_dispatch_005805e0(void* receiver,U first,U second,U third){
 void* table=ptr(get(receiver,0xc));const U target=get(table,0x3c);if(!target)return 0;return reinterpret_cast<ProviderTriple>(static_cast<std::uintptr_t>(target))(get(receiver,0x10),first,second,third);
}
}
