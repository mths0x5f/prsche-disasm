#include "app_main_subsystem_final_pt1_410.hpp"

namespace porsche {

// =============================================================================
// Function 1: 0056a680 (38 bytes) - Render Frame Counters Initialization
// =============================================================================
void CALL_CDECL render_counters_init_0056a680() {
    g_val_006a5dd4 = 0;
    g_val_006a5dd8 = 0;
    g_val_006a5de0 = 0;
    g_val_006a5de4 = 0;
    g_val_006a5de8 = 0;
    g_val_006a5ddc = g_val_006b7c40;
}

// =============================================================================
#if defined(_MSC_VER) && defined(_M_IX86)
__declspec(naked) std::int64_t CALL_CDECL ftol_005a0f98() {
    __asm {
        push        ebp
        mov         ebp, esp
        add         esp, 0FFFFFFF4h
        wait
        fnstcw      word ptr [ebp-2]
        wait
        mov         ax, word ptr [ebp-2]
        or          ah, 0Ch
        mov         word ptr [ebp-4], ax
        fldcw       word ptr [ebp-4]
        fistp       qword ptr [ebp-0Ch]
        fldcw       word ptr [ebp-2]
        mov         eax, dword ptr [ebp-0Ch]
        mov         edx, dword ptr [ebp-8]
        leave
        ret
    }
#else
    return 0;
#endif
}

// =============================================================================
// Function 3: 00412030 (91 bytes) - Audio Parameters Quad-Value Sync
// =============================================================================
void CALL_CDECL audio_parameters_sync_00412030() {
    if (g_val_005e940c != 0) {
        std::uint32_t idx = g_val_005e9410;
        sub_005338d0(static_cast<std::int32_t>(g_audio_params_005e9420[idx].val_24));
        sub_005338d0(static_cast<std::int32_t>(g_audio_params_005e9420[idx].val_22));
        sub_005338d0(static_cast<std::int32_t>(g_audio_params_005e9420[idx].val_20));
        sub_005338d0(static_cast<std::int32_t>(g_audio_params_005e9420[idx].val_26));
    }
}

// =============================================================================
// Function 4: 00414eb0 (196 bytes) - Session & Frame State Initialization
// =============================================================================
void CALL_CDECL session_state_init_00414eb0() {
    g_val_00606ab8 = 1;
    g_val_00656858 = 0;
    g_val_00606a8c = 0;
    g_val_00606a90 = 0;
    g_val_00606a98 = 0;
    g_val_00606a9c = 0;
    g_val_00606aa0 = 0;
    g_val_00606ac0 = 0;
    g_val_00606ac4 = 0;
    g_val_00657e6c = 0;

    sub_004a4780(g_val_00657a34);
    sub_0044fd00(g_val_00657a34);
    sub_004030b0();
    sub_004069d0();
    sub_004066d0();
    sub_004110a0();
    sub_00406710();
    sub_004069e0();
    sub_004690a0();
    sub_00412150();

    g_val_006280f0 = 0;
    g_val_00606ac8 = g_val_005e99b8;
    g_val_006280ec = 0;
    g_val_006280e8 = 0;
    g_val_00628100 = 0;
    g_val_006280fc = 0;
    g_val_006280f8 = 0;
}

// =============================================================================
// Function 5: 004dd600 (1012 bytes) - Texture Subsystem Surface & Config Setup
// =============================================================================
void CALL_CDECL texture_subsystem_config_004dd600() {
    sub_00467fc0(0x280, 0x1E0, 0x10, 2);
    sub_00560030();

    char path_buf[260];
    sprintf_005a0fbf(path_buf, g_str_005d99bc, g_ptr_0065b32c);

    if (g_ptr_0069ed0c != nullptr) {
        auto obj = *reinterpret_cast<TextureContextObj**>(static_cast<char*>(g_ptr_0069ed0c) + 4);
        if (obj) {
            obj->sub_00536080();
        }
    }

    if (sub_0059dc30(path_buf) != 0) {
        AllocDesc desc = { nullptr, nullptr, nullptr, 0 };
        desc.init_00403520(8);
        if (desc.current != nullptr) {
            *static_cast<char*>(desc.current) = '\0';
        }
        sub_0059e440(path_buf, &desc);

        for (int i = 0; i < 3; ++i) {
            g_pfn_006bd9b0(2);
            g_pfn_006bd91c();
            g_pfn_006bd970();
            g_pfn_006bd948();
            g_pfn_006bd978(0);
        }

        std::uint32_t val_f8 = 0;
        sub_004dc850(desc.start, &val_f8, 0, 3, 0);

        std::size_t sz = reinterpret_cast<std::uintptr_t>(desc.end) - reinterpret_cast<std::uintptr_t>(desc.start);
        if (desc.start != nullptr && sz != 0) {
            sub_004237d0(desc.start, sz, 0);
        }
    }

    if (g_ptr_0069ed0c != nullptr) {
        auto obj = *reinterpret_cast<TextureContextObj**>(static_cast<char*>(g_ptr_0069ed0c) + 4);
        if (obj) {
            obj->sub_00536050();
        }
    }
    sub_004dd4a0();

    sub_00467fc0(0x280, 0x1E0, 0x10, 2);
    sprintf_005a0fbf(path_buf, g_str_005d99ac, g_ptr_0065b334);

    if (sub_0059dc30(path_buf) != 0) {
        void* p_tex = sub_0059d8e0(path_buf, 0, 0);
        char* esi = static_cast<char*>(p_tex);

        std::int32_t val_8 = 6;
        while (true) {
            sub_00534540();

            std::int32_t ebx = 0;
            char* edi = esi + 0x14;
            while (ebx < 0x280) {
                std::uint32_t off = *reinterpret_cast<std::uint32_t*>(edi);
                char* target_surface = esi + off;

                sub_00563440(target_surface, ebx, 0, 32, 32);

                ebx += 0x20;
                edi += 8;
            }

            ebx = 0;
            edi = esi + 0xB4;
            while (ebx < 0x280) {
                std::uint32_t off = *reinterpret_cast<std::uint32_t*>(edi);
                char* target_surface = esi + off;

                sub_00563440(target_surface, ebx, 32, 64, 64);

                ebx += 0x40;
                edi += 8;
            }

            ebx = 0;
            edi = esi + 0x104;
            while (ebx < 0x280) {
                std::uint32_t off = *reinterpret_cast<std::uint32_t*>(edi);
                char* target_surface = esi + off;

                sub_00563440(target_surface, ebx, 96, 128, 128);

                ebx += 0x80;
                edi += 8;
            }

            ebx = 0;
            edi = esi + 0x12c;
            while (ebx < 0x280) {
                std::uint32_t off = *reinterpret_cast<std::uint32_t*>(edi);
                char* target_surface = esi + off;

                sub_00563440(target_surface, ebx, 224, 128, 128);

                ebx += 0x80;
                edi += 8;
            }

            ebx = 0;
            edi = esi + 0x154;
            while (ebx < 0x280) {
                std::uint32_t off = *reinterpret_cast<std::uint32_t*>(edi);
                char* target_surface = esi + off;

                sub_00563440(target_surface, ebx, 352, 128, 128);

                ebx += 0x80;
                edi += 8;
            }

            sub_00534550();
            g_pfn_006bd948();

            val_8--;
            if (val_8 == 0) {
                break;
            }
        }

        heap_pool_block_free_00531f90(p_tex);
    }

    sub_00560030();
}

} // namespace porsche
