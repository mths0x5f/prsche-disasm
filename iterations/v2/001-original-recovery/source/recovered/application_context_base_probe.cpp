#include "porsche/application_context_base.hpp"

#include "porsche/application_heap_init.hpp"

#include <windows.h>

#include <array>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

static_assert(sizeof(void*) == 4, "Run 135 requires native Win32/x86");

namespace {
constexpr std::uintptr_t kPoolBase = 0x23000000u;
constexpr std::size_t kPoolSize = 0x00200000u;
constexpr std::uint32_t kManager = 0x23010000u;
constexpr std::uint32_t kLock = 0x23010100u;
constexpr std::uint32_t kHeapSelector = 0x23010300u;
constexpr std::uint32_t kContext = 0x23020000u;
constexpr std::uint32_t kHead = 0x23030000u;
constexpr std::uint32_t kHeadNext = 0x23031000u;
constexpr std::uint32_t kCtorAllocation = 0x23040000u;
constexpr std::uint32_t kContextMember = 0x23041000u;
constexpr std::uint32_t kMemberStorage = 0x23042000u;
constexpr std::uint32_t kExistingHead = 0x23043000u;
constexpr std::uint32_t kListNode = 0x23044000u;
constexpr std::uint32_t kMember = 0x23050000u;
constexpr std::uint32_t kMemberArray = 0x23060000u;
constexpr std::uint32_t kMemberBlock = 0x23070000u;
constexpr std::uint32_t kReturnValue = 0xcafe0071u;

std::uint8_t* pool = nullptr;
std::vector<std::string> trace;
std::vector<std::string> constructor_trace;
std::array<std::uint32_t, 8> allocation_results{};
std::array<std::uint32_t, 8> allocation_sizes{};
std::size_t allocation_count = 0;
std::size_t allocation_index = 0;
std::uint32_t head_next = 0;
std::uint32_t member_block_result = kMemberBlock;
unsigned active_id = 0;
unsigned block_calls = 0;
unsigned destroy_calls = 0;
std::uint32_t selector_cell = kHeapSelector;

std::uint32_t read32(std::uint32_t address) {
    std::uint32_t result;
    std::memcpy(&result, reinterpret_cast<const void*>(address), 4);
    return result;
}
void write32(std::uint32_t address, std::uint32_t value) {
    std::memcpy(reinterpret_cast<void*>(address), &value, 4);
}
std::string hex32(std::uint32_t value) {
    std::ostringstream out;
    out << std::hex << std::setfill('0') << std::setw(8) << value;
    return out.str();
}
std::string hex_bytes(const void* address, std::size_t bytes) {
    const auto* data = static_cast<const std::uint8_t*>(address);
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (std::size_t i = 0; i < bytes; ++i)
        out << std::setw(2) << static_cast<unsigned>(data[i]);
    return out.str();
}
void event(std::string text) { trace.emplace_back(std::move(text)); }
void fill_canary(std::uint8_t* start, std::size_t size) {
    for (std::size_t i = 0; i < size; ++i)
        start[i] = static_cast<std::uint8_t>((i * 19u + 0x17u) & 0xffu);
}
void reset(unsigned id) {
    active_id = id;
    block_calls = destroy_calls = 0;
    selector_cell = kHeapSelector;
    if (!pool) {
        pool = static_cast<std::uint8_t*>(VirtualAlloc(
            reinterpret_cast<void*>(kPoolBase), kPoolSize,
            MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE));
        if (pool != reinterpret_cast<std::uint8_t*>(kPoolBase)) {
            std::cerr << "fixed scratch VirtualAlloc failed\n";
            std::exit(3);
        }
    }
    fill_canary(pool, kPoolSize);
    trace.clear();
    constructor_trace.clear();
    allocation_index = 0;
    allocation_count = 0;
    allocation_results.fill(0);
    allocation_sizes.fill(0);
    head_next = 0;
    member_block_result = kMemberBlock;

    write32(kManager + 0x28, kLock);
    write32(kManager + 0x40, (id == 2 || id == 7 || id == 8) ? kExistingHead : 0);
    write32(kExistingHead, 0x11111111u);
    write32(kExistingHead + 4, kHead);
    write32(kHead, 0x22222222u);
    write32(kHead + 4, 0);
    write32(kHeapSelector, 7);
    write32(kMemberArray, 0x23061000u);
    write32(kMemberArray + 4, 0x23062000u);
    write32(kMemberArray + 8, 0x23063000u);
    write32(kMemberArray + 12, kMemberBlock);
    write32(kMemberArray + 16, 0x23065000u);
    write32(kMemberArray + 20, 0x23066000u);
    write32(kMemberArray + 24, 0x23067000u);
    write32(kMemberArray + 28, 0x23068000u);
    write32(kListNode + 8, 0);
    write32(kListNode + 0x0c, 0x55667788u);
    write32(kListNode + 0x10, 0x23045000u);
    write32(kListNode + 0x100 + 8, 0);
    write32(kListNode + 0x100 + 0x0c, 0x99aabbccu);

    auto* context = reinterpret_cast<porsche::ApplicationSetupContext*>(kContext);
    std::memcpy(context->bytes, pool + (kContext - kPoolBase), 0x180);
    std::memcpy(reinterpret_cast<void*>(kMember), pool + (kMember - kPoolBase), 0x2c);
    if (id == 0 || id == 18) {
        allocation_results[0] = 0;
        allocation_sizes[0] = 0x0c;
        allocation_count = 1;
    } else if (id == 1 || id == 2 || (id >= 6 && id <= 8)) {
        allocation_results[0] = kCtorAllocation;
        allocation_sizes[0] = 0x0c;
        allocation_count = 1;
    } else if (id == 3) {
        allocation_results[0] = 0;
        allocation_sizes[0] = 0x28;
        allocation_count = 1;
    } else if (id == 4 || (id >= 9 && id <= 11) || id == 16 || id == 17) {
        allocation_results[0] = kMemberStorage;
        allocation_sizes[0] = 0x28;
        allocation_count = 1;
    } else if (id == 5) {
        allocation_results[0] = kCtorAllocation;
        allocation_sizes[0] = 0x0c;
        allocation_results[1] = kContextMember;
        allocation_sizes[1] = 0x2c;
        allocation_results[2] = kMemberStorage;
        allocation_sizes[2] = 0x28;
        allocation_count = 3;
    }
    if (id == 16) member_block_result = 0;

    if (id == 5) {
        std::memcpy(porsche::application_object_heap_name_005e8e50,
            "ctx", 4);
    } else {
        porsche::application_object_heap_name_005e8e50[0] = '\0';
    }
}

void print_result(unsigned id, const std::string& before, const std::string& after,
    std::uint32_t result, std::uint32_t base_ctor_result,
    std::uint32_t member_ctor_result, const std::string& scratch_before) {
    std::cout << "{\"case\":" << id << ",\"before\":\"" << before
        << "\",\"after\":\"" << after << "\",\"result\":\""
        << hex32(result) << "\",\"base_ctor_result\":\""
        << hex32(base_ctor_result) << "\",\"member_ctor_result\":\""
        << hex32(member_ctor_result) << "\",\"scratch_before\":\""
        << scratch_before << "\",\"scratch\":\""
        << hex_bytes(pool + 0x10000, 0x70000) << "\",\"trace\":[";
    for (std::size_t i = 0; i < trace.size(); ++i)
        std::cout << (i ? "," : "") << "\"" << trace[i] << "\"";
    std::cout << "],\"constructor_trace\":[";
    for (std::size_t i = 0; i < constructor_trace.size(); ++i)
        std::cout << (i ? "," : "") << "\"" << constructor_trace[i] << "\"";
    std::cout << "]}\n";
}
}

