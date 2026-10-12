#pragma once

#include "porsche/formatter_original.hpp"

#include <cstdint>

namespace porsche {

// 005a4259 consumes the full 32-byte CRT-like descriptor. The shared
// formatter descriptor type is reused; the tail words at +0x10 and +0x18
// have cleanup-specific meanings, while +0x14 and +0x1c stay opaque.
std::int32_t __cdecl formatter_cleanup_005a4259(
    std::uint32_t character, FormatterOriginalDescriptor32* descriptor);

// Canonical owner shared with the formatter-output regression probe.
std::uint32_t __cdecl cleanup_is_character_device_005abf35(std::uint32_t file_id);

// Typed unresolved file/descriptor operations called by the recovered body.
std::int32_t __cdecl formatter_cleanup_file_write_005a9e49(
    std::uint32_t file_id, const void* bytes, std::int32_t length);
std::int32_t __cdecl formatter_cleanup_file_aux_005a9ab8(
    std::uint32_t file_id, std::uint32_t offset, std::uint32_t origin);
std::int32_t __cdecl formatter_cleanup_prepare_descriptor_005abef1(
    FormatterOriginalDescriptor32* descriptor);

// Existing runtime owners must bind these aliases; this packet defines no
// duplicate global storage for original FILE objects or handle tables.
extern FormatterOriginalDescriptor32* formatter_cleanup_stream_005e5508;
extern FormatterOriginalDescriptor32* formatter_cleanup_stream_005e5528;
extern const std::uint8_t* formatter_cleanup_invalid_handle_record_005e5f50;
// The signed SAR lookup at 005a4304 can address the DWORD immediately before
// the handle-table base for file identifiers -32..-2. Its runtime owner is
// still external; integration fixtures bind this adjacent cell explicitly.
extern const std::uint8_t* formatter_cleanup_preceding_handle_bank_006c01dc;
extern const std::uint8_t* formatter_cleanup_handle_table_006c01e0[];
extern std::uint32_t formatter_cleanup_handle_limit_006c02e0;

} // namespace porsche
