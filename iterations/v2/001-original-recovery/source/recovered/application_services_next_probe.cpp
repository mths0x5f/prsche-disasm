#include "porsche/application_services_next.hpp"
#include "porsche/application_services.hpp"
#include "porsche/application_state.hpp"
#include "porsche/startup_services.hpp"

#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace porsche {
// Private fixture ownership for the deliberately unresolved original storage.
std::uint32_t application_audio_source_storage_005e8bfc[16]{};
void* startup_network_00628c70 = nullptr;
namespace {
using U = std::uint32_t;
std::array<U, 64> network_a{}, network_b{};
U lock_a = 0x11110000, lock_b = 0x22220000;
std::vector<std::vector<U>> events;
std::array<U, 12> args{};
U operation = 0;
U message_count = 0;
U norm(const void* p) {
    if (p == network_a.data()) return 0x23000000;
    if (p == network_b.data()) return 0x23001000;
    if (p == &lock_a) return 0x23002000;
    if (p == &lock_b) return 0x23002004;
    return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));
}
U word(const void* p, U offset) { U v; std::memcpy(&v, static_cast<const std::uint8_t*>(p) + offset, 4); return v; }
void put(void* p, U offset, U value) { std::memcpy(static_cast<std::uint8_t*>(p) + offset, &value, 4); }
void putbyte(void* p, U offset, U value) { static_cast<std::uint8_t*>(p)[offset] = static_cast<std::uint8_t>(value); }
void event(U id, std::initializer_list<U> values = {}) {
    std::vector<U> row{id}; row.insert(row.end(), values); events.push_back(row);
}
void init_network(std::array<U,64>& n, U index) {
    n.fill(0xa0a00000u + index);
    put(n.data(),8,args[1]); putbyte(n.data(),0xbf,args[2]); putbyte(n.data(),0xbd,args[3]);
    put(n.data(),0xc,0x24000000u + index * 0x1000u);
    put(n.data(),0x10, static_cast<U>(reinterpret_cast<std::uintptr_t>(index ? &lock_b : &lock_a)));
}
U normalize_word(U v) { return norm(reinterpret_cast<void*>(static_cast<std::uintptr_t>(v))); }
}

void __cdecl application_audio_shutdown_channels_005659f0(std::int32_t channel) {
    event(0x5659f0,{static_cast<U>(channel)});
    if (args[6] & 1) application_audio_records_006564a0[7].raw_08 = 0x23003100;
}
std::uint32_t __cdecl free_00531f90(void* p) {
    event(0x531f90,{norm(p)});
    if (args[6] & 2) application_audio_buffer_00655d44 = 0x23003200;
    return 1;
}
void __cdecl application_audio_shutdown_device_004ae310() {
    event(0x4ae310);
    if (args[6] & 4) {
        application_audio_active_005d1734 = 1;
        application_audio_buffer_00655d44 = 0x23003300;
    }
}
void __cdecl application_audio_probe_finish_004ab4b0() {
    event(0x4ab4b0);
    if (args[6] & 8) application_audio_buffer_00655d44 = 0x23003400;
}
std::int32_t __cdecl application_audio_probe_measure_00565890() {
    event(0x565890);
    if (args[6] & 16) application_audio_buffer_00655d44 = 0x23003500;
    std::int32_t value; std::memcpy(&value, &args[5], 4); return value;
}
void __cdecl startup_sequence_report_005a177b(U format, U value) {
    event(0x5a177b,{format,value,application_audio_buffer_00655d44});
}
void __cdecl heap_enter_005322b0(void* lock) {
    event(0x5322b0,{norm(lock)});
    if (operation == 2 && (args[4] & 1)) startup_network_00628c70 = network_b.data();
    if (operation == 2 && (args[4] & 2)) lock_a = 0x33330000;
}
void __cdecl heap_leave_005322c0(void* lock) {
    event(0x5322c0,{norm(lock)});
    if (operation == 2 && (args[4] & 4)) startup_network_00628c70 = network_a.data();
}
void __fastcall application_network_message_0048c870(void* receiver,void*,U message,U first,U second,U third,U fourth) {
    event(0x48c870,{norm(receiver),message,first,second,third,fourth});
    ++message_count;
    if (operation == 2 && (args[4] & 8) && message_count == 1)
        putbyte(startup_network_00628c70,0xbf,1);
    if (operation == 2 && (args[4] & 16) && message_count == 1)
        startup_network_00628c70 = network_b.data();
}
void __fastcall application_network_reset_0048e9c0(void* receiver, void*) {
    event(0x48e9c0,{norm(receiver)});
    if (args[3] == 1) startup_network_00628c70 = nullptr;
    if (args[3] == 2) startup_network_00628c70 = network_b.data();
}
void __fastcall application_network_change_0048e1a0(void* receiver,void*,U mode,U first,U second) {
    event(0x48e1a0,{norm(receiver),mode,first,second});
}
void __fastcall application_network_member_destroy_004935c0(void* receiver,void*) {
    event(0x4935c0,{norm(receiver)});
    if (args[4]) put(network_a.data(),0xc,0x24004000);
}
U __cdecl application_release_0059f050(void* address) {
    event(0x59f050,{norm(address),word(network_a.data(),0x14)}); return 1;
}