namespace porsche {
char application_object_heap_name_005e8e50[32]{};

void* __cdecl startup_network_allocate_0059ef90(std::uint32_t bytes) {
    const auto index = allocation_index++;
    const auto result = index < allocation_count && allocation_sizes[index] == bytes
        ? allocation_results[index] : 0;
    event("alloc59ef90:" + hex32(bytes) + ":" + hex32(result));
    return reinterpret_cast<void*>(static_cast<std::uintptr_t>(result));
}
std::uint32_t __cdecl application_release_0059f050(void* address) {
    const auto raw = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(address));
    event("free59f050:" + hex32(raw) + ":" + hex32(kReturnValue));
    return kReturnValue;
}
void* __cdecl application_context_heap_state_005e4fe8() {
    return reinterpret_cast<void*>(kManager);
}
std::uint32_t __cdecl application_context_heap_selector_005e4fec() {
    return read32(selector_cell);
}
void __cdecl application_context_new_head_0059eeb0(
    std::uint32_t kind, std::uint32_t slot) {
    event("newhead59eeb0:" + hex32(kind) + ":" + hex32(slot));
    write32(kManager + 0x40, kHead);
    write32(kHead + 4, head_next);
    if (active_id == 6) {
        write32(kManager + 0x28, kLock + 0x10);
        write32(kHead + 4, kHeadNext);
    }
}
void __cdecl heap_enter_005322b0(void* lock) {
    event("enter322b0:" + hex32(static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(lock))));
}
void __cdecl heap_leave_005322c0(void* lock) {
    event("leave322c0:" + hex32(static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(lock))));
}
void __fastcall application_context_unlink_005262e0(
    void* root, void*, std::uint32_t key) {
    event("unlink262e0:" + hex32(static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(root))) + ":" + hex32(key));
    if (active_id == 7 && key == 0x55667788u)
        write32(kListNode + 8, kListNode + 0x100);
}
void* __fastcall application_context_release_node_004e4560(
    void* member, void*, std::uint32_t flags) {
    event("releasenode4e4560:" + hex32(static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(member))) + ":" + hex32(flags));
    if (active_id == 7) write32(kListNode + 8, 0);
    return member;
}
void __cdecl application_context_notify_node_004d7da0(void* node, std::uint32_t flags) {
    event("notify4d7da0:" + hex32(static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(node))) + ":" + hex32(flags));
    if (active_id == 7) write32(kCtorAllocation, kHeadNext);
}
void __cdecl application_context_clear_004237d0(
    void* address, std::uint32_t bytes, std::uint32_t value) {
    event("clear4237d0:" + hex32(static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(address))) + ":" + hex32(bytes) + ":" + hex32(value));
}
void* __cdecl application_context_member_storage_004211d0(
    std::uint32_t bytes, std::uint32_t mode) {
    event("memberarray4211d0:" + hex32(bytes) + ":" + hex32(mode) + ":" + hex32(kMemberArray));
    if (active_id == 9) write32(kMemberStorage + 4, 6);
    return reinterpret_cast<void*>(kMemberArray);
}
void* __cdecl application_context_member_block_0059ecb0(
    std::uint32_t bytes, std::uint32_t heap, std::uint32_t source_va) {
    const auto result = active_id == 14 ? kMemberBlock + block_calls * 0x200 : member_block_result;
    event("memberblock59ecb0:" + hex32(bytes) + ":" + hex32(heap) + ":" + hex32(source_va) + ":" + hex32(result));
    ++block_calls;
    if (active_id == 14) {
        selector_cell = kHeapSelector + block_calls * 4;
        write32(selector_cell, 7 + block_calls);
        write32(kHeapSelector, 7 + block_calls);
    }
    return reinterpret_cast<void*>(result);
}
void __cdecl application_context_compare_ranges_00529c20(
    ApplicationContextRange16 first, ApplicationContextRange16 second,
    std::uint32_t zero) {
    event("compareranges29c20:" + hex_bytes(first.words, 16) + ":" +
        hex_bytes(second.words, 16) + ":" + hex32(zero));
    if (active_id == 10) write32(kMemberStorage, 0);
    if (active_id == 11) {
        write32(kMemberStorage + 0x14, kMemberArray + 8);
        write32(kMemberStorage + 0x24, kMemberArray + 12);
    }
    if (active_id == 17) write32(kMemberStorage + 4, 0);
}
void __cdecl application_context_member_destroy_block_00441200(
    void* block, std::uint32_t bytes) {
    event("destroyblock441200:" + hex32(static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(block))) + ":" + hex32(bytes));
    ++destroy_calls;
    if (active_id == 11) {
        write32(kMemberStorage + 4, 3);
        write32(kMemberStorage, kMemberArray + 0x100);
        write32(kMemberStorage + 0x24, 0);
        write32(kMemberStorage + 0x14, 0);
    }
}
}

