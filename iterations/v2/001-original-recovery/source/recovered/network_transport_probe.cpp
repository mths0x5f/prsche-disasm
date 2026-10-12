#include "porsche/network_transport.hpp"
#include "porsche/files.hpp"
#include "porsche/heap.hpp"
#include <windows.h>
#include <array>
#include <cstring>
#include <iostream>
#include <sstream>
#include <vector>
namespace porsche {
namespace {
using U=std::uint32_t;constexpr U B=0x23000000,S=B,V=B+0x100,R=B+0x1000,N=B+0x2000,D=B+0x4000,SRC=B+0x10000;
std::array<U,11>a{};U op,copy_count;std::vector<std::vector<U>>events;
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U raw(const void*p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(U p){U v;std::memcpy(&v,ptr(p),4);return v;}
void put(U p,U v){std::memcpy(ptr(p),&v,4);}
U norm(U p){return p>=B&&p<B+0x20000?p:0;}
void event(U id,std::initializer_list<U>args={}){std::vector<U>row{id};row.insert(row.end(),args);for(U v:{get(R),get(R+8),get(R+0x18),get(R+0x1c),get(D+4),get(D+16)})row.push_back(v);events.push_back(row);}
U __cdecl buffer(void* context,const void* bytes,U packed){
 std::vector<U>row{0x24000000,raw(context),norm(raw(bytes)),packed};auto*p=static_cast<const unsigned char*>(bytes);row.insert(row.end(),p,p+(packed&0xffffffu));events.push_back(row);event(0x24000001);
 if(a[6]&16)put(R+0x18,0x26001111);return a[7];
}
U __cdecl control_base(void* context,const void* bytes,U size){return buffer(context,bytes,size);}
U route(U id,void* context,U provider,U count,U* descriptors,void* routes){
 std::vector<U>row{id,raw(context),provider,count,raw(routes)};row.insert(row.end(),descriptors,descriptors+count*3);events.push_back(row);event(0x24000001);
 if(a[6]&16)put(R+0x18,0x26001111);
 if(!a[8])return a[7];
 U stage=get(R+0x1c);
 if(id==0x24000010){descriptors[count*3]=0x40000000;descriptors[count*3+1]=3;descriptors[count*3+2]=SRC+0x7000;return network_transport_stage_00587110(context,stage-1u,count+1,descriptors,routes);}
 return network_transport_control_00586ee0(context,stage+1,count,descriptors,routes);
}
U __cdecl route_send(void*c,U p,U n,U*d,void*r){return route(0x24000010,c,p,n,d,r);}
U __cdecl route_control(void*c,U p,U n,U*d,void*r){return route(0x24000020,c,p,n,d,r);}
U __cdecl predicate(void* node,U target){event(0x24000030,{raw(node),target});if(a[6]&32)put(raw(node),0);return raw(node)==target?a[7]:0;}
std::int32_t __cdecl io_predicate(IoNode* node,U target){return static_cast<std::int32_t>(predicate(node,target));}
void init(){
 std::memset(ptr(B),0xcc,0x20000);events.clear();copy_count=0;
 put(S+8,V);put(V+8,raw(reinterpret_cast<void*>(&buffer)));put(S+0x24,raw(reinterpret_cast<void*>(&control_base)));
 put(R,a[3]);put(R+8,a[5]?N:0);put(R+0x18,0x26000000);put(R+0x1c,0x12345678);put(R+0x10,raw(reinterpret_cast<void*>(&predicate)));put(R+0x14,a[9]<4?N+a[9]*0x40:0);
 for(U i=0;i<4;++i){U n=N+i*0x40;put(n,i+1<a[5]?n+0x40:0);put(n+4,raw(reinterpret_cast<void*>(&route_send)));put(n+8,raw(reinterpret_cast<void*>(&route_control)));put(n+0xc,0x81000000+i);}
 for(U i=0;i<12;++i){put(D+i*12,a[2]^(i<<24));put(D+i*12+4,a[1]+i);put(D+i*12+8,SRC+(i%4)*0x2000);}
 for(U i=0;i<0x8000;++i)*static_cast<unsigned char*>(ptr(SRC+i))=static_cast<unsigned char>(0x21+i*7);
}
}
void __cdecl heap_enter_005322b0(void*h){event(0x5322b0,{raw(h)});if(a[6]&1)put(R+8,get(N));if(a[6]&2)put(R+0x18,0x26001000);}
void __cdecl heap_leave_005322c0(void*h){event(0x5322c0,{raw(h)});if(a[6]&4)put(R+8,0);}
void __cdecl heap_copy_dispatch_005323e0(void*d,const void*s,U n){event(0x5323e0,{norm(raw(d)),norm(raw(s)),n});std::memcpy(d,s,n);if(!copy_count++&&(a[6]&8)){put(D+20,SRC+0x6000);}}
int main(){if(VirtualAlloc(ptr(B),0x20000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=ptr(B))return 2;
 std::string line;while(std::getline(std::cin,line)){std::istringstream in(line);in>>op;for(auto&v:a)in>>v;init();U result=0;U count=a[0],stage=a[4];
 switch(op){
 case 0:result=network_transport_direct_00587000(ptr(S),count,static_cast<U*>(ptr(D)));break;
 case 1:result=network_transport_routed_005870b0(ptr(S),count,static_cast<U*>(ptr(D)),R);break;
 case 2:result=network_transport_stage_00587110(ptr(S),stage,count,static_cast<U*>(ptr(D)),ptr(R));break;
 case 3:result=raw(network_route_at_00580b20(ptr(R),stage));break;
 case 4:result=raw(network_route_next_00580b70(ptr(N),stage));break;
 case 5:result=network_route_index_00580a00(ptr(R),a[9]<4?ptr(N+a[9]*0x40):nullptr);break;
 case 6:result=network_route_first_value_00580a50(ptr(R));break;
 case 7:result=raw(io_find_00580ad0(static_cast<IoList*>(ptr(R)),a[10]?io_predicate:nullptr,a[9]<4?N+a[9]*0x40:0));break;
 case 8:result=network_transport_control_00586ee0(ptr(S),stage,count,static_cast<U*>(ptr(D)),ptr(R));break;
 }
 // Normalize only native function-pointer words; all other backing remains exact.
 put(S+0x24,0x24000000);put(V+8,0x24000000);put(R+0x10,0x24000030);for(U i=0;i<4;++i){put(N+i*0x40+4,0x24000010);put(N+i*0x40+8,0x24000020);}
 std::cout<<"{\"return\":"<<result<<",\"trace\":[";for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';}std::cout<<"],\"state\":[";
 bool first=true;for(auto range:{std::pair<U,U>{B,0x200},{R,0x100},{N,0x100},{D,0x100},{SRC,0x8000}})for(U i=0;i<range.second;i+=4){if(!first)std::cout<<',';first=false;std::cout<<get(range.first+i);}std::cout<<"]}\n";
 }VirtualFree(ptr(B),0,MEM_RELEASE);return 0;
}
}
int main(){return porsche::main();}
