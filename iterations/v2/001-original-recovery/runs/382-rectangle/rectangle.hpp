#pragma once
#include <cstdint>
namespace porsche {
// Exact20-byte blocks. Fields are raw FLOAT32 words except where copied as bits.
// 006a6404:z,6408:u0,640c:v0,6410:left,6414:top.
extern std::uint32_t rectangle_state_006a6404[5];
// 005dfa08:rhw,fa0c:u1,fa10:v1,fa14:right,fa18:bottom.
extern std::uint32_t rectangle_limits_005dfa08[5];
extern const float rectangle_zero_005b23f8;
}
