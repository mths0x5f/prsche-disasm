// Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// Exact independent read-only float cells at original VAs 005b47d8 and 005b2764.
#pragma section(".p3lim", read)
#pragma section(".p3step", read)
namespace porsche {
__declspec(allocate(".p3lim")) extern const float frame_limit_005b47d8 = 8000.0f;
__declspec(allocate(".p3step")) extern const float frame_step_005b2764 = 10000.0f;
static_assert(sizeof(float) == 4 && alignof(float) == 4, "original float4 cells");
}
