; Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
;
; Run 429: frame root storage 00628940..00628a64 as ONE zero-fill block with the
; original offsets (the original .data virtual tail). The labels are the three
; names Run 419's header declares. The bytes after 00628968 include cells used by
; unrecovered code (006289e4..00628a20); they are part of the block, not objects.
.686
.model flat
option casemap:none

PUBLIC ?g_frame_root_track_name_00628940@porsche@@3PADA
PUBLIC ?frame_service_root_00628960@porsche@@3IA
PUBLIC ?g_frame_root_formatted_path_00628964@porsche@@3PADA

_FROOT SEGMENT ALIGN(64) READ WRITE 'BSS'
; 00628940..0062895f: char g_frame_root_track_name_00628940[32]
?g_frame_root_track_name_00628940@porsche@@3PADA LABEL BYTE
    BYTE 020h DUP (?)
; 00628960..00628963: std::uint32_t frame_service_root_00628960
?frame_service_root_00628960@porsche@@3IA LABEL BYTE
    BYTE 04h DUP (?)
; 00628964..00628a63: char g_frame_root_formatted_path_00628964[256] (as declared)
?g_frame_root_formatted_path_00628964@porsche@@3PADA LABEL BYTE
    BYTE 0100h DUP (?)
_FROOT ENDS
END
