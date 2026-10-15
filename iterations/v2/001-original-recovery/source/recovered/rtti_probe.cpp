#include "porsche/rtti.hpp"
#include "porsche/exit_registry.hpp"
#include "porsche/formatter_crt_runtime.hpp"
#include "porsche/application_alloc.hpp"
#include <windows.h>
#include <array>
#include <cstring>
#include <iostream>
#include <map>
#include <sstream>
#include <vector>
namespace porsche {namespace {
using U=std::uint32_t;constexpr U B=0x23000000,O=B,L=B+0x1000,H=B+0x1100,A=B+0x1200,D=B+0x2000,T=B+0x3000,P=B+0x4000,V=B+0x5000,VB=B+0x6000,STR=B+0x7000;
std::array<U,12>a{};U op,object;std::map<U,U>mapping;std::vector<std::vector<U>>events;
void* ptr(U p){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(p));}U raw(const void*p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}U get(U p){U v;std::memcpy(&v,ptr(p),4);return v;}void put(U p,U v){std::memcpy(ptr(p),&v,4);}
U norm(U p){auto it=mapping.find(p);return it==mapping.end()?p:it->second;}
void event(U id,U arg){events.push_back({id,norm(arg),norm(get(object)),get(object+4)});}
void add(U address,const void*p){mapping[raw(p)]=address;}
void setup_mapping(){mapping.clear();add(0x5c18f4,&rtti_type_info_table_005c18f8);add(0x5c18f8,&rtti_type_info_table_005c18f8.destructor);add(0x5a103a,reinterpret_cast<const void*>(&rtti_type_info_delete_005a103a));
 for(auto pair:{std::pair<U,const RttiCompleteObjectLocator*>{0x5c98d0,&rtti_type_info_locator_005c98d0},{0x5c5190,&network_rtti_005c5190},{0x5c51d8,&network_rtti_005c51d8},{0x5c5228,&network_rtti_005c5228}})add(pair.first,pair.second);
 add(0x5e51c0,&rtti_type_info_005e51c0);add(0x5d0630,&rtti_client_type_005d0630);add(0x5d0650,&rtti_connection_type_005d0650);add(0x5d0690,&rtti_host_type_005d0690);
 const RttiCompleteObjectLocator*cols[]={&rtti_type_info_locator_005c98d0,&network_rtti_005c5190,&network_rtti_005c51d8,&network_rtti_005c5228};const U hs[]={0x5c98c0,0x5c5180,0x5c51c8,0x5c5218},arrays[]={0x5c98b8,0x5c5170,0x5c51c0,0x5c5208};const U bases[][2]={{0x5c98a0,0},{0x5c5158,0x5c51a8},{0x5c51a8,0},{0x5c51f0,0x5c51a8}};
 for(U i=0;i<4;++i){add(hs[i],cols[i]->hierarchy);add(arrays[i],cols[i]->hierarchy->bases);for(U j=0;j<cols[i]->hierarchy->count;++j)add(bases[i][j],cols[i]->hierarchy->bases[j]);}
}
const RttiCompleteObjectLocator* canonical_col(){return a[1]%3==0?&network_rtti_005c5190:a[1]%3==1?&network_rtti_005c51d8:&network_rtti_005c5228;}
const RttiTypePrefix*canonical_type(U index){return index%3==0?&rtti_client_type_005d0630.prefix:index%3==1?&rtti_connection_type_005d0650.prefix:&rtti_host_type_005d0690.prefix;}
void init(){std::memset(ptr(B),0xcc,0x10000);events.clear();setup_mapping();
 for(auto*type:{&rtti_type_info_005e51c0.prefix,&rtti_client_type_005d0630.prefix,&rtti_connection_type_005d0650.prefix,&rtti_host_type_005d0690.prefix}){type->vptr=&rtti_type_info_table_005c18f8.destructor;type->cached_name=nullptr;}
 object=op==8?raw(&rtti_client_type_005d0630):O;put(object,0x12345678);put(object+4,a[7]?0x26000000:0);put(O+0x20,VB);
 put(V,L);put(V+4,0);put(O,V+4);if(op==8)put(object,raw(&rtti_type_info_table_005c18f8.destructor));
 for(U i=0;i<5;++i)put(L+i*4,0);put(L+4,a[3]);put(L+8,a[6]&4?0x10:0);put(O+0x30,a[2]);put(O+0x40,V+4);put(L+0x10,H);put(H+8,a[0]);put(H+0xc,A);
 for(U i=0;i<8;++i){put(A+i*4,D+i*0x40);put(D+i*0x40,T+(i%4)*0x100);U remain=i<a[0]?a[0]-i-1:0;put(D+i*0x40+4,a[5]==0?0:a[5]==1?(remain?1:0):a[5]==2?(remain<3?remain:3):remain);put(D+i*0x40+8,a[6]&2?0:i*4);put(D+i*0x40+12,a[6]&1?0x20:0xffffffff);put(D+i*0x40+16,i*4);put(D+i*0x40+20,(a[4]>>(i*2))&3);put(VB+i*4,i*8);}
 const char*names[]={".?AVA@@",".?AVB@@",".?AVC@@",".?AVA@@"};for(U i=0;i<4;++i){put(T+i*0x100,0);put(T+i*0x100+4,0);std::strcpy(static_cast<char*>(ptr(T+i*0x100+8)),names[i]);}
 put(P,a[3]);put(P+4,a[6]&1?0x20:0xffffffff);put(P+8,a[2]*4);
 std::memset(ptr(STR),'a',64);std::memset(ptr(STR+0x100),'a',64);*static_cast<char*>(ptr(STR+(a[11]&3)+a[10]))=0;*static_cast<char*>(ptr(STR+0x100+((a[11]>>2)&3)+a[10]))=0;
 if(a[9]&4)*static_cast<unsigned char*>(ptr(STR+0x100+((a[11]>>2)&3)+(a[10]?a[10]-1:0)))=0xff;
 if(a[9]&8)*static_cast<unsigned char*>(ptr(STR+0x100+((a[11]>>2)&3)+(a[10]?a[10]-1:0)))=0;
 if(op==9)put(V,raw(canonical_col()));
}
}
void __cdecl exit_registry_lock_api_005a4ba4(U id){event(0x5a4ba4,id);if(a[9]&1)put(object+4,0x26000010);}
void __cdecl exit_registry_unlock_api_005a4c05(U id){event(0x5a4c05,id);}
void __cdecl formatter_crt_free_005a3b9d(void*p){event(0x5a3b9d,raw(p));if(a[9]&2)put(object+4,0x26000020);}
U __cdecl application_release_0059f050(void*p){event(0x59f050,raw(p));return 0x87654321;}
int main(){if(VirtualAlloc(ptr(B),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=ptr(B))return 2;std::string line;
 while(std::getline(std::cin,line)){std::istringstream in(line);in>>op;for(auto&v:a)in>>v;init();U result=0;
 auto col=static_cast<const RttiCompleteObjectLocator*>(ptr(L));auto source=static_cast<const RttiTypePrefix*>(ptr(T+(a[2]%4)*0x100));auto target=static_cast<const RttiTypePrefix*>(ptr(T+(a[1]%4)*0x100));
 switch(op){case 0:rtti_type_info_destroy_005a1011(ptr(object),nullptr);break;case 1:result=raw(rtti_type_info_delete_005a103a(ptr(object),nullptr,a[8]));break;case 2:result=raw(rtti_complete_object_005a14b3(ptr(O+0x40)));break;
 case 3:result=raw(rtti_find_single_005a14cd(ptr(O),col,source,a[3],target));break;case 4:result=raw(rtti_find_multiple_005a1527(ptr(O),col,source,a[3],target));break;case 5:result=raw(rtti_find_virtual_005a1620(ptr(O),col,source,a[3],target));break;
 case 6:result=rtti_pmd_offset_005a1758(ptr(O),static_cast<const RttiPmd*>(ptr(P)));break;case 7:result=static_cast<U>(rtti_compare_names_005a4c20(static_cast<const char*>(ptr(STR+(a[11]&3))),static_cast<const char*>(ptr(STR+0x100+((a[11]>>2)&3)))));break;
 case 8:result=raw(rtti_type_info_table_005c18f8.destructor(ptr(object),nullptr,a[8]));break;case 9:result=raw(rtti_complete_object_005a14b3(ptr(O)));break;
 case 10:result=raw(rtti_find_single_005a14cd(ptr(O),canonical_col(),canonical_type(a[2]),0,canonical_type(a[10])));break;
 case 11:result=raw(rtti_find_multiple_005a1527(ptr(O),canonical_col(),canonical_type(a[2]),0,canonical_type(a[10])));break;
 case 12:result=raw(rtti_find_virtual_005a1620(ptr(O),canonical_col(),canonical_type(a[2]),0,canonical_type(a[10])));break;}
 std::cout<<"{\"return\":"<<norm(result)<<",\"trace\":[";for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';}std::cout<<"],\"state\":[";
 bool first=true;for(auto range:{std::pair<U,U>{O,0x100},{D,0x200},{P,12}})for(U i=0;i<range.second;i+=4){if(!first)std::cout<<',';first=false;std::cout<<norm(get(range.first+i));}
 std::cout<<"],\"graph\":[";first=true;
 // Inventory order sorted by original VA, excluding unproven alignment padding.
 std::map<U,std::pair<U,U>>records;for(auto item:mapping){U n=0;switch(item.second){case 0x5c18f4:n=8;break;case 0x5c98d0:case 0x5c5190:case 0x5c51d8:case 0x5c5228:n=20;break;case 0x5c98c0:case 0x5c5180:case 0x5c51c8:case 0x5c5218:n=16;break;case 0x5c98b8:case 0x5c51c0:n=4;break;case 0x5c5170:case 0x5c5208:n=8;break;case 0x5c98a0:case 0x5c5158:case 0x5c51a8:case 0x5c51f0:case 0x5e51c0:n=24;break;case 0x5d0630:n=25;break;case 0x5d0650:n=26;break;case 0x5d0690:n=23;break;}if(n)records[item.second]={item.first,n};}
 for(auto rec:records){std::vector<unsigned char>bytes(rec.second.second);std::memcpy(bytes.data(),ptr(rec.second.first),bytes.size());for(U i=0;i+4<=bytes.size();i+=4){
  bool pointer_field=false;switch(rec.first){case 0x5c18f4:case 0x5c98b8:case 0x5c5170:case 0x5c51c0:case 0x5c5208:pointer_field=true;break;
  case 0x5c98d0:case 0x5c5190:case 0x5c51d8:case 0x5c5228:pointer_field=i==12||i==16;break;
  case 0x5c98c0:case 0x5c5180:case 0x5c51c8:case 0x5c5218:pointer_field=i==12;break;default:pointer_field=i==0;break;}
  if(pointer_field){U word;std::memcpy(&word,bytes.data()+i,4);word=norm(word);std::memcpy(bytes.data()+i,&word,4);}
 }for(auto b:bytes){if(!first)std::cout<<',';first=false;std::cout<<static_cast<U>(b);}}
 std::cout<<"]}\n";
 }VirtualFree(ptr(B),0,MEM_RELEASE);return 0;}
}
int main(){return porsche::main();}
