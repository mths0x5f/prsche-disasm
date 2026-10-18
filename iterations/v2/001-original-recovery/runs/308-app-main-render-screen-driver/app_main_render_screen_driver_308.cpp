#include "app_main_render_screen_driver_308.hpp"
#include <cstdlib>

namespace porsche {

void CALL_CDECL render_screen_driver_004a4a70(std::int32_t step) {
    if (step == 0) {
        g_render_enabled_00655a28 = 1;
    } else {
        if (step == 10) {
            g_render_enabled_00655a28 = 0;
            return;
        }
        if (g_render_enabled_00655a28 == 0) {
            return;
        }
    }

    if (g_render_canvas_00655a24 == nullptr) {
        g_render_canvas_00655a24 = hook_00535950(640, 480, g_display_format_005dead0, 16);
    }

    if (g_ui_screen_node_00628c70 != nullptr &&
        g_ui_screen_node_00628c70->active_element != nullptr &&
        g_ui_screen_node_00628c70->field_bf == 0 &&
        g_ui_screen_node_00628c70->field_be != 0 &&
        g_ui_screen_node_00628c70->field_dc >= 0 &&
        step > 0 &&
        g_render_enabled_00655a28 != 0)
    {
        std::int32_t local_stream[24];
        std::int32_t* p_stream = local_stream;
        hook_004edc00(0x256, reinterpret_cast<void**>(&p_stream), g_screen_matched_index_0065741c, step);
        *p_stream = 0;
        if (p_stream != local_stream) {
            hook_0048d550(local_stream);
        }
    }

    if (g_skip_render_00657440 != 1) {
        std::int32_t target_time = hook_004ad670();
        std::int32_t current_time = hook_004ad6c0();
        while (current_time < target_time) {
            hook_005366e0(0);
            target_time = hook_004ad670();
            current_time = hook_004ad6c0();
        }

        hook_00534480(g_render_canvas_00655a24);

        if (step == 0 || (step == 5 && g_screen_mode_006573e8 != 9)) {
            char fsh_path[100];
            std::uint8_t* car_fsh = nullptr;
            if (step == 5) {
                char car_name_buf[96];
                hook_005a0fbf(car_name_buf, "%s%s.fsh", g_fsh_path_0065b350, &g_screen_suffix_00657444);
                if (hook_0059dc30(car_name_buf) != 0) {
                    car_fsh = hook_0059d8e0(car_name_buf, 0);
                }
            }

            std::int32_t era_idx = 0;
            if (g_screen_mode_006573e8 == 4) {
                std::int32_t theme = hook_005032d0();
                if (theme == 0x209) era_idx = 1;
                else if (theme == 0x20a) era_idx = 2;
                else if (theme == 0x20b) era_idx = 3;
            }

            const char* fmt = (step == 0) ? "%sera%d.fsh" : "%seradtr.fsh";
            hook_005a0fbf(fsh_path, fmt, g_fsh_dir_0065b334, era_idx);
            std::uint8_t* bg_fsh = hook_0059d8e0(fsh_path, 0);

            if (bg_fsh != nullptr) {
                // Strip 1: y=0, w=32, h=32
                const std::int32_t* pi = reinterpret_cast<const std::int32_t*>(bg_fsh + 0x14);
                for (std::int32_t x = 0; x < 640; x += 32, pi += 2) {
                    hook_00563440(bg_fsh + *pi, x, 0, 32, 32);
                }

                // Strip 2: y=32, w=64, h=64
                pi = reinterpret_cast<const std::int32_t*>(bg_fsh + 0xb4);
                for (std::int32_t x = 0; x < 640; x += 64, pi += 2) {
                    hook_00563440(bg_fsh + *pi, x, 32, 64, 64);
                }

                // Strip 3: y=96, w=128, h=128
                pi = reinterpret_cast<const std::int32_t*>(bg_fsh + 0x104);
                for (std::int32_t x = 0; x < 640; x += 128, pi += 2) {
                    hook_00563440(bg_fsh + *pi, x, 96, 128, 128);
                }

                // Strip 4: y=224, w=128, h=128
                pi = reinterpret_cast<const std::int32_t*>(bg_fsh + 0x12c);
                for (std::int32_t x = 0; x < 640; x += 128, pi += 2) {
                    hook_00563440(bg_fsh + *pi, x, 224, 128, 128);
                }

                // Strip 5: y=352, w=128, h=128
                pi = reinterpret_cast<const std::int32_t*>(bg_fsh + 0x154);
                for (std::int32_t x = 0; x < 640; x += 128, pi += 2) {
                    hook_00563440(bg_fsh + *pi, x, 352, 128, 128);
                }
            }

            // Car art overlays
            if (step == 5 && car_fsh != nullptr) {
                std::uint8_t* chunk1 = car_fsh + *reinterpret_cast<const std::int32_t*>(car_fsh + 0x14);
                std::int32_t x1 = std::abs(static_cast<int>(*reinterpret_cast<const std::int16_t*>(chunk1 + 8)));
                std::int32_t y1 = std::abs(static_cast<int>(*reinterpret_cast<const std::int16_t*>(chunk1 + 10)));
                std::int32_t w1 = *reinterpret_cast<const std::int16_t*>(chunk1 + 4);
                std::int32_t h1 = *reinterpret_cast<const std::int16_t*>(chunk1 + 6);
                if (g_blend_flag_0065742c == 1) hook_00563320(chunk1);
                hook_00563160(chunk1, x1, y1, w1, h1);
                if (g_blend_flag_0065742c == 1) hook_00563320(chunk1);

                std::uint8_t* chunk2 = car_fsh + *reinterpret_cast<const std::int32_t*>(car_fsh + 0x1c);
                std::int32_t x2 = std::abs(static_cast<int>(*reinterpret_cast<const std::int16_t*>(chunk2 + 8)));
                std::int32_t y2 = std::abs(static_cast<int>(*reinterpret_cast<const std::int16_t*>(chunk2 + 10)));
                std::int32_t w2 = *reinterpret_cast<const std::int16_t*>(chunk2 + 4);
                std::int32_t h2 = *reinterpret_cast<const std::int16_t*>(chunk2 + 6);
                hook_00563160(chunk2, x2, y2, w2, h2);

                std::int32_t off3 = (g_alt_flag_00657430 == 1) ? *reinterpret_cast<const std::int32_t*>(car_fsh + 0x2c)
                                                               : *reinterpret_cast<const std::int32_t*>(car_fsh + 0x24);
                if (off3 != 0) {
                    std::uint8_t* chunk3 = car_fsh + off3;
                    std::int32_t x3 = std::abs(static_cast<int>(*reinterpret_cast<const std::int16_t*>(chunk3 + 8)));
                    std::int32_t y3 = std::abs(static_cast<int>(*reinterpret_cast<const std::int16_t*>(chunk3 + 10)));
                    std::int32_t w3 = *reinterpret_cast<const std::int16_t*>(chunk3 + 4);
                    std::int32_t h3 = *reinterpret_cast<const std::int16_t*>(chunk3 + 6);
                    if (g_blend_flag_0065742c == 1) hook_00563320(chunk3);
                    hook_00563160(chunk3, x3, y3, w3, h3);
                }
            }

            if (bg_fsh != nullptr) hook_00531f90(bg_fsh);
            if (car_fsh != nullptr) hook_00531f90(car_fsh);
        }

        // MLoading.fsh
        if (g_ui_screen_node_00628c70 != nullptr &&
            g_ui_screen_node_00628c70->active_element != nullptr &&
            g_ui_screen_node_00628c70->field_bf == 0 &&
            g_ui_screen_node_00628c70->field_be != 0 &&
            g_ui_screen_node_00628c70->field_dc >= 0 &&
            (step == 0 || step == 5))
        {
            std::int32_t sub_idx = (step > 4) ? 2 : 0;
            char load_path[100];
            hook_005a0fbf(load_path, "%sMLoading.fsh", g_fsh_dir_0065b334);
            std::uint8_t* load_fsh = hook_0059d8e0(load_path, 0);
            if (load_fsh != nullptr) {
                hook_00563440(load_fsh + *reinterpret_cast<const std::int32_t*>(load_fsh + 0x14 + sub_idx * 8), 0, 0x142, 0x100, 0x9e);
                hook_00563440(load_fsh + *reinterpret_cast<const std::int32_t*>(load_fsh + 0x1c + sub_idx * 8), 0x100, 0x142, 0x100, 0x9e);
                hook_00563440(load_fsh + *reinterpret_cast<const std::int32_t*>(load_fsh + 0x24 + sub_idx * 8), 0x200, 0x142, 0x80, 0x9e);
                hook_00531f90(load_fsh);
            }
        }

        // loadtext.fsh
        if ((step == 0 || step == 5) && g_loadtext_idx_00657c84 != 0) {
            char text_path[100];
            hook_005a0fbf(text_path, "%sloadtext.fsh", g_fsh_dir_0065b334);
            std::uint8_t* text_fsh = nullptr;
            if (hook_0059dc30(text_path) != 0) {
                text_fsh = hook_0059d8e0(text_path, 0);
            }
            if (text_fsh != nullptr) {
                std::uint8_t* chunk = text_fsh + *reinterpret_cast<const std::int32_t*>(text_fsh + 0xc + g_loadtext_idx_00657c84 * 8);
                std::int32_t x = -static_cast<std::int32_t>(*reinterpret_cast<const std::int16_t*>(chunk + 8));
                std::int32_t y = -static_cast<std::int32_t>(*reinterpret_cast<const std::int16_t*>(chunk + 10));
                std::int32_t w = *reinterpret_cast<const std::int16_t*>(chunk + 4);
                std::int32_t h = *reinterpret_cast<const std::int16_t*>(chunk + 6);
                hook_00562810(chunk, x, y, w, h);
                hook_00531f90(text_fsh);
            }
        }

        // Status indicator
        if (step >= 0) {
            std::int32_t bar_w = static_cast<std::int32_t>(static_cast<double>(step) * 12.399999618530273);
            hook_00562680(302, 467, bar_w, 6, 0xffffbb00);
        }

        // Slot table walk
        if (g_ui_screen_node_00628c70 != nullptr &&
            g_ui_screen_node_00628c70->active_element != nullptr &&
            g_ui_screen_node_00628c70->field_bf == 0 &&
            g_ui_screen_node_00628c70->field_be != 0 &&
            g_ui_screen_node_00628c70->field_dc >= 0 &&
            g_render_enabled_00655a28 != 0)
        {
            if (g_ui_screen_node_00628c70->container != nullptr && *g_ui_screen_node_00628c70->container != nullptr) {
                hook_005322b0(*g_ui_screen_node_00628c70->container);
            }

            for (std::int32_t i = 0; i < g_slot_count_00658084; ++i) {
                const std::int32_t* slot_entry = reinterpret_cast<const std::int32_t*>(&g_slot_table_00658200[i * 0x580]);
                std::int32_t slot_idx = slot_entry[0];
                UiElement* elem = reinterpret_cast<UiElement*>(hook_0048d720(i));
                if (elem == nullptr || elem->is_visible_00490390() == 0) {
                    hook_00562680(slot_idx * 74 + 32, 364, 54, 64, 0);
                } else {
                    std::uint8_t* graphic = elem->get_graphic_004903f0(0);
                    std::uint8_t* chunk = nullptr;
                    if (graphic != nullptr) {
                        std::int32_t g_val = *reinterpret_cast<const std::int32_t*>(graphic + 8);
                        if (*reinterpret_cast<const std::int32_t*>(graphic + 0xc) >= g_val) {
                            chunk = reinterpret_cast<std::uint8_t*>(*reinterpret_cast<const std::int32_t*>(graphic + 4));
                        }
                    }
                    if (chunk != nullptr) {
                        std::uint8_t* c_ptr = chunk + *reinterpret_cast<const std::int32_t*>(chunk + 0x14);
                        hook_00562810(c_ptr, slot_idx * 74 + 32, 364,
                                      *reinterpret_cast<const std::int16_t*>(c_ptr + 4),
                                      *reinterpret_cast<const std::int16_t*>(c_ptr + 6));
                        std::int32_t base_x = slot_idx * 74 + 32;
                        std::int32_t fill_w = (slot_entry[0x102] * 54) / 10;
                        std::int32_t rem_w = 54 - fill_w;
                        hook_00562680(base_x + fill_w, 436, rem_w, 6, 0xff312000);
                        hook_00562680(base_x, 436, fill_w, 6, 0xffffbb00);
                    }
                }
            }

            if (g_ui_screen_node_00628c70 != nullptr &&
                g_ui_screen_node_00628c70->container != nullptr &&
                *g_ui_screen_node_00628c70->container != nullptr)
            {
                hook_005322c0(*g_ui_screen_node_00628c70->container);
            }
        }

        // Render pass finalize & present
        hook_004b0d70();
        if (g_driver_fn_006bd9b0) g_driver_fn_006bd9b0(2);
        if (g_driver_fn_006bd91c) g_driver_fn_006bd91c();
        if (g_driver_fn_006bd978) g_driver_fn_006bd978(0);
        hook_00534540();
        hook_0053d570(*reinterpret_cast<void**>(reinterpret_cast<char*>(g_render_canvas_00655a24) + 0x28),
                      (g_screen_width_005deac8 - 640) / 2,
                      (g_screen_height_005deacc - 480) / 2);
        hook_00534550();
        if (g_driver_fn_006bd948) g_driver_fn_006bd948();

        if (step == 10) {
            if (g_render_canvas_00655a24 != nullptr) {
                hook_00533f80(g_render_canvas_00655a24);
            }
            g_render_canvas_00655a24 = nullptr;
        }
    }
}

} // namespace porsche
