#include "app_main_subsystem_large_304.hpp"

namespace porsche {

// =============================================================================
// Function 1: 0059d650 (625 bytes) - CD-ROM Path Resolver & Game Root Discovery
// =============================================================================
void CALL_CDECL cdrom_path_resolve_0059d650() {
    g_val_006af370 = 1;
    char mod_path[260];
    g_pfn_GetModuleFileNameA_005b2064(nullptr, mod_path, sizeof(mod_path));

    int len = 0;
    while (mod_path[len] != '\0') {
        len++;
    }

    char dir_path[260];
    dir_path[0] = '\0';
    int slash_idx = -1;
    for (int i = len - 1; i >= 0; --i) {
        if (mod_path[i] == '\\') {
            slash_idx = i;
            break;
        }
    }

    if (slash_idx >= 0) {
        const char* src = &mod_path[slash_idx + 1];
        char* dst = dir_path;
        while (*src != '\0') {
            *dst++ = *src++;
        }
        *dst = '\0';
        mod_path[slash_idx + 1] = '\0';
    }

    g_val_006af168 = 0;

    char drive_buf[16];
    char probe_buf[260];
    bool found_cd = false;
    for (char c = 'd'; c <= 'z'; ++c) {
        sprintf_005a0fbf(drive_buf, g_str_005d1290, static_cast<int>(c));
        std::uint32_t dtype = g_pfn_GetDriveTypeA_005b2060(drive_buf);
        if (dtype == 5) { // DRIVE_CDROM
            sprintf_005a0fbf(probe_buf, g_str_005cc588, drive_buf, dir_path);
            file_exists_00561b80(probe_buf);
            const char* s = drive_buf;
            char* d = g_val_006af26c;
            while (*s != '\0') {
                *d++ = *s++;
            }
            *d = '\0';
            found_cd = true;
            break;
        }
    }

    if (!found_cd) {
        g_val_006af26c[0] = '\0';
    }

    // Loop 2 in original PE
    for (char c = 'd'; c <= 'z'; ++c) {
        sprintf_005a0fbf(drive_buf, g_str_005d1290, static_cast<int>(c));
        if (g_pfn_GetDriveTypeA_005b2060(drive_buf) == 5) {
            sprintf_005a0fbf(probe_buf, g_str_005cc588, drive_buf, dir_path);
            file_exists_00561b80(probe_buf);
        }
        break; // In original PE, 0059D78D unconditionally breaks loop 2
    }

    // PE 0059D7FE: clears g_val_006af26c and probes probe.dat
    g_val_006af26c[0] = '\0';
    sprintf_005a0fbf(probe_buf, g_str_005cc588, mod_path, g_str_005d6e14);
    file_exists_00561b80(probe_buf);
    // PE 0059D81C: unconditionally returns
}

// =============================================================================
// Function 2: 004a88a0 (471 bytes) - Display Mode Probe & Capabilities Sync
// =============================================================================
void CALL_CDECL display_mode_probe_sync_004a88a0() {
    sub_004ad510();
    sub_004ae3c0(0x5dc);
    if (g_val_00657c94 != 0) {
        return;
    }

    sub_004af900(0, 0);
    sub_004afd30();

    for (int i = 0; i < 32; ++i) {
        DisplaySlot0065653c& slot = g_entries_0065653c[i];
        if (slot.field_00 != -1) {
            if (slot.field_04 != -1) {
                sub_005659f0(static_cast<std::uint32_t>(slot.field_04));
                slot.field_04 = -1;
            }
            if (slot.buffer_10 != nullptr) {
                heap_pool_block_free_00531f90(slot.buffer_10);
                slot.buffer_10 = nullptr;
            }
            slot.field_00 = -1;
        }
    }

    for (int i = 0; i < 73; ++i) {
        DisplaySlot00656180& slot = g_entries_00656180[i];
        if (slot.field_00 != -1) {
            sub_00565d60(static_cast<std::uint32_t>(slot.field_00));
            slot.field_00 = -1;
            slot.field_04 = -1;
        }
    }

    if (g_val_00656868 != 0) {
        sub_00565cd0(0, 0);
        g_val_00656869 = 0;
        g_val_00656868 = 0;
    }

    sub_004a8660();

    if (g_val_005d1734 != 0 && g_val_005d1750 > 0) {
        std::uint32_t t_end = timer_0053c2e0() + 0x280;
        while (timer_0053c2e0() < t_end) {
            sub_004b0a20();
            sub_005366e0(0);

            bool ok = true;
            if (g_val_00657a24 == 1) {
                if (sub_004a8570(1, 0, 0) == -1) {
                    ok = false;
                }
            }

            int count = g_count_00658080;
            for (int i = 0; i < count; ++i) {
                DisplayTarget0065808c& t = g_targets_0065808c[i];
                if (t.type == 2) {
                    std::int32_t h = sub_004b04d0(t.handle, 0);
                    if (h > -1) {
                        if (sub_004a8570(1, static_cast<std::uint32_t>(h), 0) == -1) {
                            ok = false;
                        }
                    }
                    std::int32_t h2 = sub_004b04d0(t.handle, 1);
                    if (h2 > -1) {
                        if (sub_004a8570(1, static_cast<std::uint32_t>(h2), 0) == -1) {
                            ok = false;
                        }
                    }
                }
            }

            if (ok) {
                break;
            }
        }
    }

    sub_004af5c0();

    if (g_val_005e99f4 < 2) {
        sub_004ae470(g_val_00657cb8, &g_val_00657cbc);
        sub_004ae4d0(0, 0);
    }
}

// =============================================================================
// Function 3: 004640b0 (564 bytes) - Audio Listener & Emitter Transform Sync
// =============================================================================
void CALL_CDECL audio_listener_update_004640b0() {
    std::uint32_t mode = (g_val_00657404 == 1) ? 1 : 0;
    AudioContextObject local_ctx;
    local_ctx.ctor_00473100(0);

    std::int32_t count = static_cast<std::int32_t>(mode);
    if (count >= 0) {
        std::uint8_t flag = static_cast<std::uint8_t>(mode << 7) | 0x20;
        for (std::int32_t i = 0; i <= count; ++i) {
            AudioListenerSlot& listener = g_listeners_00627e94[i];
            AudioEmitterObject* emitter = g_emitters_005e8c00[g_val_0065741c];
            listener.emitter_prev = emitter;
            listener.emitter_curr = emitter;

            for (int j = 0; j < 3; ++j) {
                listener.pos1[j] = emitter->position[j];
                listener.pos2[j] = emitter->position[j];
            }
            listener.field_0c = 0;
            listener.field_1c = 0;
            listener.val_20 = 0.0f;
            listener.val_24 = 37.5f;
            listener.val_64 = 37.5f;
            listener.val_28 = 0.0f;
            listener.val_2c = 0.0f;
            listener.val_44 = 37.5f;
            listener.val_48 = 0.5f;

            for (int j = 0; j < 9; ++j) {
                listener.matrix[j] = emitter->orientation[j];
            }
            listener.field_8c = 0;

            for (int j = 0; j < 3; ++j) {
                listener.pos3[j] = emitter->position[j];
                listener.pos4[j] = emitter->position[j];
            }

            listener.field_a8 = 0x000e;
            listener.field_aa = 0;
            listener.field_ac = flag;
            listener.field_ad = 0;
            listener.field_ae = 0;
            listener.field_af &= 0xf0;
            listener.field_b0 = 0;
            listener.field_b2 = 0;
            listener.field_b4 = 0;
            listener.field_b6 = g_val_005cf5d8;
            listener.field_b8 = 0.9f;
            listener.field_bc = 0;
            listener.field_c0 = 0xff;
            listener.field_c4 = 0x40;

            listener.ctx_c8.copy_00473190(&local_ctx);
            sub_00465cf0(static_cast<std::uint32_t>(i + 1));
        }
    }

    AudioEmitterObject* emitter = g_emitters_005e8c00[g_val_0065741c];
    for (int j = 0; j < 3; ++j) {
        g_val_005cf620[j] = emitter->listener_pos[j];
        g_val_00627ecc[j] = emitter->listener_vel[j];
    }

    std::int32_t res = sub_005ae3c0(g_val_00657444, g_val_005cf760);
    g_val_005cf584 = (res != 0) ? 1 : 0;

    sub_00463c30();
    pipe_00516950();
}

// =============================================================================
// Function 4: 00467470 (642 bytes) - User Input Subsystem & Controller Init
// =============================================================================
void CALL_CDECL input_subsystem_init_00467470() {
    void* mem = operator_new_0059ef90(0x118);
    InputContext* ctx = nullptr;
    if (mem != nullptr) {
        ctx = static_cast<InputContext*>(mem)->ctor_00467700(g_str_005d6f1c, g_str_005d6f20);
    }
    g_ptr_0065b39c = ctx;

    char dev_name[64];
    const char* src_kbd = g_str_00657a38;
    char* dst = dev_name;
    while (*src_kbd != '\0') {
        *dst++ = *src_kbd++;
    }
    *dst = '\0';

    if (ctx != nullptr && ctx->vtable != nullptr) {
        ctx->vtable->virtual_action_00(ctx);
    }

    bool is_keyboard = true;
    const char* s1 = g_str_00657a38;
    const char* s2 = g_str_005cf7bc;
    while (*s1 != '\0' || *s2 != '\0') {
        if (*s1 != *s2) {
            is_keyboard = false;
            break;
        }
        s1++;
        s2++;
    }

    std::uint32_t val_ebx = 0;
    char buf_80[80];
    char buf_d0[80];

    if (is_keyboard) {
        ctx->sub_004b7240(0, dev_name);
        if (dev_name[0] == '\0') {
            g_pfn_MessageBoxA_005b2270(nullptr, g_str_005cf78c, g_str_005cf7b4, 0);
            sub_005a246e(1);
        }

        bool match_788 = true;
        s1 = dev_name;
        s2 = g_str_005cf788;
        while (*s1 != '\0' || *s2 != '\0') {
            if (*s1 != *s2) {
                match_788 = false;
                break;
            }
            s1++;
            s2++;
        }

        if (match_788) {
            val_ebx = ctx->sub_004b7340(1);
            const char* app = g_str_005ccc2c;
            char* p = dev_name;
            while (*p != '\0') {
                p++;
            }
            while (*app != '\0') {
                *p++ = *app++;
            }
            *p = '\0';
        } else {
            val_ebx = 0;
        }

        const char* app2 = g_str_005cf784;
        char* p2 = dev_name;
        while (*p2 != '\0') {
            p2++;
        }
        while (*app2 != '\0') {
            *p2++ = *app2++;
        }
        *p2 = '\0';

        ctx->sub_004b7240(2, buf_80);
    } else {
        val_ebx = g_val_00657a58;
        sprintf_005a0fbf(buf_80, g_str_005cf77c, g_val_00657a48, g_val_00657a4c);
    }

    const char* s_b304 = g_str_0065b304;
    char* d = buf_d0;
    while (*s_b304 != '\0') {
        *d++ = *s_b304++;
    }
    const char* s_dev = dev_name;
    while (*s_dev != '\0') {
        *d++ = *s_dev++;
    }
    *d = '\0';

    ctx->sub_004b7220();

    ControllerDevice* dev = g_ptr_00628130;
    if (dev == nullptr) {
        void* dev_mem = operator_new_0059ef90(0x80);
        if (dev_mem != nullptr) {
            dev = static_cast<ControllerDevice*>(dev_mem)->ctor_004677e0(buf_d0, val_ebx, 0, buf_80);
        } else {
            dev = nullptr;
        }
        g_ptr_00628130 = dev;
    }

    if (dev != nullptr) {
        sub_004b70d0(dev->field_7c, dev->field_74);
    }
    sub_00465df0();
    sub_00449b40();
}

} // namespace porsche
