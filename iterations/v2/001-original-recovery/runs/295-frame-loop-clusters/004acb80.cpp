#include "frame_loop_clusters_295.hpp"
#include <cstring>

namespace porsche {
namespace {
std::uint32_t read_u32(const std::uint8_t* p) {
    std::uint32_t v;
    std::memcpy(&v, p, sizeof(v));
    return v;
}
void write_u32(std::uint8_t* p, std::uint32_t v) {
    std::memcpy(p, &v, sizeof(v));
}
} // namespace

void __cdecl application_main_function_004acb80() {
    for (std::size_t bank_idx = 0; bank_idx < 2u; ++bank_idx) {
        auto* bank = static_cast<std::uint8_t*>(audio_channel_banks_00656aa8[bank_idx]);
        if (bank != nullptr) {
            const std::uint8_t mode = bank[0x2d2];
            bank[0x40] = 0u;
            bank[0x2d3] = mode;
            write_u32(bank + 0x38, 0xffffffffu);
            write_u32(bank + 0x3c, 0xffffffffu);
            std::uint8_t* pair_cursor = bank + 0x5dc;
            std::uint8_t* state_cursor = bank + 0x44;
            for (std::uint32_t i = 0; i < 32u; ++i) {
                const std::uint32_t first = read_u32(pair_cursor - 0x180);
                if (first != 0xffffffffu) {
                    audio_channel_stop_00565d60(first);
                }
                const std::uint32_t second = read_u32(pair_cursor);
                if (second != 0xffffffffu) {
                    audio_channel_stop_00565d60(second);
                }
                write_u32(state_cursor, 0u);
                write_u32(pair_cursor - 0x180, 0xffffffffu);
                write_u32(pair_cursor, 0xffffffffu);
                state_cursor += 4;
                pair_cursor += 0x0c;
            }
        }
    }
}
} // namespace porsche
