// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
// Run 429 differential fixture TEMPLATE for the corrected 00413ea0. Derived from
// Run 401's fixture. experiment-v2-frame-clock-429.py fills in the original
// 296 bytes and the absolute/rel32 operand sites from the PE at build time, so
// no game bytes are versioned here. Not part of the game graph.
#include "frame_clock_401.hpp"
#include "porsche/application_main.hpp"

using U = std::uint32_t;
static_assert(sizeof(void*) == 4, "32-bit x86 ABI required");

extern "C" void* __stdcall VirtualAlloc(void* address, U size, U allocation_type, U protect);
extern "C" int __stdcall VirtualFree(void* address, U size, U free_type);
extern "C" void __stdcall ExitProcess(U exit_code);

namespace {

void mem_fill(void* dst, std::uint8_t val, std::size_t n) {
    auto* p = static_cast<std::uint8_t*>(dst);
    for (std::size_t i = 0; i < n; ++i) p[i] = val;
}

void mem_copy(void* dst, const void* src, std::size_t n) {
    auto* d = static_cast<std::uint8_t*>(dst);
    const auto* s = static_cast<const std::uint8_t*>(src);
    for (std::size_t i = 0; i < n; ++i) d[i] = s[i];
}

bool mem_equal(const void* a, const void* b, std::size_t n) {
    const auto* pa = static_cast<const std::uint8_t*>(a);
    const auto* pb = static_cast<const std::uint8_t*>(b);
    for (std::size_t i = 0; i < n; ++i) {
        if (pa[i] != pb[i]) return false;
    }
    return true;
}

void write_u32_raw(std::uint8_t* dst, U v) {
    mem_copy(dst, &v, 4);
}

const std::uint8_t kOriginalBytes[296] = { /*@ORIGINAL_BYTES@*/ };

struct SlabReloc {
    U offset;
    U is_rel32;
    U target_va;
};

const SlabReloc kSlabRelocs[/*@RELOC_COUNT@*/] = {
/*@SLAB_RELOCS@*/
};

std::uint8_t* g_exec_slab = nullptr;
U g_failures = 0;
U g_cases_passed = 0;

void require(bool cond) {
    if (!cond) {
        ++g_failures;
        ExitProcess(1u);
    }
}

struct EventRecord {
    U tag;
    U a;
    U b;
};

struct TraceLog {
    U count;
    EventRecord events[64];
};

TraceLog g_trace;

void record_event(U tag, U a = 0u, U b = 0u) {
    if (g_trace.count < 64u) {
        g_trace.events[g_trace.count++] = EventRecord{tag, a, b};
    }
}

// Call wrapper state
U g_saved_sp, g_saved_bp, g_saved_bx, g_saved_si, g_saved_di;
U g_entry_sp, g_seen_sp, g_seen_eax, g_seen_bp, g_seen_bx, g_seen_si, g_seen_di, g_seen_flags;
U g_call_target;

__declspec(naked) void invoke_target() {
    __asm {
        mov g_saved_sp, esp
        mov g_saved_bp, ebp
        mov g_saved_bx, ebx
        mov g_saved_si, esi
        mov g_saved_di, edi
        mov ebp, 13579bdfh
        mov ebx, 2468ace0h
        mov esi, 89abcdefh
        mov edi, 0fedcba98h
        mov eax, esp
        sub eax, 4
        mov g_entry_sp, eax
        cld
        call dword ptr g_call_target
        mov g_seen_eax, eax
        mov g_seen_sp, esp
        mov g_seen_bp, ebp
        mov g_seen_bx, ebx
        mov g_seen_si, esi
        mov g_seen_di, edi
        pushfd
        pop g_seen_flags
        mov esp, g_saved_sp
        mov ebp, g_saved_bp
        mov ebx, g_saved_bx
        mov esi, g_saved_si
        mov edi, g_saved_di
        ret
    }
}

void call_void_0(U target) {
    g_call_target = target;
    invoke_target();
    require(g_seen_sp == g_entry_sp + 4u);
    require(g_seen_bp == 0x13579bdfu);
    require(g_seen_bx == 0x2468ace0u);
    require(g_seen_si == 0x89abcdefu);
    require(g_seen_di == 0xfedcba98u);
    require((g_seen_flags & 0x400u) == 0u);
}

// Mock state and global definitions
U g_mock_predicate_result = 1u;
U g_mock_sample_counter = 100u;
int g_count_delta = 0;   // added to 005e8bfc by every 00413960 call
porsche::FrameClockEntityContext g_mock_entities[8];

} // namespace

