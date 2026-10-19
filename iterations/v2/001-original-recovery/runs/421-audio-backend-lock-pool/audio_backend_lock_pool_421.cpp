// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
//
// Audio backend lock and pool helpers, ten bodies:
//   0058e2d0 (12)  0058e2e0 (12)  0058e2f0 (12)  0058e300 (12)
//   005896d0 (18)  005896f0 (17)
//   0058aa90 (44)  0058aac0 (31)  0058fef0 (31)  0058ff10 (50)
#include "audio_backend_lock_pool_421.hpp"

namespace porsche {

namespace {

AudioBackendPoolHeader_421* pool_at(std::uint32_t va) {
    return reinterpret_cast<AudioBackendPoolHeader_421*>(static_cast<std::uintptr_t>(va));
}

} // namespace

// ---------------------------------------------------------------------------
// 0058e2d0 (12 bytes): push 006b1800; call [005b207c] InitializeCriticalSection.
// Canonical name says "start"; the body only creates the backend lock.
// ---------------------------------------------------------------------------
void __cdecl application_audio_backend_start_0058e2d0() {
    platform_initialize_critical_section(audio_backend_lock_cs_006b1800);
}

// 0058e2e0 (12 bytes): push 006b1800; call [005b2068] DeleteCriticalSection.
// Canonical name says "stop"; the body only destroys the backend lock.
void __cdecl application_audio_backend_stop_0058e2e0() {
    platform_delete_critical_section(audio_backend_lock_cs_006b1800);
}

// 0058e2f0 (12 bytes): push 006b1800; call [005b2078] EnterCriticalSection.
void __cdecl audio_backend_enter_0058e2f0() {
    platform_enter_critical_section(audio_backend_lock_cs_006b1800);
}

// 0058e300 (12 bytes): push 006b1800; call [005b206c] LeaveCriticalSection.
void __cdecl audio_backend_leave_0058e300() {
    platform_leave_critical_section(audio_backend_lock_cs_006b1800);
}

// ---------------------------------------------------------------------------
// 005896d0 (18 bytes): enter the lock, then increment the byte counter
// (mov al,[006b499f]; inc al; mov [006b499f],al) — it wraps at 8 bits.
// ---------------------------------------------------------------------------
void __cdecl audio_backend_lock_005896d0() {
    audio_backend_enter_0058e2f0();
    audio_backend_lock_depth_006b499f =
        static_cast<std::uint8_t>(audio_backend_lock_depth_006b499f + 1u);
}

// 005896f0 (17 bytes): decrement the counter first, then tail-jump to the
// leave primitive (jmp 0058e300).
void __cdecl audio_backend_unlock_005896f0() {
    audio_backend_lock_depth_006b499f =
        static_cast<std::uint8_t>(audio_backend_lock_depth_006b499f - 1u);
    audio_backend_leave_0058e300();
}

// ---------------------------------------------------------------------------
// 0058fef0 (31 bytes): zero buffer_bytes bytes at buffer_va. The length test is
// signed (test ecx,ecx; jle), so zero and negative lengths do nothing. Then
// rep stosd for len>>2 dwords and rep stosb for len&3 bytes.
// ---------------------------------------------------------------------------
void __cdecl application_audio_backend_configure_0058fef0(
    std::uint32_t buffer_va, std::uint32_t buffer_bytes) {
    if (static_cast<std::int32_t>(buffer_bytes) <= 0) {
        return;
    }
    auto* dwords = reinterpret_cast<std::uint32_t*>(static_cast<std::uintptr_t>(buffer_va));
    const std::uint32_t dword_count = buffer_bytes >> 2;
    for (std::uint32_t i = 0; i < dword_count; ++i) {
        dwords[i] = 0;
    }
    auto* bytes = reinterpret_cast<std::uint8_t*>(dwords + dword_count);
    const std::uint32_t tail = buffer_bytes & 3u;
    for (std::uint32_t i = 0; i < tail; ++i) {
        bytes[i] = 0;
    }
}

// ---------------------------------------------------------------------------
// 0058aa90 (44 bytes): publish buffer_va as the pool and write its header.
// Store order follows the original: global, +08, +04, +00, +0c, +10.
// ---------------------------------------------------------------------------
void __cdecl application_audio_backend_configure_0058aa90(
    std::uint32_t buffer_va, std::uint32_t buffer_bytes) {
    audio_backend_pool_006b4a18 = buffer_va;
    AudioBackendPoolHeader_421* header = pool_at(buffer_va);
    header->size = buffer_bytes;
    header->end_marker = buffer_va + buffer_bytes - 8u;
    header->first_aligned = (buffer_va + 0x1bu) & 0xfffffffcu;
    const std::uint32_t reduced = buffer_bytes - 3u;
    header->limit = reduced - 0x20u;
    header->cursor = reduced;
}

// ---------------------------------------------------------------------------
// 0058aac0 (31 bytes): ((size - cursor) * 100) / size as a signed division.
// The multiply is lea*5, lea*5, shl 2 in 32 bits, so it wraps; cdq; idiv ecx.
// Canonical name says "close"; the body only reads the pool usage. A zero size
// faults in the original exactly as here; that case is not exercised.
// ---------------------------------------------------------------------------
std::int32_t __cdecl application_audio_backend_close_0058aac0() {
    const AudioBackendPoolHeader_421* header = pool_at(audio_backend_pool_006b4a18);
    const std::uint32_t size = header->size;
    const std::uint32_t used = size - header->cursor;
    const std::int32_t scaled = static_cast<std::int32_t>(used * 100u);
    return scaled / static_cast<std::int32_t>(size);
}

// ---------------------------------------------------------------------------
// 0058ff10 (50 bytes): stop every channel. The count is a signed 16-bit cell
// (cmp word ptr [006b49a4],0; jle) and both the count and the table pointer
// are reloaded after each 00565d60 call; records are 0x70 bytes apart.
// ---------------------------------------------------------------------------
void __cdecl application_audio_backend_quiet_0058ff10() {
    if (audio_backend_channel_count_006b49a4 <= 0) {
        return;
    }
    std::int32_t index = 0;
    std::uint32_t offset = 0;
    std::int32_t count;
    do {
        const std::uint32_t table = audio_backend_channels_006b4a00;
        const std::uint32_t handle =
            *reinterpret_cast<const std::uint32_t*>(static_cast<std::uintptr_t>(table + offset));
        audio_channel_stop_00565d60(handle);
        count = audio_backend_channel_count_006b49a4;
        ++index;
        offset += 0x70u;
    } while (index < count);
}

} // namespace porsche