// Link-only private controls for Run128's unchanged owner TU. None of these
// effects can be reached by this packet's four function bodies.
void* __cdecl allocate_00531ca0(const char*,std::int32_t,U) { std::abort(); }
std::uint8_t __cdecl application_audio_probe_initialize_004a66b0() { std::abort(); }
void __cdecl application_audio_probe_configure_004ae100(std::int32_t,U,U) { std::abort(); }
void __cdecl application_audio_probe_start_004a8b80() { std::abort(); }
void __cdecl application_audio_probe_prepare_004ae2b0() { std::abort(); }
std::int32_t __cdecl application_service_message_box_api(const char*,const char*) { std::abort(); }
std::int32_t __cdecl application_service_create_directory_api(const char*) { std::abort(); }
}

int main() {
    using namespace porsche;
    std::string line;
    while (std::getline(std::cin,line)) {
        std::istringstream input(line); input >> operation;
        args.fill(0); for (auto& value : args) input >> value;
        events.clear(); message_count = 0;
        application_state_006573e8.words().fill(0xababababu);
        for (std::size_t i = 0; i < application_audio_reset_storage_00655d48.size(); ++i)
            application_audio_reset_storage_00655d48[i] = 0x70000000u + static_cast<U>(i);
        for (U i = 0; i < 8; ++i)
            application_audio_records_006564a0[i] = {0x1000u+i,0x2000u+i,0x3000u+i,0x4000u+i};
        application_audio_buffer_00655d44 = 0x12345678;
        application_audio_active_005d1734 = 0x55555555;
        application_audio_secondary_active_005d1738 = 0x66666666;
        lock_a = 0x11110000; lock_b = 0x22220000;
        init_network(network_a,0); init_network(network_b,1);
        startup_network_00628c70 = network_a.data();
        if (operation == 0) {
            application_audio_records_006564a0[7].raw_08 = args[0];
            application_audio_records_006564a0[7].raw_00 = args[1];
            application_audio_active_005d1734 = args[2];
            application_audio_secondary_active_005d1738 = args[3];
            application_audio_buffer_00655d44 = args[4];
            application_main_function_004a6960();
        } else if (operation == 1) {
            application_state_006573e8.word(0x657404) = args[0];
            application_state_006573e8.word(0x65741c) = args[1];
            application_audio_source_storage_005e8bfc[0] = args[2];
            for (U i = 1; i < 16; ++i) application_audio_source_storage_005e8bfc[i] = 0x81000000u + i * 0x12345u;
            application_main_function_004a6e30();
        } else if (operation == 2) {
            if (!args[0]) startup_network_00628c70 = nullptr;
            application_main_function_0048dad0();
        } else {
            put(network_a.data(),0x28,args[0]); putbyte(network_a.data(),0xc6,args[1]);
            put(network_a.data(),0x14,args[2] ? 0x25000000u : 0);
            if (args[5] == 1) startup_network_00628c70 = nullptr;
            if (args[5] == 2) startup_network_00628c70 = network_b.data();
            if (operation == 4) application_main_function_0048e6f0();
            else application_network_close_0048e6f0(network_a.data(),nullptr);
        }
        std::cout << "{\"trace\":[";
        for (std::size_t i=0;i<events.size();++i) {
            if(i)std::cout<<','; std::cout<<'[';
            for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}
            std::cout<<']';
        }
        std::cout<<"],\"state\":[";
        bool first=true;
        const auto emit=[&](U v){if(!first)std::cout<<',';first=false;std::cout<<v;};
        for(auto v:application_state_006573e8.words())emit(v);
        for(auto v:application_audio_reset_storage_00655d48)emit(v);
        for(const auto& r:application_audio_records_006564a0){emit(r.raw_00);emit(r.opaque_04);emit(r.raw_08);emit(r.opaque_0c);}
        emit(application_audio_buffer_00655d44);emit(application_audio_active_005d1734);emit(application_audio_secondary_active_005d1738);
        for(auto v:network_a)emit(normalize_word(v));for(auto v:network_b)emit(normalize_word(v));
        emit(norm(startup_network_00628c70));emit(lock_a);emit(lock_b);
        std::cout<<"]}\n";
    }
}
