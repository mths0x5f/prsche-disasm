#include "app_main_subsystem_medium_302.hpp"

// =============================================================================
// Function 1: 0059d8e0 (206 bytes)
// Asset path locator & file opener helper
// =============================================================================
int CALL_CDECL asset_path_locate_or_open_0059d8e0(const char* filename, int flags) {
    char buf[260];
    if (g_flag_006af370 == 0) {
        char* d = buf;
        const char* s = filename;
        while ((*d++ = *s++) != '\0') {}
        return file_open_00561ca0(buf, flags);
    }

    sprintf_005a0fbf(buf, g_fmt_005cc588, g_path_006af168, filename);
    if (file_exists_00561b80(buf) != 0) {
        return file_open_00561ca0(buf, flags);
    }

    if (g_path_006af26c[0] != '\0') {
        sprintf_005a0fbf(buf, g_fmt_005cc588, g_path_006af26c, filename);
        if (file_exists_00561b80(buf) != 0) {
            return file_open_00561ca0(buf, flags);
        }
    }

    if (g_fn_006afbe4 != nullptr) {
        g_fn_006afbe4(filename, -2);
    }
    return 0;
}

// =============================================================================
// Function 2: 004a6e30 (217 bytes)
// Display timing sync & device sync table resetter
// =============================================================================
void CALL_CDECL display_timing_sync_004a6e30() {
    g_val_00655e48 = 0;
    g_val_00655d54 = 0;
    g_val_00655ffc = 0;
    g_val_00655d5c = -1;
    g_val_00655d48 = -1;
    g_val_00655d4c = -1;
    g_val_00655d50 = -1;

    for (int i = 0; i < 2; ++i) {
        TimingRecord50* rec = &g_table_00655f38[i];
        rec->field_00 = -1;
        rec->field_04 = 0;
        rec->field_08 = 0;
        rec->field_18 = 0;
        rec->field_1c = -1;
        rec->field_20 = -1;
        rec->field_28 = 0;
        rec->field_2c = 0x1324;
        rec->field_30 = 0;
        rec->field_38 = 0;
        rec->field_48 = 0;
        rec->field_4c = 0;

        if (static_cast<std::int32_t>(g_val_00657404) > 1) {
            if (i == 0 && static_cast<std::int32_t>(g_val_0065741c) < g_count_005e8bfc) {
                rec->field_18 = g_table_005e8c00[g_val_0065741c];
            }
        } else {
            if (i < g_count_005e8bfc) {
                rec->field_18 = g_table_005e8c00[i];
            }
        }
    }

    for (int j = 0; j < 4; ++j) {
        TimingRecord38* rec = &g_table_00655d60[j];
        rec->field_00 = 0;
        rec->field_04 = -1;
        rec->field_08 = -1;
        rec->field_10 = 0;
        rec->field_14 = 0x1324;
        rec->field_18 = 0;
        rec->field_20 = 0;
        rec->field_30 = 0;
        rec->field_34 = 0;
    }

    g_val_00655e44 = 0;
}

// =============================================================================
// Function 3: 0048dad0 (218 bytes)
// Input message dequeue & accelerator translation dispatcher
// =============================================================================
void CALL_CDECL input_msg_dequeue_0048dad0() {
    InputSubsystem* sub = g_input_subsystem_00628c70;
    if (sub == nullptr || sub->field_08 == 0 || sub->flag_bf != 0) {
        return;
    }

    if (sub->flag_bd == 0) {
        InputMsgLock* lock = sub->lock_10;
        lock_acquire_005322b0(lock->lock_handle);
        sub = g_input_subsystem_00628c70;
        sub->event_dispatcher_0c->post_event_0048c870(0xB7, 0xFFFFFFFF, 0xFFFFFFFF, 0, 0);
        g_input_subsystem_00628c70->flag_bd = 1;
        lock_release_005322c0(lock->lock_handle);
        sub = g_input_subsystem_00628c70;
    }

    if (sub != nullptr && sub->field_08 != 0 && sub->flag_bf == 0) {
        InputMsgLock* lock = sub->lock_10;
        lock_acquire_005322b0(lock->lock_handle);
        sub = g_input_subsystem_00628c70;
        sub->event_dispatcher_0c->post_event_0048c870(0xB7, 0xFFFFFFFE, 0xFFFFFFFF, 0, 0);
        g_input_subsystem_00628c70->flag_bd = 1;
        lock_release_005322c0(lock->lock_handle);
        sub = g_input_subsystem_00628c70;
    }

    if (sub != nullptr) {
        sub->flag_bc = 1;
    }
}

// =============================================================================
// Function 4: 004a5c30 (231 bytes)
// CD-ROM drive detector & launcher spawner
// =============================================================================
void CALL_CDECL cdrom_launcher_spawn_004a5c30() {
    char mod_path[260];
    char root_path[16];
    char autorun_path[260];
    StartupInfoA_004a5c30 si;
    ProcessInformation_004a5c30 pi;

    reg_delete_or_set_005655f0(g_str_porsche_005d1298);

    if (win32_get_module_file_name_005b2064(nullptr, mod_path, 255) != 0) {
        int len = 0;
        while (mod_path[len] != '\0') {
            len++;
        }
        for (int i = len - 1; i >= 0; --i) {
            if (mod_path[i] == '\\') {
                mod_path[i] = '\0';
                break;
            }
        }
    }

    int drive_letter = static_cast<int>(static_cast<signed char>(mod_path[0]));
    if (isalpha_005a2c24(drive_letter) != 0) {
        sprintf_005a0fbf(root_path, g_fmt_drive_005d1290, drive_letter);
        if (win32_get_drive_type_005b2060(root_path) == 5) { // DRIVE_CDROM
            sprintf_005a0fbf(autorun_path, g_fmt_autorun_005d1280, root_path);

            for (std::size_t i = 0; i < sizeof(si); ++i) {
                reinterpret_cast<char*>(&si)[i] = 0;
            }
            si.cb = sizeof(si);

            win32_create_process_005b204c(
                nullptr,
                autorun_path,
                nullptr,
                nullptr,
                0,
                0,
                nullptr,
                nullptr,
                &si,
                &pi
            );
            exit_005a246e(0);
        }
    }
}
