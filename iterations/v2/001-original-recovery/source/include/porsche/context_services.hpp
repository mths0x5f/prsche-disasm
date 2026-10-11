#pragma once
#include "porsche/context_effects.hpp"
#include <cstdint>

namespace porsche {
void* __fastcall context_identity_00423610(void* object,void* unused_edx);
void* __fastcall context_empty_range_00505810(void* object,void* unused_edx,std::uint32_t ignored);
std::uint32_t __cdecl context_strlen_004d55c0(const char* text);
void* __fastcall context_string_construct_004d64a0(void* object,void* unused_edx,
    const char* text,std::uint32_t ignored);
void* __fastcall context_string_assign_range_004298a0(void* object,void* unused_edx,
    const void* first,const void* last);
void* __fastcall context_string_copy_00429bf0(void* object,void* unused_edx,const void* source);
void __fastcall context_string_destroy_00429840(void* object,void* unused_edx);
std::int32_t __fastcall context_vector_count_004d6510(const void* object,void* unused_edx);
void* __fastcall context_vector_at_004d6520(const void* object,void* unused_edx,std::uint32_t index);
void __fastcall context_vector_pop_004d6530(void* object,void* unused_edx);
std::uint32_t __cdecl context_word_not_equal_004d67b0(const void* first,const void* second);
// Typed unresolved original copy service; this packet does not implement it.
void* __cdecl context_move_005a1a40(void* destination,const void* source,std::uint32_t bytes);
}
