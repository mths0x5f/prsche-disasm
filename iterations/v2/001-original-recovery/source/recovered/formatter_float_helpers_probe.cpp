#include "porsche/formatter_float_helpers.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

namespace {
alignas(8) unsigned char arena[256];
alignas(4) unsigned char classes[1024];
std::vector<std::string> events;
int mutation;
std::string hex_bytes(const void* data, std::size_t n) {
    const auto* p = static_cast<const unsigned char*>(data);
    const char* digits = "0123456789abcdef";
    std::string result;
    for (std::size_t i = 0; i < n; ++i) { result += digits[p[i] >> 4]; result += digits[p[i] & 15]; }
    return result;
}
unsigned char nibble(char c) { return static_cast<unsigned char>(c <= '9' ? c - '0' : c - 'a' + 10); }
void decode(const std::string& s, void* p, std::size_t n) {
    auto* out = static_cast<unsigned char*>(p);
    for (std::size_t i = 0; i < n; ++i) out[i] = static_cast<unsigned char>((nibble(s[i * 2]) << 4) | nibble(s[i * 2 + 1]));
}
std::string text_hex(const char* p) { return hex_bytes(p, std::strlen(p)); }
void print_events() {
    std::printf("\"events\":[");
    for (std::size_t i = 0; i < events.size(); ++i) std::printf("%s\"%s\"", i ? "," : "", events[i].c_str());
    std::printf("]");
}
void format_boundary(const char* name, const void* number, char* output, int precision, int caps) {
    events.push_back(std::string(name) + ":" + hex_bytes(number, 8) + ":" + std::to_string(precision) + ":" + std::to_string(caps));
    output[0] = name[0]; output[1] = 0;
}
using SignFunction = int (__cdecl *)(const double*);
SignFunction original_sign() {
    // Exact005a3edb..005a3ef2; patch only HIGHLOW absolute data relocation at+8.
    const unsigned char bytes[24] = {
        0x8b,0x44,0x24,0x04,0xdd,0x00,0xdc,0x1d,0xc0,0x24,0x5b,0x00,
        0xdf,0xe0,0x9e,0x72,0x04,0x6a,0x01,0x58,0xc3,0x33,0xc0,0xc3
    };
    static const std::uint64_t zero = 0;
    auto* memory = static_cast<unsigned char*>(VirtualAlloc(nullptr, sizeof(bytes), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    if (!memory) std::abort();
    std::memcpy(memory, bytes, sizeof(bytes));
    const auto relocated = reinterpret_cast<std::uintptr_t>(&zero);
    std::memcpy(memory + 8, &relocated, 4);
    DWORD old_protection;
    if (!VirtualProtect(memory, sizeof(bytes), PAGE_EXECUTE_READ, &old_protection)) std::abort();
    if (!FlushInstructionCache(GetCurrentProcess(), memory, sizeof(bytes))) std::abort();
    return reinterpret_cast<SignFunction>(memory);
}
struct SignState { int result; unsigned short control, status, tag; unsigned char value[80]; };
SignState evaluate_sign(SignFunction function, const std::uint64_t* number, unsigned control, unsigned prefix) {
    unsigned short cw = static_cast<unsigned short>(control);
    const double held = 7.25;
    __asm { fninit }
    __asm { fldcw cw }
    for (unsigned i = 0; i < prefix; ++i) { __asm { fld held } }
    SignState out;
    out.result = function(reinterpret_cast<const double*>(number));
    unsigned char environment[108];
    __asm { fnsave environment }
    std::memcpy(&out.control, environment, 2);
    std::memcpy(&out.status, environment + 4, 2);
    std::memcpy(&out.tag, environment + 8, 2);
    std::memcpy(out.value, environment + 28, 80);
    return out;
}
void print_sign(const SignState& value, unsigned prefix) {
    std::printf("\"return\":%d,\"control\":%u,\"status\":%u,\"tag\":%u,\"top_value\":\"%s\"",
        value.result, value.control, value.status, value.tag, prefix ? hex_bytes(value.value, prefix * 10).c_str() : "");
}
}
namespace porsche {
const std::uint8_t* formatter_ctype_table_005e52d0 = classes + 256;
int __cdecl formatter_float_lower_005a2248(int c) {
    events.push_back("lower:" + std::to_string(c));
    if (mutation == 1) formatter_float_decimal_word_005e54e0 = ',';
    if (mutation == 2) formatter_float_character_width_005e54dc = 2;
    return c >= 'A' && c <= 'Z' ? c + 32 : c;
}
int __cdecl formatter_float_classify_005a2eae(int c, int mask) {
    events.push_back("class:" + std::to_string(c) + ":" + std::to_string(mask));
    if (mutation == 3) formatter_float_character_width_005e54dc = 1;
    return c >= '0' && c <= '9' ? mask : 0;
}
int __cdecl formatter_float_parse_words_005ac716(FormatterFloatWords12* out, const char** end,
                                               const char* text, int a, int b, int c, int d) {
    events.push_back("parse:" + text_hex(text) + ":" + std::to_string(*end == text) + ":" +
        std::to_string(a) + ":" + std::to_string(b) + ":" + std::to_string(c) + ":" + std::to_string(d));
    out->words[0] = 0x76543210; out->words[1] = 0xfedcba98; out->words[2] = 0x89abcdef;
    *end = text + std::strlen(text);
    return -17;
}
int __cdecl formatter_float_pack_words_005abb07(const FormatterFloatWords12* words, void* output,
                                              const std::uint32_t* config) {
    events.push_back("pack:" + hex_bytes(words, 12) + ":" + hex_bytes(config, 24));
    const std::uint32_t result[2] = {words->words[0] ^ 0x13579bdfu, words->words[1] ^ 0x2468ace0u};
    std::memcpy(output, result, config[4] == 64 ? 8 : 4);
    return -39;
}
char* __cdecl formatter_float_scientific_005a3f31(const void* n, char* out, int p, int caps) {
    format_boundary("scientific", n, out, p, caps); return out;
}
char* __cdecl formatter_float_fixed_005a4054(const void* n, char* out, int p) {
    format_boundary("fixed", n, out, p, 0); return out;
}
char* __cdecl formatter_float_general_005a4150(const void* n, char* out, int p, int caps) {
    format_boundary("general", n, out, p, caps); return out;
}
}

int main() {
    using namespace porsche;
    const auto original_sign_function = original_sign();
    char kind;
    while (std::cin >> kind) {
        events.clear();
        if (kind == 't') {
            int op, width, decimal;
            std::string text;
            std::cin >> op >> width >> decimal >> mutation >> text;
            std::memset(arena, 0xcc, sizeof(arena));
            decode(text, arena + 32, text.size() / 2);
            std::memset(arena + 32 + text.size() / 2, 0, 8);
            std::memset(classes, 0, sizeof(classes));
            for (unsigned c = '0'; c <= '9'; ++c) classes[256 + c * 2] = 4;
            formatter_float_character_width_005e54dc = width;
            formatter_float_decimal_word_005e54e0 = decimal;
            if (op == 0) formatter_float_decimal_005a3e33(reinterpret_cast<char*>(arena + 32));
            else formatter_float_trim_005a3e8d(reinterpret_cast<char*>(arena + 32));
            std::printf("{\"kind\":\"text\",\"arena\":\"%s\",\"width\":%d,\"decimal\":%u,",
                hex_bytes(arena, sizeof(arena)).c_str(), formatter_float_character_width_005e54dc,
                formatter_float_decimal_word_005e54e0);
            print_events(); std::puts("}");
        } else if (kind == 's') {
            std::string bits;
            unsigned control, prefix;
            std::cin >> bits >> control >> prefix;
            std::uint64_t number;
            decode(bits, &number, 8);
            const auto recovered = evaluate_sign(&formatter_float_sign_body_005a3edb, &number, control, prefix);
            const auto original = evaluate_sign(original_sign_function, &number, control, prefix);
            std::printf("{\"kind\":\"sign\","); print_sign(recovered, prefix);
            std::printf(",\"native_original\":{"); print_sign(original, prefix); std::puts("}}");
        } else if (kind == 'p') {
            int operation, wide;
            std::string text;
            std::cin >> operation >> wide >> text;
            std::memset(arena, 0xa5, sizeof(arena));
            decode(text, arena + 32, text.size() / 2); arena[32 + text.size() / 2] = 0;
            FormatterFloatWords12 words{{0x76543210, 0xfedcba98, 0x89abcdef}};
            int result = 0;
            if (operation == 0) formatter_float_assign_body_005a3ef3(wide, arena + 128, arena + 32);
            else if (operation == 1) result = formatter_float_parse64_005abc9f(arena + 128, reinterpret_cast<char*>(arena + 32));
            else if (operation == 2) result = formatter_float_parse32_005abccc(arena + 128, reinterpret_cast<char*>(arena + 32));
            else if (operation == 3) result = formatter_float_pack64_005abc73(&words, arena + 128);
            else result = formatter_float_pack32_005abc89(&words, arena + 128);
            std::printf("{\"kind\":\"parse\",\"arena\":\"%s\",\"return\":%d,", hex_bytes(arena, sizeof(arena)).c_str(), result);
            print_events(); std::puts("}");
        } else if (kind == 'c') {
            int conversion, precision, caps;
            std::cin >> conversion >> precision >> caps;
            std::memset(arena, 0xa5, sizeof(arena));
            const std::uint64_t number = 0xc03123456789abcd;
            formatter_float_convert_005a41e3(&number, reinterpret_cast<char*>(arena + 128), conversion, precision, caps);
            std::printf("{\"kind\":\"convert\",\"arena\":\"%s\",", hex_bytes(arena, sizeof(arena)).c_str());
            print_events(); std::puts("}");
        } else return 2;
    }
    VirtualFree(reinterpret_cast<void*>(original_sign_function), 0, MEM_RELEASE);
}
