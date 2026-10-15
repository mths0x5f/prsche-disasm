#pragma once
#include <cstddef>
#include <cstdint>
namespace porsche {
struct RttiCompleteObjectLocator;
using RttiTypeInfoDestructor=void* (__fastcall*)(void*,void*,std::uint32_t);
struct RttiTypeInfoTable {const RttiCompleteObjectLocator* rtti;RttiTypeInfoDestructor destructor;};
struct RttiTypePrefix {const void* vptr;void* cached_name;};
template<std::size_t N>struct RttiTypeDescriptor {RttiTypePrefix prefix;char decorated_name[N];};
struct RttiPmd {std::int32_t member_offset,vbase_pointer_offset,vbase_offset;};
struct RttiBaseDescriptor {const RttiTypePrefix* type;std::uint32_t contained_bases;RttiPmd displacement;std::uint32_t attributes;};
struct RttiHierarchy {std::uint32_t signature,attributes,count;const RttiBaseDescriptor* const* bases;};
struct RttiCompleteObjectLocator {std::uint32_t signature,offset,constructor_displacement;const RttiTypePrefix* type;const RttiHierarchy* hierarchy;};
static_assert(sizeof(RttiTypePrefix)==8&&sizeof(RttiTypeInfoTable)==8&&sizeof(RttiPmd)==12&&sizeof(RttiBaseDescriptor)==24&&sizeof(RttiHierarchy)==16&&sizeof(RttiCompleteObjectLocator)==20);
static_assert(offsetof(RttiTypeDescriptor<16>,decorated_name)==8&&offsetof(RttiTypeInfoTable,destructor)==4);
extern const RttiTypeInfoTable rtti_type_info_table_005c18f8;
extern RttiTypeDescriptor<16> rtti_type_info_005e51c0;
extern RttiTypeDescriptor<17> rtti_client_type_005d0630;
extern RttiTypeDescriptor<18> rtti_connection_type_005d0650;
extern RttiTypeDescriptor<15> rtti_host_type_005d0690;
extern const RttiCompleteObjectLocator rtti_type_info_locator_005c98d0;
extern const RttiCompleteObjectLocator network_rtti_005c5190,network_rtti_005c51d8,network_rtti_005c5228;
void __fastcall rtti_type_info_destroy_005a1011(void*,void*);
void* __fastcall rtti_type_info_delete_005a103a(void*,void*,std::uint32_t);
void* __cdecl rtti_complete_object_005a14b3(void*);
const RttiBaseDescriptor* __cdecl rtti_find_single_005a14cd(void*,const RttiCompleteObjectLocator*,const RttiTypePrefix*,std::uint32_t,const RttiTypePrefix*);
const RttiBaseDescriptor* __cdecl rtti_find_multiple_005a1527(void*,const RttiCompleteObjectLocator*,const RttiTypePrefix*,std::uint32_t,const RttiTypePrefix*);
const RttiBaseDescriptor* __cdecl rtti_find_virtual_005a1620(void*,const RttiCompleteObjectLocator*,const RttiTypePrefix*,std::uint32_t,const RttiTypePrefix*);
std::uint32_t __cdecl rtti_pmd_offset_005a1758(void*,const RttiPmd*);
std::int32_t __cdecl rtti_compare_names_005a4c20(const char*,const char*);
}
