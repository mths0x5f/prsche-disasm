#include "app_main_ui_screen_handlers_411.hpp"
#include <cstring>

namespace porsche {

// =============================================================================
// Global Subsystem Variables Definitions
// =============================================================================
extern "C" {
    UiScreenNode* g_ui_screen_node_00628c70 = nullptr;
    std::uint32_t g_dword_00628c74 = 0;
    std::uint32_t g_dword_00657aa4 = 0;
    std::uint8_t  g_byte_005d0728 = 0;
    std::uint32_t g_dword_005b4980 = 0;
    std::uint32_t g_dword_005b4990 = 0;
    std::uint32_t g_dword_00508e70 = 0;
    std::uint32_t (CALL_STDCALL *g_pfn_005b2080)() = nullptr;
}


extern "C" {
    void CALL_CDECL sub_0055ec50(std::uint32_t a1, const char* str);
    void CALL_CDECL sub_0048da60(std::int32_t a1, std::int32_t a2);
    void CALL_CDECL sub_004a4a70(std::int32_t a1);
    std::uint32_t CALL_CDECL sub_0055ff60();
    void CALL_CDECL sub_0055f740(std::uint32_t a1);
    void CALL_CDECL sub_005366e0(std::uint32_t a1);
    void CALL_CDECL sub_005322b0(void* a1);
    void CALL_CDECL sub_005322c0(void* a1);
    std::uint32_t CALL_CDECL sub_0055eb70(std::uint32_t a1);
    void* CALL_CDECL sub_0053c290(void* dst, int val, std::size_t sz);
    char* CALL_CDECL sub_005a28a0(char* dst, const char* src, std::size_t sz);
    void* CALL_CDECL sub_005323e0(void* dst, const void* src, std::size_t sz);
    std::uint32_t CALL_CDECL sub_0055aaa0(std::uint32_t a1, std::uint32_t a2, std::uint32_t a3, void* a4, std::uint32_t a5, std::uint32_t a6, std::uint32_t a7);
    void CALL_CDECL sub_0055bfd0(std::uint32_t a1);
    void CALL_CDECL sub_0048c4d0();
    void* CALL_CDECL sub_0059ef90(std::size_t sz);
    std::uint32_t CALL_CDECL sub_0048a9a0();
    void CALL_CDECL sub_00560140(void* a1);
}

extern "C" {
    void hook_0048c870(void* self, std::uint32_t a1, std::uint32_t a2, std::uint32_t a3, std::uint32_t a4, std::uint32_t a5);
    void hook_0048d350(void* self, std::uint32_t a1, std::int32_t a2, std::int32_t a3, std::uint32_t a4);
    void hook_0048dbe0(void* self);
    void hook_0048e9c0(void* self);
    void hook_0048dbb0(void* self);
    void hook_0048aa10(void* self, std::uint32_t a1, void* a2, void* a3, const char* a4, void* a5, const char* a6, void* a7, std::uint32_t a8);
    void hook_00491cd0(void* self, std::uint32_t a1, void* a2, void* a3, std::uint32_t a4, std::uint32_t a5, std::int32_t a6);
    void* hook_004931c0(void* self, void* a1);
    void hook_0048ac70(void* self, void* a1);
    void hook_0048ac50(void* self);
    void hook_0048ac90(void* self, void* a1, std::uint32_t a2);
    void hook_0048c840(void* self, std::uint32_t a1, std::uint32_t a2);
    void* hook_00529050(void* self, void* a1);
    void hook_0050e140(void* self, void* a1);
    void hook_004937f0(void* self, void* a1);
}

// Dispatch helpers
static inline void call_0048c870(void* self, std::uint32_t a1, std::uint32_t a2, std::uint32_t a3, std::uint32_t a4, std::uint32_t a5) {
    hook_0048c870(self, a1, a2, a3, a4, a5);
}
static inline void call_0048d350(void* self, std::uint32_t a1, std::int32_t a2, std::int32_t a3, std::uint32_t a4) {
    hook_0048d350(self, a1, a2, a3, a4);
}
static inline void call_0048dbe0(void* self) {
    hook_0048dbe0(self);
}
static inline void call_0048e9c0(void* self) {
    hook_0048e9c0(self);
}
static inline void call_0048dbb0(void* self) {
    hook_0048dbb0(self);
}
static inline void call_0048aa10(void* self, std::uint32_t a1, void* a2, void* a3, const char* a4, void* a5, const char* a6, void* a7, std::uint32_t a8) {
    hook_0048aa10(self, a1, a2, a3, a4, a5, a6, a7, a8);
}
static inline void call_00491cd0(void* self, std::uint32_t a1, void* a2, void* a3, std::uint32_t a4, std::uint32_t a5, std::int32_t a6) {
    hook_00491cd0(self, a1, a2, a3, a4, a5, a6);
}
static inline void* call_004931c0(void* self, void* a1) {
    return hook_004931c0(self, a1);
}
static inline void call_0048ac70(void* self, void* a1) {
    hook_0048ac70(self, a1);
}
static inline void call_0048ac50(void* self) {
    hook_0048ac50(self);
}
static inline void call_0048ac90(void* self, void* a1, std::uint32_t a2) {
    hook_0048ac90(self, a1, a2);
}
static inline void call_0048c840(void* self, std::uint32_t a1, std::uint32_t a2) {
    hook_0048c840(self, a1, a2);
}
static inline void* call_00529050(void* self, void* a1) {
    return hook_00529050(self, a1);
}
static inline void call_0050e140(void* self, void* a1) {
    hook_0050e140(self, a1);
}
static inline void call_004937f0(void* self, void* a1) {
    hook_004937f0(self, a1);
}

// String helpers
static inline void fast_strcpy(char* dst, const char* src) {
    while ((*dst++ = *src++) != 0);
}
static inline void fast_strcat(char* dst, const char* src) {
    while (*dst) dst++;
    while ((*dst++ = *src++) != 0);
}

// =============================================================================
// Static String Constants
// =============================================================================
static const char* const s_str_high1 = "Wait to go high1\n";
static const char* const s_str_high2 = "Wait to go high2\n";
static const char* const s_str_low1  = "Wait to go low1\n";
static const char* const s_str_low2  = "Wait to go low2\n";
static const char* const s_str_abort = "Abort\n";
static const char* const s_str_nfsnet = "NfsNet";
static const char* const s_str_game   = "Game";
static const char* const s_str_tilde  = "~";
static const char* const s_str_00     = "0.0";
static const char* const s_str_c      = "c";

// =============================================================================
// 0048cdf0 (1,364 bytes): UI screen tree draw and frame state advance
// =============================================================================
std::uint8_t CALL_THISCALL UiScreenContext::ui_draw_screen_tree_0048cdf0() {
    UiScreenNode* node = g_ui_screen_node_00628c70;
    call_0048c870(this->field_c, 0xbd, static_cast<std::uint32_t>(node->field_dc), 0x80000000, 0, 0);
    sub_0055ec50(5, s_str_high1);

    while (true) {
        sub_004a4a70(-1);
        node = g_ui_screen_node_00628c70;
        if (!node || !node->active_element) break;
        if (node->field_bf == 0 && node->field_c5 != 0) return 0;
        if (!node->active_element || node->field_bf != 0 || node->field_be == 0 || node->field_dc < 0) break;
        if (sub_0055ff60() == 0x1b) break;
        sub_0055f740(1);
        sub_005366e0(0);
        std::uint16_t ax = this->field_e5;
        std::uint16_t dx = *reinterpret_cast<std::uint16_t*>(&this->field_e6);
        if ((dx & ax) == ax) {
            goto phase_2;
        }
    }

    sub_0055ec50(5, s_str_abort);
    node = g_ui_screen_node_00628c70;
    if (!node || !node->active_element || node->field_bf != 0 || node->field_be == 0 || node->field_dc < 0 || node->field_c5 != 0) {
        return 0;
    }
    node->field_c5 = 1;
    node = g_ui_screen_node_00628c70;
    node->field_bc = 1;
    node->field_c4 = 0;
    sub_0048da60(-2, -1);
    return 0;

phase_2:
    node = g_ui_screen_node_00628c70;
    call_0048c870(this->field_c, 0xbd, static_cast<std::uint32_t>(node->field_dc + 8), 0x80000000, 0, 0);
    sub_0055ec50(5, s_str_high2);

    while (true) {
        sub_004a4a70(-1);
        node = g_ui_screen_node_00628c70;
        if (!node || !node->active_element) break;
        if (node->field_bf == 0 && node->field_c5 != 0) return 0;
        if (!node->active_element || node->field_bf != 0 || node->field_be == 0 || node->field_dc < 0) break;
        if (sub_0055ff60() == 0x1b) break;
        sub_0055f740(1);
        sub_005366e0(0);
        std::uint16_t ax = this->field_e5;
        std::uint16_t cx = this->field_e7;
        if ((cx & ax) == ax) {
            goto phase_3;
        }
    }

    sub_0055ec50(5, s_str_abort);
    node = g_ui_screen_node_00628c70;
    if (!node || !node->active_element || node->field_bf != 0 || node->field_be == 0 || node->field_dc < 0 || node->field_c5 != 0) {
        return 0;
    }
    node->field_c5 = 1;
    node = g_ui_screen_node_00628c70;
    node->field_bc = 1;
    node->field_c4 = 0;
    sub_0048da60(-2, -1);
    return 0;

phase_3:
    node = g_ui_screen_node_00628c70;
    call_0048c870(this->field_c, 0xbd, static_cast<std::uint32_t>(node->field_dc), 0x80000000, 0, 0);
    sub_0055ec50(5, s_str_low1);

    while (true) {
        sub_004a4a70(-1);
        node = g_ui_screen_node_00628c70;
        if (!node || !node->active_element) break;
        if (node->field_bf == 0 && node->field_c5 != 0) return 0;
        if (!node->active_element || node->field_bf != 0 || node->field_be == 0 || node->field_dc < 0) break;
        if (sub_0055ff60() == 0x1b) break;
        sub_0055f740(1);
        sub_005366e0(0);
        std::uint8_t al = this->field_e5;
        std::uint8_t cl = this->field_e6;
        if ((cl & al) == 0) {
            goto phase_4;
        }
    }

    sub_0055ec50(5, s_str_abort);
    node = g_ui_screen_node_00628c70;
    if (!node || !node->active_element || node->field_bf != 0 || node->field_be == 0 || node->field_dc < 0 || node->field_c5 != 0) {
        return 0;
    }
    node->field_c5 = 1;
    node = g_ui_screen_node_00628c70;
    node->field_bc = 1;
    node->field_c4 = 0;
    node = g_ui_screen_node_00628c70;
    if (!node || !node->active_element || node->field_bf != 0) return 0;
    {
        void** cont = reinterpret_cast<void**>(node->container);
        sub_005322b0(cont ? *cont : nullptr);
        node = g_ui_screen_node_00628c70;
        call_0048d350(node->manager, 0xb7, -2, -1, 0);
        node = g_ui_screen_node_00628c70;
        node->field_bd = 1;
        sub_005322c0(cont ? *cont : nullptr);
    }
    return 0;

phase_4:
    node = g_ui_screen_node_00628c70;
    call_0048c870(this->field_c, 0xbd, static_cast<std::uint32_t>(node->field_dc + 8), 0x80000000, 0, 0);
    sub_0055ec50(5, s_str_low2);

    while (true) {
        sub_004a4a70(-1);
        node = g_ui_screen_node_00628c70;
        if (!node || !node->active_element) break;
        if (node->field_bf == 0 && node->field_c5 != 0) return 0;
        if (!node->active_element || node->field_bf != 0 || node->field_be == 0 || node->field_dc < 0) break;
        if (sub_0055ff60() == 0x1b) break;
        sub_0055f740(1);
        sub_005366e0(0);
        std::uint8_t cl = this->field_e5;
        std::uint8_t al = this->field_e7;
        if ((cl & al) == 0) {
            return 1;
        }
    }

    sub_0055ec50(5, s_str_abort);
    node = g_ui_screen_node_00628c70;
    if (!node || !node->active_element || node->field_bf != 0 || node->field_be == 0 || node->field_dc < 0 || node->field_c5 != 0) {
        return 0;
    }
    node->field_c5 = 1;
    node = g_ui_screen_node_00628c70;
    node->field_bc = 1;
    node->field_c4 = 0;
    node = g_ui_screen_node_00628c70;
    if (!node || !node->active_element || node->field_bf != 0) return 0;
    {
        void** cont = reinterpret_cast<void**>(node->container);
        sub_005322b0(cont ? *cont : nullptr);
        node = g_ui_screen_node_00628c70;
        call_0048c870(node->manager, 0xb7, static_cast<std::uint32_t>(-2), static_cast<std::uint32_t>(-1), 0, 0);
        node = g_ui_screen_node_00628c70;
        node->field_bd = 1;
        sub_005322c0(cont ? *cont : nullptr);
    }
    return 0;
}

// =============================================================================
// 0048dcb0 (1,250 bytes): UI screen refresh and layout coordinator
// =============================================================================
void CALL_THISCALL UiScreenContext::ui_screen_refresh_0048dcb0(const char* title, std::uint32_t /*param2*/) {
    UiScreenNode* node = g_ui_screen_node_00628c70;
    if (!node) return;
    if (this->field_28 == 0) {
        if (!node->mode_0_flag) return;
    } else if (this->field_28 == 1) {
        if (!node->mode_1_flag) return;
    } else if (this->field_28 == 2) {
        if (!sub_0055eb70(0)) return;
    } else {
        return;
    }

    call_0048dbe0(this);

    char buf[0x34];
    if (!title) {
        sub_0053c290(buf, 0, 0x34);
        sub_005a28a0(buf + 0xc, s_str_nfsnet, 0x1f);
        buf[0x1b] = 0;
        *reinterpret_cast<std::uint32_t*>(buf + 0x2c) = 8;
    } else {
        sub_005323e0(buf, title, 0x34);
    }

    if (buf[4] == '\0') {
        fast_strcpy(buf + 4, s_str_game);
    }
    fast_strcat(buf + 4, s_str_tilde);
    node = g_ui_screen_node_00628c70;
    if (node && node->name[0]) {
        fast_strcat(buf + 4, node->name);
    } else {
        fast_strcat(buf + 4, s_str_00);
    }

    node = g_ui_screen_node_00628c70;
    if (node && node->active_element && node->field_bf == 0 && node->field_be != 0 && node->field_dc >= 0) {
        std::uint8_t pkt[0x50];
        sub_0053c290(pkt + 8, 0, 0x4c);
        pkt[8] = 0xb4;
        sub_005323e0(pkt + 0x28, buf + 0x10, 0x34);
        struct NetDispatcher {
            void*** vtbl;
        };
        NetDispatcher* disp = reinterpret_cast<NetDispatcher*>(this->field_c);
        if (disp && disp->vtbl) {
            typedef void (CALL_STDCALL *SendPktFn)(std::uint32_t, void*, std::uint32_t);
            SendPktFn fn = reinterpret_cast<SendPktFn>(disp->vtbl[0][0]);
            if (fn) fn(0, pkt, 0x50);
        }
        goto tail_label;
    }

    if (this->field_c1 != 0) {
        if (this->field_be == 0) {
            if (this->field_28 == 0) {
                call_0048e9c0(this);
                node = g_ui_screen_node_00628c70;
                if (node) {
                    reinterpret_cast<UiScreenContext*>(node)->ui_screen_render_present_0048e1a0(0, 0, nullptr);
                }
            } else if (this->field_28 == 2) {
                call_0048e9c0(this);
                node = g_ui_screen_node_00628c70;
                if (node) {
                    reinterpret_cast<UiScreenContext*>(node)->ui_screen_render_present_0048e1a0(2, 0, nullptr);
                }
            } else {
                if (this->field_c6 != 0) {
                    call_0048dbb0(this);
                    call_0048c870(this->field_c, 0xba, 0x80000000, 0x80000000, 0, 0);
                } else {
                    call_0048e9c0(this);
                }
            }
        } else {
            std::uint8_t pkt[0x50];
            sub_0053c290(pkt + 8, 0, 0x4c);
            pkt[8] = 0xb4;
            sub_005323e0(pkt + 0x28, buf + 0x10, 0x34);
            struct NetDispatcher {
                void*** vtbl;
            };
            NetDispatcher* disp = reinterpret_cast<NetDispatcher*>(this->field_c);
            if (disp && disp->vtbl) {
                typedef void (CALL_STDCALL *SendPktFn)(std::uint32_t, void*, std::uint32_t);
                SendPktFn fn = reinterpret_cast<SendPktFn>(disp->vtbl[0][0]);
                if (fn) fn(0, pkt, 0x50);
            }
            this->field_c6 = 1;
            goto tail_label;
        }
    }

    {
        this->field_24 = 2;
        std::uint32_t target = 0;
        std::uint32_t saved_edx = 0;
        if (this->field_28 == 0) {
            target = this->field_0;
            if (g_byte_005d0728 != 0) {
                g_byte_005d0728 = 0;
                char net_buf[0x34];
                sub_0053c290(net_buf, 0, 0x34);
                if (title) {
                    sub_005323e0(net_buf, title, 0x34);
                } else {
                    sub_005323e0(net_buf, s_str_nfsnet, 7);
                }
                std::uint32_t res = sub_0055aaa0(g_dword_00508e70, target, g_dword_005b4980, net_buf, 0, 0, 0);
                sub_0055bfd0(res);
            }
        } else if (this->field_28 == 1) {
            target = this->field_4;
            saved_edx = g_dword_005b4990;
        } else if (this->field_28 == 2) {
            target = 1;
        }

        std::uint32_t saved_mode = this->field_28;
        call_0048e9c0(this);
        if (saved_mode == 1) {
            sub_0048c4d0();
            this->field_c7 = 1;
        }

        void* elem = sub_0059ef90(0x14);
        if (elem) {
            node = g_ui_screen_node_00628c70;
            const char* node_name = (node && node->name[0]) ? node->name : s_str_00;
            call_0048aa10(elem, 3, reinterpret_cast<void*>(0x0048f040), this, s_str_c, this->field_a8, node_name, reinterpret_cast<void*>(0x005e8e50), 0);
        }
        this->field_8 = elem;

        struct ListNode {
            void* data;
            void* next;
        };
        ListNode* lnode = reinterpret_cast<ListNode*>(sub_0059ef90(8));
        if (lnode) {
            lnode->data = this->field_8;
            lnode->next = nullptr;
        }
        this->field_c = lnode;
        this->field_c1 = (target == this->field_0) ? 1 : 0;
        this->field_28 = saved_mode;
        this->field_24 = 0;
        this->field_c0 = 0;
        this->field_c6 = 0;
        this->field_bf = 0;
        this->field_e0 = 0;
        this->field_c2 = 0;
        this->field_1c = sub_0048a9a0() << 5;
        sub_00560140(reinterpret_cast<void*>(0x0048ee90));
        this->field_106 = 1;

        if (g_dword_00628c74 == 0) {
            void* child = sub_0059ef90(0x188);
            if (child) {
                call_00491cd0(child, target, buf + 0x10, this->field_8, 0, saved_edx, -1);
            }
        }
        this->field_c2 = 1;
    }

tail_label:
    if (g_dword_00657aa4 == 1) {
        if (!this->field_14) {
            void* pres = sub_0059ef90(0x74);
            if (pres) {
                this->field_14 = call_004931c0(pres, this->field_c);
            } else {
                this->field_14 = nullptr;
            }
        }
    }
}

// =============================================================================
// 0048e1a0 (1,357 bytes): UI screen render, child list traversal & presentation
// =============================================================================
void CALL_THISCALL UiScreenContext::ui_screen_render_present_0048e1a0(std::uint32_t mode, std::uint32_t id, const char* title) {
    UiScreenNode* node = g_ui_screen_node_00628c70;
    if (!node) return;
    if (mode == 0) {
        if (!node->mode_0_flag) return;
    } else if (mode == 1) {
        if (!node->mode_1_flag) return;
    } else if (mode == 2) {
        if (!sub_0055eb70(0)) return;
    } else {
        return;
    }

    call_0048dbe0(this);

    if (mode == 0) {
        if (this->field_c1 && this->field_106) {
            struct ChildEntry {
                ChildEntry* next;
                void* pad;
                struct Elem {
                    std::uint8_t pad[0xb0];
                    std::uint32_t id;
                }* elem;
            };
            ChildEntry* head = reinterpret_cast<ChildEntry*>(this->field_25c);
            if (head) {
                ChildEntry* cur = head->next;
                while (cur != head) {
                    if (cur->elem && cur->elem->id == id) {
                        this->field_24 = 3;
                        call_0048ac70(this->field_8, cur->elem);
                        goto tail_check;
                    }
                    cur = cur->next;
                }
            }
            return;
        }

        call_0048e9c0(this);
        void** cont = reinterpret_cast<void**>(this->field_10);
        sub_005322b0(cont ? *cont : nullptr);
        void* elem = sub_0059ef90(0x14);
        if (elem) {
            node = g_ui_screen_node_00628c70;
            const char* node_name = (node && node->name[0]) ? node->name : s_str_00;
            call_0048aa10(elem, this->field_0, reinterpret_cast<void*>(0x0048f040), this, s_str_c, this->field_a8, node_name, reinterpret_cast<void*>(0x005e8e50), 0);
        }
        this->field_8 = elem;

        struct ListNode {
            void* data;
            void* next;
        };
        ListNode* lnode = reinterpret_cast<ListNode*>(sub_0059ef90(8));
        if (lnode) {
            lnode->data = this->field_8;
            lnode->next = nullptr;
        }
        this->field_c = lnode;
        this->field_c1 = 1;
        this->field_28 = 0;
        this->field_24 = 0;
        this->field_c0 = 0;
        this->field_c6 = 0;
        this->field_bf = 0;
        this->field_e0 = 0;
        this->field_c2 = 0;
        this->field_1c = sub_0048a9a0() << 5;
        this->field_24 = 1;
        sub_00560140(reinterpret_cast<void*>(0x0048ee90));
        this->field_106 = 1;
        call_0048ac50(this->field_8);
        if (g_pfn_005b2080) {
            this->field_148 = g_pfn_005b2080();
        }
        sub_005322c0(cont ? *cont : nullptr);
        return;
    } else if (mode == 1) {
        if (!title) {
            node = g_ui_screen_node_00628c70;
            if (!node || !node->active_element || node->field_bf != 0 || node->field_be == 0) return;
            call_0048c870(this->field_c, 0xb6, id, 0x80000000, 0, 0);
            this->field_c6 = 1;
            goto tail_check;
        }

        call_0048e9c0(this);
        void** cont = reinterpret_cast<void**>(this->field_10);
        sub_005322b0(cont ? *cont : nullptr);
        sub_0048c4d0();
        this->field_c7 = 1;

        void* elem = sub_0059ef90(0x14);
        if (elem) {
            node = g_ui_screen_node_00628c70;
            const char* node_name = (node && node->name[0]) ? node->name : s_str_00;
            call_0048aa10(elem, this->field_4, reinterpret_cast<void*>(0x0048f040), this, this->field_58, this->field_a8, node_name, this->field_98, 0);
        }
        this->field_8 = elem;

        struct ListNode {
            void* data;
            void* next;
        };
        ListNode* lnode = reinterpret_cast<ListNode*>(sub_0059ef90(8));
        if (lnode) {
            lnode->data = this->field_8;
            lnode->next = nullptr;
        }
        this->field_c = lnode;
        this->field_c1 = 0;
        this->field_24 = 0;
        this->field_c0 = 0;
        this->field_c6 = 0;
        this->field_bf = 0;
        this->field_e0 = 0;
        this->field_c2 = 0;
        this->field_1c = sub_0048a9a0() << 5;
        this->field_24 = 3;
        sub_00560140(reinterpret_cast<void*>(0x0048ee90));
        this->field_106 = 1;
        call_0048ac90(this->field_8, const_cast<char*>(title), g_dword_005b4990);

        if (g_dword_00657aa4 == 1 && !this->field_14) {
            void* pres = sub_0059ef90(0x74);
            if (pres) {
                this->field_14 = call_004931c0(pres, this->field_c);
            } else {
                this->field_14 = nullptr;
            }
        }
        sub_005322c0(cont ? *cont : nullptr);
        return;
    } else if (mode == 2) {
        if (!title) {
            call_0048e9c0(this);
            std::uint32_t slot = 0;
            std::uint32_t item = sub_0055eb70(0);
            while (item) {
                void* block = sub_0059ef90(0x44);
                if (block) {
                    struct ItemRef {
                        std::uint8_t pad[8];
                        std::uint32_t val;
                    };
                    ItemRef* iref = reinterpret_cast<ItemRef*>(item);
                    call_0048c840(block, iref ? iref->val : 0, id);
                }
                void* pair[2] = { nullptr, block };
                void* iter = call_00529050(this->field_254, &pair[0]);
                call_0050e140(iter, &pair[0]);
                call_004937f0(this->field_254, &pair[0]);
                slot = id + 1;
                item = sub_0055eb70(slot);
            }
            this->field_28 = 2;
            return;
        }

        call_0048e9c0(this);
        this->field_28 = 2;
        void* elem = sub_0059ef90(0x14);
        if (elem) {
            node = g_ui_screen_node_00628c70;
            const char* node_name = (node && node->name[0]) ? node->name : s_str_00;
            call_0048aa10(elem, 1, reinterpret_cast<void*>(0x0048f040), this, s_str_c, this->field_a8, node_name, reinterpret_cast<void*>(0x005e8e50), reinterpret_cast<std::uint32_t>(title));
        }
        this->field_8 = elem;

        struct ListNode {
            void* data;
            void* next;
        };
        ListNode* lnode = reinterpret_cast<ListNode*>(sub_0059ef90(8));
        if (lnode) {
            lnode->data = this->field_8;
            lnode->next = nullptr;
        }
        this->field_c = lnode;
        this->field_c1 = 0;
        this->field_24 = 0;
        this->field_c0 = 0;
        this->field_c6 = 0;
        this->field_bf = 0;
        this->field_e0 = 0;
        this->field_c2 = 0;
        this->field_1c = sub_0048a9a0() << 5;
        this->field_24 = 3;
        sub_00560140(reinterpret_cast<void*>(0x0048ee90));
        this->field_106 = 1;
        call_0048ac90(this->field_8, const_cast<char*>(title), reinterpret_cast<std::uint32_t>(title));

        if (g_dword_00657aa4 == 1 && !this->field_14) {
            void* pres = sub_0059ef90(0x74);
            if (pres) {
                this->field_14 = call_004931c0(pres, this->field_c);
            } else {
                this->field_14 = nullptr;
            }
        }
        return;
    }

tail_check:
    if (g_dword_00657aa4 == 1 && !this->field_14) {
        void* pres = sub_0059ef90(0x74);
        if (pres) {
            this->field_14 = call_004931c0(pres, this->field_c);
        } else {
            this->field_14 = nullptr;
        }
    }
}

} // namespace porsche
