#pragma once
#include <cstddef>
#include <cstdint>

namespace porsche {
// Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
struct DiagnosticDevice { std::uint32_t callback, flags, name; }; // name of following physical entry
struct DiagnosticChannel { std::uint32_t name, flags; };
static_assert(sizeof(DiagnosticDevice)==12 && sizeof(DiagnosticChannel)==8);
struct DiagnosticDeviceImage { std::uint32_t preceding_name; DiagnosticDevice devices[8]; };
static_assert(sizeof(DiagnosticDeviceImage)==100 && offsetof(DiagnosticDeviceImage,devices)==4);
extern DiagnosticDeviceImage application_diagnostic_device_image_005e1c88;
extern DiagnosticDevice (&application_diagnostic_devices_005e1c8c)[8];
extern DiagnosticChannel application_diagnostic_channels_005df4a0[64];
extern std::uint32_t application_diagnostic_started_006a57cc;

// Unrecovered original child bodies. The fixture supplies controlled probes.
void __cdecl application_diagnostic_device_set_0055ed20(std::uint32_t,std::uint32_t);
void __cdecl application_diagnostic_device_parse_0055ed50(const char*);
void __cdecl application_diagnostic_channel_set_0055efd0(std::uint32_t,std::uint32_t);
void __cdecl application_diagnostic_channel_parse_0055f060(const char*);
const char* __cdecl application_diagnostic_environment_005a3050(const char*);
void __cdecl application_diagnostic_device_callback_00586ca0(std::uint32_t,const char*);
void __cdecl application_diagnostic_device_callback_00586cb0(std::uint32_t,const char*);
void __cdecl application_diagnostic_device_callback_00586cc0(std::uint32_t,const char*);
}
