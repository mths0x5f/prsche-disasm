#include "diagnostic_devices.hpp"
#include "porsche/application_heap.hpp"
#include <cstdint>

namespace porsche {
namespace {
using U=std::uint32_t;
static_assert(sizeof(void*)==4,"original x86 records");
U word(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
// Exact PE read-only spans keep interior pointers and string adjacency.
const unsigned char channel_labels_005bcbe4[]={
    0x63,0x61,0x70,0x74,0x75,0x72,0x65,0x00,0x65,0x61,0x67,0x6c,0x00,0x00,0x00,0x00,
    0x6d,0x61,0x74,0x68,0x00,0x00,0x00,0x00,0x63,0x6f,0x64,0x65,0x63,0x00,0x00,0x00,
    0x66,0x6f,0x6e,0x74,0x00,0x00,0x00,0x00,0x33,0x64,0x00,0x00,0x73,0x79,0x73,0x74,
    0x65,0x6d,0x00,0x00,0x69,0x6e,0x70,0x75,0x74,0x00,0x00,0x00,0x66,0x69,0x6c,0x65,
    0x00,0x00,0x00,0x00,0x67,0x72,0x61,0x70,0x68,0x69,0x63,0x73,0x00,0x00,0x00,0x00,
    0x63,0x6f,0x6e,0x6e,0x65,0x63,0x74,0x69,0x6f,0x6e,0x00,0x00,0x6d,0x65,0x6d,0x6f,
    0x72,0x79,0x00,0x00,0x67,0x65,0x6e,0x65,0x72,0x61,0x6c,0x00,0x61,0x6c,0x65,0x72,
    0x74,0x00,0x00,0x00,0x72,0x65,0x61,0x6c,0x00,0x00,0x00,0x00,0x61,0x6c,0x6c,0x00,
    0x50,0x52,0x49,0x4e,0x54,0x5f,0x44,0x45,0x56,0x49,0x43,0x45,0x00,0x00,0x00,0x00,
    0x20,0x2c,0x00,0x00,0x50,0x52,0x49,0x4e,0x54,0x5f,0x43,0x48,0x41,0x4e,0x4e,0x45,
    0x4c,0x00,
};
const unsigned char device_labels_005c1588[]={
    0x64,0x65,0x62,0x75,0x67,0x67,0x65,0x72,0x00,0x00,0x00,0x00,0x63,0x6f,0x6e,0x73,
    0x6f,0x6c,0x65,0x00,0x6d,0x6f,0x6e,0x6f,0x00,
};
static_assert(sizeof(channel_labels_005bcbe4)==0xa2);
static_assert(sizeof(device_labels_005c1588)==0x19);
}

DiagnosticDeviceImage application_diagnostic_device_image_005e1c88={
    reinterpret_cast<U>(device_labels_005c1588+0x14),
    {{reinterpret_cast<U>(&application_diagnostic_device_callback_00586ca0),0,reinterpret_cast<U>(device_labels_005c1588+0x0c)},
    {reinterpret_cast<U>(&application_diagnostic_device_callback_00586cb0),1,reinterpret_cast<U>(device_labels_005c1588)},
    {reinterpret_cast<U>(&application_diagnostic_device_callback_00586cc0),0,0},
    {},{},{},{},{0,0,1}}
};
DiagnosticDevice (&application_diagnostic_devices_005e1c8c)[8]=application_diagnostic_device_image_005e1c88.devices;
DiagnosticChannel application_diagnostic_channels_005df4a0[64]={
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x7c),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x74),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x6c),3},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x64),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x5c),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x50),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x44),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x3c),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x34),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x2c),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x28),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x20),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x18),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x10),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4+0x08),2},
    {reinterpret_cast<U>(channel_labels_005bcbe4),2}
};
U application_diagnostic_started_006a57cc=0;

void __cdecl application_secondary_start(){
    if(application_diagnostic_started_006a57cc!=0)return;
    application_diagnostic_started_006a57cc=1;
    for(auto& device:application_diagnostic_devices_005e1c8c)device.flags&=~1u;
    for(auto& channel:application_diagnostic_channels_005df4a0)channel.flags&=~1u;
    for(U i=3;i<8;++i){
        application_diagnostic_devices_005e1c8c[i-1].name=0;
        application_diagnostic_devices_005e1c8c[i].callback=0;
    }
    for(U i=16;i<64;++i){
        application_diagnostic_channels_005df4a0[i].name=0;
        application_diagnostic_channels_005df4a0[i].flags&=~2u;
    }
    application_heap_kind(2,1);
    application_queue_kind(1,1);
}

void __cdecl application_heap_secondary_stop_0055ec30(){
    if(application_diagnostic_started_006a57cc!=0)application_diagnostic_started_006a57cc=0;
}

void __cdecl application_queue_kind(U index,U enabled){
    if(application_diagnostic_devices_005e1c8c[index].callback==0)return;
    if(application_diagnostic_started_006a57cc==0)application_secondary_start();
    application_diagnostic_device_set_0055ed20(index,enabled);
    const char* value=application_diagnostic_environment_005a3050(
        reinterpret_cast<const char*>(channel_labels_005bcbe4+0x80));
    if(value!=nullptr)application_diagnostic_device_parse_0055ed50(value);
}

void __cdecl application_heap_kind(U index,U enabled){
    if(application_diagnostic_started_006a57cc==0)application_secondary_start();
    application_diagnostic_channel_set_0055efd0(index,enabled);
    const char* value=application_diagnostic_environment_005a3050(
        reinterpret_cast<const char*>(channel_labels_005bcbe4+0x94));
    if(value!=nullptr)application_diagnostic_channel_parse_0055f060(value);
}

void __cdecl application_printf_start(U index,const char* name){
    if(application_diagnostic_started_006a57cc==0)application_secondary_start();
    application_diagnostic_channels_005df4a0[index].name=word(name);
    const char* value=application_diagnostic_environment_005a3050(
        reinterpret_cast<const char*>(channel_labels_005bcbe4+0x94));
    if(value!=nullptr)application_diagnostic_channel_parse_0055f060(value);
}
}