namespace porsche {

std::uint32_t global_005e99f4 = 0u;
std::uint32_t frame_clock_counter_005e99f8 = 0u;
std::uint32_t frame_clock_flag_005e99fc = 0u;
std::uint32_t frame_clock_step_accum_005e9a00 = 0u;
std::uint32_t frame_clock_substep_005e9a04 = 0u;

std::uint32_t frame_clock_rate_00606850 = 0u;
std::uint32_t frame_clock_subticks_00606854 = 0u;
std::uint32_t frame_clock_ticks_00606858 = 0u;
std::uint32_t frame_clock_flags_00606860 = 0u;
std::uint32_t frame_clock_state_00606864 = 0u;
std::uint32_t frame_clock_var_00606868 = 0u;
std::uint32_t frame_clock_var_0060686c = 0u;
std::uint32_t frame_clock_var_00606870 = 0u;

std::uint32_t frame_clock_arena_005ed848[0x6400];
std::uint32_t g_session_cell_006573e8 = 0u;
std::uint32_t& global_006573e8 = g_session_cell_006573e8;
std::uint32_t frame_clock_tick_cell_0065741c = 0u;

std::int32_t frame_clock_entity_count_005e8bfc = 0;
FrameClockEntityContext* frame_clock_entities_005e8c00[64];

// Cutpoints
std::uint32_t __cdecl frame_clock_predicate_0046d960() {
    record_event(0x46d9u, g_mock_predicate_result, 0u);
    return g_mock_predicate_result;
}

std::uint32_t __cdecl frame_clock_sample_time_0046d890() {
    const U val = ++g_mock_sample_counter;
    record_event(0x46d8u, val, 0u);
    return val;
}

void __cdecl frame_clock_dispatch_step_00413960(std::uint32_t clock_val) {
    record_event(0x4139u, clock_val, static_cast<U>(frame_clock_entity_count_005e8bfc));
    frame_clock_entity_count_005e8bfc += g_count_delta;
    if (frame_clock_entity_count_005e8bfc > 6) g_count_delta = 0;
}

void __cdecl frame_clock_adjust_rate_004659e0(std::uint32_t zero, std::uint32_t step) {
    record_event(0x4659u, zero, step);
}

} // namespace porsche

