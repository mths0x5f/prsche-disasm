#include "porsche/application_audio_lifecycle.hpp"
#include "porsche/application_state.hpp"
#include "porsche/engine_service_427a60.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/frame_services.hpp"
#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <vector>

namespace porsche {
ApplicationAudioDeviceStateStorage application_audio_device_state_006b48c0{};
const char* lifecycle_fixture_root = "";
const char*& engine_service_root_0065b360 = lifecycle_fixture_root;
std::uint8_t lifecycle_fixture_flags[2]{};
std::uint8_t& frame_services_byte_00656868 = lifecycle_fixture_flags[0];
std::uint8_t& frame_services_byte_00656869 = lifecycle_fixture_flags[1];
namespace {
std::vector<std::array<std::uint32_t,6>> events;
std::uint32_t mutation=0,initialized=0,allocation=0;
void record(std::uint32_t id,std::uint32_t a=0,std::uint32_t b=0,
 std::uint32_t c=0,std::uint32_t d=0,std::uint32_t e=0) {
 events.push_back({id,a,b,c,d,e});
}
void put(std::size_t offset,std::uint32_t value) {
 std::memcpy(application_audio_device_state_006b48c0.data()+offset,&value,4);
}
std::uint32_t get(std::size_t offset) {
 std::uint32_t value;std::memcpy(&value,application_audio_device_state_006b48c0.data()+offset,4);return value;
}
void __cdecl callback3();
void __cdecl callback0() {record(20);if(mutation&2)put(0x13c,static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(&callback3)));}
void __cdecl callback1() {record(21);if(mutation&4)put(0x134,0);}
void __cdecl callback2() {record(22);}
void __cdecl callback3() {record(23);}
void __cdecl callback4(std::int32_t value) {record(24,static_cast<std::uint32_t>(value));}
template<class T>std::uint32_t pointer(T f) {return static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(f));}
std::uint32_t normalize(std::uint32_t value) {
 const std::array<std::uint32_t,5> targets={pointer(&callback0),pointer(&callback1),pointer(&callback2),pointer(&callback3),pointer(&callback4)};
 for(std::size_t i=0;i<targets.size();++i)if(value==targets[i])return 0x02100100u+static_cast<std::uint32_t>(i)*0x100u;
 return value;
}
}
void* __cdecl allocate_00531ca0(const char* name,std::int32_t bytes,std::uint32_t mode) {
 record(1,name && std::strcmp(name,"audio heap")==0?0x5d13ec:0,static_cast<std::uint32_t>(bytes),mode);
 return reinterpret_cast<void*>(static_cast<std::uintptr_t>(allocation?0x23000000:0));
}
std::uint32_t __cdecl free_00531f90(void* address) {record(2,pointer(address));return 0x71717171;}
std::uint8_t __cdecl application_audio_probe_initialize_004a66b0() {record(3);return static_cast<std::uint8_t>(initialized);}
void __cdecl application_audio_probe_configure_004ae100(std::int32_t a,std::uint32_t b,std::uint32_t c) {record(4,static_cast<std::uint32_t>(a),b,c);}
void __cdecl application_audio_probe_start_004a8b80() {record(5);}
void __cdecl application_audio_probe_prepare_004ae2b0() {record(6);}
void __cdecl application_audio_transition_configure_004ae010(std::uint32_t a,std::uint32_t b) {record(7,a,b);}
void __cdecl application_audio_transition_finish_004ae4d0(std::uint32_t a,std::uint32_t b) {record(8,a,b);}
std::int32_t __cdecl application_audio_stop_channel_005659f0(std::int32_t a) {record(9,static_cast<std::uint32_t>(a));return -8;}
void __cdecl application_audio_period_control_00565c70(std::uint32_t a,std::uint32_t b,std::uint32_t c,std::uint32_t d,std::uint32_t e) {
 record(10,a,b,c,d,e);if(mutation&1)application_audio_auxiliary_006568e4=0x76543210;
}
void __cdecl application_audio_backend_quiet_0058ff10() {record(11);if(mutation&8)put(0x130,pointer(&callback4));}
void __cdecl application_audio_backend_stop_device_0058fe80() {record(12);if(mutation&16)put(0x140,0xa0a0a0a0);}
void __cdecl application_audio_backend_release_0058ac30(std::uint32_t address) {record(13,address);if(mutation&32)put(0x144,0xb0b0b0b0);}
void __cdecl application_audio_backend_stop_0058e2e0() {record(14);}
std::int32_t __cdecl application_audio_backend_close_0058aac0() {record(15);return -123;}
std::int32_t __cdecl application_service_message_box_api(const char*,const char*) {record(90);return 0;}
std::int32_t __cdecl application_service_create_directory_api(const char*) {record(91);return 0;}
}
using namespace porsche;
int main() {
 if(&application_audio_post_init_byte_00656868!=&frame_services_byte_00656868 ||
    &application_audio_post_init_byte_00656869!=&frame_services_byte_00656869)return 6;
 std::array<std::uint32_t,16> v{};
 while(std::cin>>v[0]) {
  for(std::size_t i=1;i<v.size();++i)if(!(std::cin>>v[i]))return 2;
  events.clear();mutation=v[15];initialized=v[13];allocation=v[14];
  auto& state=application_audio_device_state_006b48c0;
  for(std::size_t i=0;i<state.backing.size();++i)state.backing[i]=static_cast<std::uint8_t>(i*29+7);
  application_state_006573e8.words().fill(0xabababab);
  application_state_006573e8.word(0x657c94)=0x12345678;
  application_state_006573e8.word(0x657c98)=v[5];
  application_state_006573e8.word(0x657c9c)=0xcccccccc;
  application_audio_mode_00655d38=v[5];application_audio_config_00655d34=v[6];
  application_audio_flag_00655d3c=static_cast<std::uint8_t>(v[7]);application_audio_buffer_00655d44=v[8];
  application_audio_auxiliary_006568e4=v[9];application_audio_active_005d1734=0x55555555;
  application_audio_device_configured_00655d40=v[10];
  application_audio_post_init_byte_00656868=0x87;application_audio_post_init_byte_00656869=0x98;
  for(std::uint32_t i=0;i<8;++i)application_audio_records_006564a0[i]={0x1000+i,0x2000+i,0x3000+i,0x4000+i};
  application_audio_records_006564a0[7].raw_08=v[10];
  state[0xdc]=static_cast<std::uint8_t>(v[11]);
  const auto mask=v[12];
  put(0x138,mask&1?pointer(&callback0):0);put(0x13c,mask&2?pointer(&callback1):0);
  put(0x134,mask&4?pointer(&callback2):0);put(0x130,mask&8?pointer(&callback4):0);
  put(0x140,0x11111111);put(0x144,0x22222222);
  std::int32_t result=0;
  switch(v[0]) {
  case 0:application_audio_transition_004a6a00(v[1],0xdeadbeef,v[2],v[3],v[4]);break;
  case 1:application_audio_probe_finish_004ab4b0();break;
  case 2:result=application_audio_probe_measure_00565890();break;
  case 3:application_audio_post_setup_004ab470();break;
  case 4:application_audio_setup_004a6840(static_cast<std::int32_t>(v[3]),v[4]);break;
  default:return 3;
  }
  // Normalize only the five fixture callback identities, not arbitrary cells.
  auto audio=state.backing;
  for(const auto offset:{0x130u,0x134u,0x138u,0x13cu}) {
   const auto value=normalize(get(offset));std::memcpy(audio.data()+0x10+offset,&value,4);
  }
  std::cout<<"{\"result\":"<<result<<",\"trace\":[";
  for(std::size_t i=0;i<events.size();++i) {
   if(i)std::cout<<',';std::cout<<'[';
   for(std::size_t j=0;j<6;++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';
  }
  std::cout<<"],\"arena\":[";
  for(std::size_t i=0;i<application_state_word_count;++i) {if(i)std::cout<<',';std::cout<<application_state_006573e8.words()[i];}
  std::cout<<"],\"records\":[";
  std::uint32_t words[32];std::memcpy(words,application_audio_records_006564a0,sizeof words);
  for(std::size_t i=0;i<32;++i){if(i)std::cout<<',';std::cout<<words[i];}
  std::cout<<"],\"outside\":["<<application_audio_config_00655d34<<','<<application_audio_mode_00655d38<<','
   <<static_cast<unsigned>(application_audio_flag_00655d3c)<<','<<application_audio_buffer_00655d44<<','
   <<application_audio_auxiliary_006568e4<<','<<application_audio_active_005d1734<<','
   <<application_audio_device_configured_00655d40<<','<<static_cast<unsigned>(application_audio_post_init_byte_00656868)<<','
   <<static_cast<unsigned>(application_audio_post_init_byte_00656869)<<"],\"audio\":[";
  for(std::size_t i=0;i<audio.size();++i){if(i)std::cout<<',';std::cout<<static_cast<unsigned>(audio[i]);}
  std::cout<<"]}\n";
 }
}
