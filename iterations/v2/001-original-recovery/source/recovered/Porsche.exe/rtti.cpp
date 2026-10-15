#include "porsche/rtti.hpp"
#include "porsche/exit_registry.hpp"
#include "porsche/formatter_crt_runtime.hpp"
#include "porsche/application_alloc.hpp"
#include <cstring>
namespace porsche {
namespace {
using U=std::uint32_t;
void* ptr(U p){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(p));}U raw(const void*p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(const void*p,U offset=0){U v;std::memcpy(&v,static_cast<const unsigned char*>(p)+offset,4);return v;}void put(void*p,U offset,U v){std::memcpy(static_cast<unsigned char*>(p)+offset,&v,4);}
bool same_type(const RttiTypePrefix*a,const RttiTypePrefix*b){return a==b||!rtti_compare_names_005a4c20(reinterpret_cast<const char*>(a)+8,reinterpret_cast<const char*>(b)+8);}
const RttiBaseDescriptor type_info_base{&rtti_type_info_005e51c0.prefix,0,{0,-1,0},0};
const RttiBaseDescriptor client_base{&rtti_client_type_005d0630.prefix,1,{0,-1,0},0};
const RttiBaseDescriptor connection_base{&rtti_connection_type_005d0650.prefix,0,{0,-1,0},0};
const RttiBaseDescriptor host_base{&rtti_host_type_005d0690.prefix,1,{0,-1,0},0};
const RttiBaseDescriptor* const type_info_bases[]={&type_info_base};
const RttiBaseDescriptor* const client_bases[]={&client_base,&connection_base};
const RttiBaseDescriptor* const connection_bases[]={&connection_base};
const RttiBaseDescriptor* const host_bases[]={&host_base,&connection_base};
const RttiHierarchy type_info_hierarchy{0,0,1,type_info_bases},client_hierarchy{0,0,2,client_bases},connection_hierarchy{0,0,1,connection_bases},host_hierarchy{0,0,2,host_bases};
}
// Each name array ends at its proven original NUL. C++ alignment padding is not
// claimed to be an original object extent. Cached names are canonical mutable state.
RttiTypeDescriptor<16> rtti_type_info_005e51c0{{&rtti_type_info_table_005c18f8.destructor,nullptr},".?AVtype_info@@"};
RttiTypeDescriptor<17> rtti_client_type_005d0630{{&rtti_type_info_table_005c18f8.destructor,nullptr},".?AVCConClient@@"};
RttiTypeDescriptor<18> rtti_connection_type_005d0650{{&rtti_type_info_table_005c18f8.destructor,nullptr},".?AVCConnection@@"};
RttiTypeDescriptor<15> rtti_host_type_005d0690{{&rtti_type_info_table_005c18f8.destructor,nullptr},".?AVCConHost@@"};
const RttiCompleteObjectLocator rtti_type_info_locator_005c98d0{0,0,0,&rtti_type_info_005e51c0.prefix,&type_info_hierarchy};
const RttiCompleteObjectLocator network_rtti_005c5190{0,0,0,&rtti_client_type_005d0630.prefix,&client_hierarchy};
const RttiCompleteObjectLocator network_rtti_005c51d8{0,0,0,&rtti_connection_type_005d0650.prefix,&connection_hierarchy};
const RttiCompleteObjectLocator network_rtti_005c5228{0,0,0,&rtti_host_type_005d0690.prefix,&host_hierarchy};
const RttiTypeInfoTable rtti_type_info_table_005c18f8{&rtti_type_info_locator_005c98d0,rtti_type_info_delete_005a103a};
void __fastcall rtti_type_info_destroy_005a1011(void* object,void*){
 put(object,0,raw(&rtti_type_info_table_005c18f8.destructor));exit_registry_lock_api_005a4ba4(27);
 const U cached=get(object,4);if(cached)formatter_crt_free_005a3b9d(ptr(cached));exit_registry_unlock_api_005a4c05(27);
}
void* __fastcall rtti_type_info_delete_005a103a(void*object,void*,U flags){rtti_type_info_destroy_005a1011(object,nullptr);if(flags&1)application_release_0059f050(object);return object;}
void* __cdecl rtti_complete_object_005a14b3(void*object){
 auto* locator=static_cast<const RttiCompleteObjectLocator*>(ptr(get(ptr(get(object)-4))));U result=raw(object)-locator->offset;
 const U displacement=locator->constructor_displacement;if(displacement)result+=get(ptr(raw(object)-displacement));return ptr(result);
}
U __cdecl rtti_pmd_offset_005a1758(void*object,const RttiPmd*pmd){
 U adjustment=0;if(pmd->vbase_pointer_offset>=0){adjustment=static_cast<U>(pmd->vbase_pointer_offset);const U table=get(ptr(raw(object)+adjustment));adjustment+=get(ptr(table+static_cast<U>(pmd->vbase_offset)));}
 return static_cast<U>(pmd->member_offset)+adjustment;
}
const RttiBaseDescriptor* __cdecl rtti_find_single_005a14cd(void*,const RttiCompleteObjectLocator*locator,const RttiTypePrefix*,U,const RttiTypePrefix*target){
 auto bases=locator->hierarchy->bases;for(U i=0;i<locator->hierarchy->count;++i,++bases){auto*base=*bases;if(same_type(base->type,target)&&!(base->attributes&1))return base;}return nullptr;
}
const RttiBaseDescriptor* __cdecl rtti_find_multiple_005a1527(void*object,const RttiCompleteObjectLocator*locator,const RttiTypePrefix*source,U offset,const RttiTypePrefix*target){
 auto bases=locator->hierarchy->bases;for(U i=0;i<locator->hierarchy->count;++i,++bases){auto*base=*bases;if(!same_type(base->type,target))continue;
  auto following=bases+1;for(U j=0;j<base->contained_bases;++j,++following){auto*child=*following;if(same_type(child->type,source)&&rtti_pmd_offset_005a1758(object,&child->displacement)==offset)return base;}
 }
 bases=locator->hierarchy->bases;for(U i=0;i<locator->hierarchy->count;++i,++bases){auto*base=*bases;if(same_type(base->type,target)&&!(base->attributes&3))return base;}return nullptr;
}
const RttiBaseDescriptor* __cdecl rtti_find_virtual_005a1620(void*object,const RttiCompleteObjectLocator*locator,const RttiTypePrefix*source,U offset,const RttiTypePrefix*target){
 const RttiBaseDescriptor*found=nullptr;auto bases=locator->hierarchy->bases;
 for(U i=0;i<locator->hierarchy->count;++i,++bases){auto*base=*bases;if(!same_type(base->type,target))continue;
  auto following=bases+1;for(U j=0;j<base->contained_bases;++j,++following){auto*child=*following;if(!same_type(child->type,source)||rtti_pmd_offset_005a1758(object,&child->displacement)!=offset)continue;
   if(found&&rtti_pmd_offset_005a1758(object,&base->displacement)!=rtti_pmd_offset_005a1758(object,&found->displacement))return nullptr;found=base;
  }
 }
 if(found)return found;
 bases=locator->hierarchy->bases;for(U i=0;i<locator->hierarchy->count;++i,++bases){auto*base=*bases;if(same_type(base->type,target)&&!(base->attributes&3))return base;}return nullptr;
}
std::int32_t __cdecl rtti_compare_names_005a4c20(const char*left,const char*right){
 auto*l=reinterpret_cast<const unsigned char*>(left);auto*r=reinterpret_cast<const unsigned char*>(right);
 auto one=[&](){const U a=*l++,b=*r++;return a==b?(a?2:0):(a<b?-1:1);};
 if(raw(l)&1){const int result=one();if(result!=2)return result;}
 if(raw(l)&2){std::uint16_t word;std::memcpy(&word,l,2);for(U i=0;i<2;++i){const U a=(word>>(i*8))&255,b=r[i];if(a!=b)return a<b?-1:1;if(!a)return 0;}l+=2;r+=2;}
 for(;;){const U word=get(l);for(U i=0;i<4;++i){const U a=(word>>(i*8))&255,b=r[i];if(a!=b)return a<b?-1:1;if(!a)return 0;}l+=4;r+=4;}
}
}
