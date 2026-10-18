#include "app_main_frame_event_pump_307.hpp"
#include <cstring>

namespace porsche {

void CALL_CDECL frame_event_pump_004b4da0(std::int32_t* event_stream) {
    // 1. Zero out the screen context buffer at 0x006573e8 (size 0x3e24)
    std::memset(g_screen_buffer_006573e8, 0, 0x3e24);

    // 2. Set default values in screen context
    *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x9c8]) = 0xff; // 0x00657db0
    *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x9c0]) = 0x77; // 0x00657da8
    *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x9c4]) = 0xbb; // 0x00657dac

    // 3. Reset input subsystem
    hook_00412e00();

    // 4. Preprocess event stream
    hook_004b6560(event_stream);
    hook_004b6600(event_stream);

    // 5. Initial pass over event stream: apply all events
    std::int32_t* p = event_stream;
    while (*p != 0) {
        hook_004b4b80(reinterpret_cast<const std::uint32_t*>(p));
        std::int32_t step = hook_004b4cd0(reinterpret_cast<const std::uint32_t*>(p));
        p += step;
    }

    // 6. Check if screen mode is 3
    if (*reinterpret_cast<std::int32_t*>(&g_screen_buffer_006573e8[0]) == 3) {
        std::int32_t expected_matches = 8;
        std::int32_t matched_count = 0;
        hook_0048d3d0();

        while (g_ui_screen_node_00628c70 != nullptr &&
               g_ui_screen_node_00628c70->active_element != nullptr &&
               *reinterpret_cast<const char*>(reinterpret_cast<const char*>(g_ui_screen_node_00628c70) + 0xbf) == 0 &&
               *reinterpret_cast<const char*>(reinterpret_cast<const char*>(g_ui_screen_node_00628c70) + 0xbe) != 0 &&
               *reinterpret_cast<const std::int32_t*>(reinterpret_cast<const char*>(g_ui_screen_node_00628c70) + 0xdc) >= 0 &&
               expected_matches != matched_count)
        {
            std::uint8_t bitmask = *reinterpret_cast<const std::uint8_t*>(reinterpret_cast<const char*>(g_ui_screen_node_00628c70) + 0xe5);
            std::int32_t target_dc = *reinterpret_cast<const std::int32_t*>(reinterpret_cast<const char*>(g_ui_screen_node_00628c70) + 0xdc);
            matched_count = 0;
            std::int32_t matched_index = 0;

            // Child list traversal at offset 0x260
            UiElementNode** p_list_head = reinterpret_cast<UiElementNode**>(reinterpret_cast<char*>(g_ui_screen_node_00628c70) + 0x260);
            if (p_list_head != nullptr && *p_list_head != nullptr) {
                UiElementNode* head = *p_list_head;
                UiElementNode* curr = head->next;
                while (curr != head && curr != nullptr) {
                    UiElementData* item = curr->element_data;
                    if (item != nullptr) {
                        std::int32_t item_id = item->element_id;
                        if ((bitmask & (1 << (item_id & 0x1f))) != 0) {
                            item->mapped_index = matched_count;
                            if (item_id == target_dc) {
                                matched_index = matched_count;
                            }
                            matched_count++;
                        } else {
                            item->mapped_index = -1;
                        }
                    }
                    curr = curr->next;
                }
            }

            // Stream re-dispatch
            p = event_stream;
            while (*p != 0) {
                std::int32_t ev_type = *p;
                if ((ev_type >= 0x21e) ||
                    (ev_type >= 0x147 && ev_type < 0x14e) ||
                    (ev_type >= 0x13a && ev_type < 0x142))
                {
                    if (ev_type != 0x247 && (p[1] == target_dc || (hook_0048caa0() != 0 && p[1] >= 8))) {
                        std::int32_t words = hook_004b4cd0(reinterpret_cast<const std::uint32_t*>(p));
                        std::int32_t local_buf[64];
                        std::memcpy(local_buf, p, words * sizeof(std::int32_t));
                        if (local_buf[1] == target_dc) {
                            local_buf[1] = matched_index;
                        } else {
                            local_buf[1] = local_buf[1] + matched_count - 8;
                        }
                        hook_0048d490(local_buf);
                    }
                }
                else {
                    if (ev_type >= 0x146 || (ev_type >= 0x126 && ev_type < 0x142) || (ev_type >= 0x2f && ev_type < 0x10e)) {
                        hook_004b4b80(reinterpret_cast<const std::uint32_t*>(p));
                    }
                    else {
                        if (hook_0048caa0() != 0) {
                            hook_0048d490(p);
                        }
                    }
                }
                p += hook_004b4cd0(reinterpret_cast<const std::uint32_t*>(p));
            }

            // Fisher-Yates shuffle
            if (hook_0048caa0() != 0) {
                char arr[8] = {0, 1, 2, 3, 4, 5, 6, 7};
                std::int32_t remaining = matched_count;
                std::int32_t shuf_event[3];
                shuf_event[0] = 0x247;
                for (std::int32_t idx = 0; idx < matched_count; ++idx) {
                    std::int32_t r = hook_005a17c9() % remaining;
                    shuf_event[1] = idx;
                    shuf_event[2] = static_cast<std::int32_t>(arr[r]);
                    hook_0048d490(shuf_event);
                    remaining--;
                    for (std::int32_t k = r; k < remaining; ++k) {
                        arr[k] = arr[k + 1];
                    }
                }
            }

            hook_0048d440();
            hook_0048d6a0();

            *reinterpret_cast<std::int32_t*>(&g_screen_buffer_006573e8[0x34]) = matched_index; // 0x65741c
            *reinterpret_cast<std::int32_t*>(&g_screen_buffer_006573e8[0xc98]) += matched_count - 8; // 0x658080
            *reinterpret_cast<std::int32_t*>(&g_screen_buffer_006573e8[0xc9c]) = matched_count; // 0x658084
            std::int32_t total = matched_count + *reinterpret_cast<std::int32_t*>(&g_screen_buffer_006573e8[0xca0]); // 0x658088
            if (matched_count < total) {
                char* slot = reinterpret_cast<char*>(&g_screen_buffer_006573e8[0xe18]) + matched_count * 0x580; // 0x658200
                for (std::int32_t i = matched_count; i < total; ++i) {
                    *reinterpret_cast<std::int32_t*>(slot) = i;
                    slot += 0x580;
                }
            }

            // Next iteration bitmask count
            expected_matches = 0;
            std::uint8_t next_mask = 0;
            if (g_ui_screen_node_00628c70 != nullptr &&
                g_ui_screen_node_00628c70->active_element != nullptr &&
                *reinterpret_cast<const char*>(reinterpret_cast<const char*>(g_ui_screen_node_00628c70) + 0xbf) == 0)
            {
                next_mask = *reinterpret_cast<const std::uint8_t*>(reinterpret_cast<const char*>(g_ui_screen_node_00628c70) + 0xe5);
            }
            for (std::int32_t b = 0; b < 8; ++b) {
                if ((next_mask & (1 << b)) != 0) {
                    expected_matches++;
                }
            }
        }
    }

    // Check string at 0x00657a84
    char* name_buf = reinterpret_cast<char*>(&g_screen_buffer_006573e8[0x69c]); // 0x00657a84
    if (*name_buf == '\0') {
        const char* unk = g_str_unknown_005d638c;
        while ((*name_buf++ = *unk++) != '\0') {}
    }

    // Delay 100ms
    hook_0053c380(100);

    // State machine updates
    if (g_input_flag_005d1734 == 0) {
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8b0]) = 3; // 0x00657c98
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8ac]) = 1; // 0x00657c94
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8b8]) = 0; // 0x00657ca0
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8bc]) = 0; // 0x00657ca4
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c4]) = 0; // 0x00657cac
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c0]) = 0; // 0x00657ca8
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c8]) = 0; // 0x00657cb0
    } else if (*reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8b0]) == 3) {
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8ac]) = 1; // 0x00657c94
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8b8]) = 0;
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8bc]) = 0;
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c4]) = 0;
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c0]) = 0;
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c8]) = 0;
    } else if (*reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8ac]) == 1) {
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8b8]) = 0;
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8bc]) = 0;
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c4]) = 0;
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c0]) = 0;
        *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c8]) = 0;
    }

    g_input_out_005d1740 = *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8b8]);
    g_input_out_005d1744 = *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8bc]);
    g_input_out_005d174c = *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c4]);
    g_input_out_005d1748 = *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c0]);
    g_input_out_005d1750 = *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8c8]);

    hook_00411760();
}

} // namespace porsche