namespace {

U resolve_symbol_va(U target_va) {
    using namespace porsche;
    switch (target_va) {
    case 0x005e99f4u: return reinterpret_cast<U>(&global_005e99f4);
    case 0x005e99f8u: return reinterpret_cast<U>(&frame_clock_counter_005e99f8);
    case 0x005e99fcu: return reinterpret_cast<U>(&frame_clock_flag_005e99fc);
    case 0x005e9a00u: return reinterpret_cast<U>(&frame_clock_step_accum_005e9a00);
    case 0x005e9a04u: return reinterpret_cast<U>(&frame_clock_substep_005e9a04);

    case 0x00606850u: return reinterpret_cast<U>(&frame_clock_rate_00606850);
    case 0x00606854u: return reinterpret_cast<U>(&frame_clock_subticks_00606854);
    case 0x00606858u: return reinterpret_cast<U>(&frame_clock_ticks_00606858);
    case 0x00606860u: return reinterpret_cast<U>(&frame_clock_flags_00606860);
    case 0x00606864u: return reinterpret_cast<U>(&frame_clock_state_00606864);
    case 0x00606868u: return reinterpret_cast<U>(&frame_clock_var_00606868);
    case 0x0060686cu: return reinterpret_cast<U>(&frame_clock_var_0060686c);
    case 0x00606870u: return reinterpret_cast<U>(&frame_clock_var_00606870);

    case 0x005ed848u: return reinterpret_cast<U>(frame_clock_arena_005ed848);
    case 0x006573e8u: return reinterpret_cast<U>(&g_session_cell_006573e8);
    case 0x0065741cu: return reinterpret_cast<U>(&frame_clock_tick_cell_0065741c);

    case 0x005e8bfcu: return reinterpret_cast<U>(&frame_clock_entity_count_005e8bfc);
    case 0x005e8c00u: return reinterpret_cast<U>(frame_clock_entities_005e8c00);

    // Cutpoints
    case 0x0046d960u: return reinterpret_cast<U>(&frame_clock_predicate_0046d960);
    case 0x0046d890u: return reinterpret_cast<U>(&frame_clock_sample_time_0046d890);
    case 0x00413960u: return reinterpret_cast<U>(&frame_clock_dispatch_step_00413960);
    case 0x004659e0u: return reinterpret_cast<U>(&frame_clock_adjust_rate_004659e0);
    default:
        require(false);
        return 0u;
    }
}

void init_executable_pe_slab() {
    g_exec_slab = static_cast<std::uint8_t*>(VirtualAlloc(nullptr, 4096u, 0x3000u, 0x40u));
    require(g_exec_slab != nullptr);
    mem_copy(g_exec_slab, kOriginalBytes, sizeof(kOriginalBytes));
    for (std::size_t i = 0; i < sizeof(kSlabRelocs) / sizeof(kSlabRelocs[0]); ++i) {
        const auto& r = kSlabRelocs[i];
        const U resolved = resolve_symbol_va(r.target_va);
        require(resolved != 0u);
        if (r.is_rel32) {
            const U next_ip = reinterpret_cast<U>(g_exec_slab + r.offset + 4u);
            const U rel = resolved - next_ip;
            write_u32_raw(g_exec_slab + r.offset, rel);
        } else {
            write_u32_raw(g_exec_slab + r.offset, resolved);
        }
    }
}

struct Snapshot {
    TraceLog trace;
    U mode;
    U counter;
    U flag;
    U step_accum;
    U substep;
    U rate;
    U subticks;
    U ticks;
    U flags;
    U state;
    U var68;
    U var6c;
    U var70;
    U arena_sample[4];
    U entity_values[8];
};

Snapshot g_snap_orig;
Snapshot g_snap_cpp;

void capture_snapshot(Snapshot& s) {
    using namespace porsche;
    mem_fill(&s, 0, sizeof(s));
    s.trace = g_trace;
    s.mode = global_005e99f4;
    s.counter = frame_clock_counter_005e99f8;
    s.flag = frame_clock_flag_005e99fc;
    s.step_accum = frame_clock_step_accum_005e9a00;
    s.substep = frame_clock_substep_005e9a04;
    s.rate = frame_clock_rate_00606850;
    s.subticks = frame_clock_subticks_00606854;
    s.ticks = frame_clock_ticks_00606858;
    s.flags = frame_clock_flags_00606860;
    s.state = frame_clock_state_00606864;
    s.var68 = frame_clock_var_00606868;
    s.var6c = frame_clock_var_0060686c;
    s.var70 = frame_clock_var_00606870;
    s.arena_sample[0] = frame_clock_arena_005ed848[0];
    s.arena_sample[1] = frame_clock_arena_005ed848[1];
    s.arena_sample[2] = frame_clock_arena_005ed848[0x3200];
    s.arena_sample[3] = frame_clock_arena_005ed848[0x63ff];
    for (int i = 0; i < 8; ++i) {
        s.entity_values[i] = g_mock_entities[i].clock_value_10e4;
    }
}

void reset_globals() {
    using namespace porsche;
    mem_fill(&g_trace, 0, sizeof(g_trace));
    global_005e99f4 = 0u;
    frame_clock_counter_005e99f8 = 0x11111111u;
    frame_clock_flag_005e99fc = 0x22222222u;
    frame_clock_step_accum_005e9a00 = 0x33333333u;
    frame_clock_substep_005e9a04 = 0x44444444u;
    frame_clock_rate_00606850 = 0x55555555u;
    frame_clock_subticks_00606854 = 0x66666666u;
    frame_clock_ticks_00606858 = 0x77777777u;
    frame_clock_flags_00606860 = 0x88888888u;
    frame_clock_state_00606864 = 0x99999999u;
    frame_clock_var_00606868 = 0xaaaaaaaau;
    frame_clock_var_0060686c = 0xbbbbbbbbu;
    frame_clock_var_00606870 = 0xccccccccu;

    mem_fill(frame_clock_arena_005ed848, 0xef, sizeof(frame_clock_arena_005ed848));
    global_006573e8 = 0u;
    frame_clock_tick_cell_0065741c = 0x12345678u;

    frame_clock_entity_count_005e8bfc = 0;
    for (int i = 0; i < 8; ++i) {
        mem_fill(&g_mock_entities[i], 0, sizeof(g_mock_entities[i]));
        g_mock_entities[i].clock_value_10e4 = 0x500u + static_cast<U>(i);
        frame_clock_entities_005e8c00[i] = &g_mock_entities[i];
    }

    g_mock_predicate_result = 1u;
    g_mock_sample_counter = 100u;
    g_count_delta = 0;
}

void setup_case(U case_id) {
    using namespace porsche;
    reset_globals();
    if (case_id == 0u) {
        // Mode 0: arena clear, ticks reset
        global_005e99f4 = 0u;
        frame_clock_tick_cell_0065741c = 0xaabbcc01u;
    } else if (case_id == 1u) {
        // Mode 1: arena clear, ticks reset
        global_005e99f4 = 1u;
        frame_clock_tick_cell_0065741c = 0xaabbcc02u;
    } else if (case_id == 2u) {
        // Mode -1 (signed < 2): early exit
        global_005e99f4 = static_cast<U>(-1);
    } else if (case_id == 3u) {
        // Mode 2, predicate 1, session != 9, 3 entities
        global_005e99f4 = 2u;
        frame_clock_tick_cell_0065741c = 0x33330000u;
        g_mock_predicate_result = 1u;
        global_006573e8 = 0u;
        frame_clock_entity_count_005e8bfc = 3;
    } else if (case_id == 4u) {
        // Mode 2, predicate 1, session == 9 (race session adjust rate path)
        global_005e99f4 = 2u;
        frame_clock_tick_cell_0065741c = 0x44440000u;
        g_mock_predicate_result = 1u;
        global_006573e8 = 9u;
        frame_clock_entity_count_005e8bfc = 4;
    } else if (case_id == 5u) {
        // Mode 3, predicate 0 (fallback rate 10 adjust path)
        global_005e99f4 = 3u;
        frame_clock_tick_cell_0065741c = 0x55550000u;
        g_mock_predicate_result = 0u;
        global_006573e8 = 0u;
    } else if (case_id == 6u) {
        // Mode 4, predicate 1, session != 9, count 0
        global_005e99f4 = 4u;
        frame_clock_tick_cell_0065741c = 0x66660000u;
        g_mock_predicate_result = 1u;
        global_006573e8 = 5u;
        frame_clock_entity_count_005e8bfc = 0;
    } else if (case_id == 7u) {
        // The dispatch shrinks the count: the loop must stop on the re-read value.
        global_005e99f4 = 2u;
        frame_clock_tick_cell_0065741c = 0x77770000u;
        g_mock_predicate_result = 1u;
        global_006573e8 = 0u;
        frame_clock_entity_count_005e8bfc = 5;
        g_count_delta = -2;
    } else if (case_id == 8u) {
        // The dispatch grows the count: the loop must run past the first value.
        global_005e99f4 = 2u;
        frame_clock_tick_cell_0065741c = 0x88880000u;
        g_mock_predicate_result = 1u;
        global_006573e8 = 0u;
        frame_clock_entity_count_005e8bfc = 2;
        g_count_delta = 1;
    }
}

void run_all_cases() {
    using namespace porsche;
    for (U c = 0; c < 9u; ++c) {
        setup_case(c);
        call_void_0(reinterpret_cast<U>(g_exec_slab));
        capture_snapshot(g_snap_orig);

        setup_case(c);
        call_void_0(reinterpret_cast<U>(&application_main_function_00413ea0));
        capture_snapshot(g_snap_cpp);

        require(mem_equal(&g_snap_orig, &g_snap_cpp, sizeof(Snapshot)));
        ++g_cases_passed;
    }
}

} // namespace

extern "C" void __stdcall entry() {
    init_executable_pe_slab();
    run_all_cases();
    VirtualFree(g_exec_slab, 0u, 0x8000u);
    ExitProcess((g_failures == 0u && g_cases_passed == 9u) ? 0u : 1u);
}