int main(int argc, char** argv) {
    const auto id = argc > 1 ? static_cast<unsigned>(std::strtoul(argv[1], nullptr, 10)) : 0;
    if (id > 19) return 2;
    reset(id);
    using namespace porsche;

    std::string before;
    std::string after;
    std::string scratch_before;
    std::uint32_t result = 0;
    std::uint32_t base_ctor_result = 0;
    std::uint32_t member_ctor_result = 0;
    auto* const context = reinterpret_cast<ApplicationSetupContext*>(kContext);
    auto* const member = reinterpret_cast<void*>(id == 5 ? kContextMember : kMember);
    if (id <= 2 || (id >= 6 && id <= 8) || id == 18) {
        base_ctor_result = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(
            application_context_base_construct_00525e20(context, nullptr)));
        constructor_trace = trace;
        before = hex_bytes(context->bytes, 0x180);
        scratch_before = hex_bytes(pool + 0x10000, 0x70000);
        if (id == 2 || id == 7 || id == 8) {
            write32(kCtorAllocation + 4, 1);
            write32(kExistingHead, 0x33333333u);
            write32(kExistingHead + 4, id == 8 ? 0 : kListNode);
            write32(kListNode + 8, 0);
            write32(kListNode + 0x0c, 0x55667788u);
        }
        result = application_context_base_destroy_00525ec0(context, nullptr);
        after = hex_bytes(context->bytes, 0x180);
    } else if (id <= 4 || (id >= 9 && id <= 11) || id == 16 || id == 17) {
        member_ctor_result = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(
            application_context_member_construct_005294c0(member, nullptr)));
        before = hex_bytes(member, 0x2c);
        scratch_before = hex_bytes(pool + 0x10000, 0x70000);
        application_context_member_destroy_005295b0(member, nullptr);
        after = hex_bytes(member, 0x2c);
    } else if (id == 5) {
        const auto ctor = application_setup_context_construct_004d1a90(context, nullptr);
        base_ctor_result = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(ctor));
        before = hex_bytes(context->bytes, 0x180);
        scratch_before = hex_bytes(pool + 0x10000, 0x70000);
        result = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(ctor));
        result = application_setup_context_destroy_004d1ba0(context, nullptr);
        after = hex_bytes(context->bytes, 0x180);
    } else {
        before = hex_bytes(reinterpret_cast<void*>(kMemberArray), 0x20);
        scratch_before = hex_bytes(pool + 0x10000, 0x70000);
        if (id == 12) {
            result = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(
                application_context_copy_range_005299d0(
                    reinterpret_cast<void*>(kMemberArray + 4), nullptr,
                    reinterpret_cast<void*>(kMemberArray))));
        } else if (id == 13) {
            application_context_range_link_00529a20(
                reinterpret_cast<void*>(kMemberArray), nullptr,
                reinterpret_cast<std::uint32_t*>(kMemberArray + 4));
        } else {
            const auto end = id == 14 ? kMemberArray + 12 :
                (id == 15 ? kMemberArray - 4 : kMemberArray);
            application_context_initialize_blocks_00529a40(
                reinterpret_cast<std::uint32_t*>(kMemberArray),
                reinterpret_cast<std::uint32_t*>(end));
        }
        after = hex_bytes(reinterpret_cast<void*>(kMemberArray), 0x20);
    }
    print_result(id, before, after, result, base_ctor_result, member_ctor_result, scratch_before);
    return 0;
}
