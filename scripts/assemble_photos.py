#!/usr/bin/env python3
"""
scripts/assemble_photos.py
==========================
Reconstitui com 100% de fidelidade canônica ao motor do Porsche Unleashed
(conforme FEChroniclePictureControl em VA 0x00508350) todas as imagens que
eram salvas como mosaicos/tiles (quebra-cabeças) dentro dos arquivos FSH:

1. FEData/Chron/ (Cronologia Histórica da Marca Porsche):
   - Mosaicos em grid de colunas/linhas variáveis reconstruídos nas resoluções
     originais completas (ex: 458x286, 458x650, 549x286, etc.).
   - Suporte canônico a paletas de 8-bit e formatos diretos 24/32-bit.

2. FEData/Showcase/ (Showcase dos Veículos Porsche):
   - Cada arquivo FSH contém 2 fotografias completas de alta definição
     (cada uma montada a partir de 4 quadrantes 2x2, totalizando 255x181).
"""

import os
import sys
import struct
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHRON_DIR = ROOT / "local" / "game" / "FEData" / "Chron"
SHOWCASE_DIR = ROOT / "local" / "game" / "FEData" / "Showcase"

OUT_CHRON = ROOT / "local" / "media" / "chronology"
OUT_SHOWCASE = ROOT / "local" / "media" / "showcase"

def decompress_qfs(data: bytes) -> bytes:
    if len(data) < 2:
        return data
    b0, b1 = data[0], data[1]
    if b0 != 0x10 or b1 != 0xfb:
        return data
    d = data[2:]
    out = bytearray()
    p = 0
    d_len = len(d)
    if d_len >= 3:
        p = 3  # Pula o tamanho descompactado de 3 bytes (big-endian)
    while p < d_len:
        c = d[p]
        p += 1
        if c < 0x80:
            if p >= d_len: break
            a = d[p]
            p += 1
            literal = c & 3
            count = ((c >> 2) & 7) + 3
            distance = ((c >> 5) << 8) + a + 1
        elif c < 0xc0:
            if p + 1 >= d_len: break
            ab0 = d[p]
            ab1 = d[p+1]
            p += 2
            literal = (ab0 >> 6)
            count = (c & 63) + 4
            distance = ((ab0 & 63) << 8) + ab1 + 1
        elif c < 0xe0:
            if p + 2 >= d_len: break
            ab0 = d[p]
            ab1 = d[p+1]
            ab2 = d[p+2]
            p += 3
            literal = c & 3
            count = ((c >> 2) & 3) * 256 + ab2 + 5
            distance = ((c & 16) << 12) + ab0 * 256 + ab1 + 1
        else:
            literal = ((c & 31) * 4 + 4) if c < 0xfc else (c & 3)
            count = 0
            distance = 0

        if literal > 0:
            out.extend(d[p : p + literal])
            p += literal

        if count > 0:
            for _ in range(count):
                out.append(out[-distance])

        if c >= 0xfc:
            break
    return bytes(out)

def decode_fsh_entries(dec: bytes):
    if len(dec) < 16 or dec[:4] != b"SHPI":
        return []
    total_len, n = struct.unpack("<II", dec[4:12])
    entries = []
    for i in range(n):
        entry_off = 16 + i * 8
        if entry_off + 8 > len(dec): break
        name = dec[entry_off:entry_off+4].decode("latin1", "ignore").strip("\x00 ")
        o = struct.unpack("<I", dec[entry_off+4:entry_off+8])[0]
        if o + 16 > len(dec): continue
        
        code = struct.unpack("<I", dec[o:o+4])[0]
        w, h, ox, oy = struct.unpack("<HHhh", dec[o+4:o+12])
        m1, m2 = struct.unpack("<hh", dec[o+12:o+16])
        
        code_byte = code & 0xff
        count = w * h
        img_data = None
        
        if code_byte == 0x7b:  # Paletted 8-bit
            pixels = dec[o+16 : o+16+count]
            pal_offset = o + (code >> 8)
            if pal_offset + 16 <= len(dec):
                pc = dec[pal_offset]
                pn = struct.unpack("<H", dec[pal_offset+4:pal_offset+6])[0]
                stride = 4 if pc == 0x2a else (3 if pc == 0x24 else 2)
                pal_bytes = dec[pal_offset+16 : pal_offset+16+pn*stride]
                rgba = bytearray(count * 4)
                for px, idx in enumerate(pixels):
                    idx_off = idx * stride
                    if idx_off + stride <= len(pal_bytes):
                        p = pal_bytes[idx_off : idx_off+stride]
                        if pc == 0x2a:
                            rgba[px*4 : px*4+4] = bytes([p[2], p[1], p[0], p[3]])
                        elif pc == 0x24:
                            rgba[px*4 : px*4+4] = bytes([p[2], p[1], p[0], 255])
                        elif pc == 0x29:
                            v = p[0] | (p[1] << 8)
                            rgba[px*4 : px*4+4] = bytes([((v>>11)&31)*255//31, ((v>>5)&63)*255//63, (v&31)*255//31, 255])
                        elif pc == 0x2d:
                            v = p[0] | (p[1] << 8)
                            rgba[px*4 : px*4+4] = bytes([((v>>10)&31)*255//31, ((v>>5)&31)*255//31, (v&31)*255//31, 255 if (v&0x8000) else 0])
                img_data = Image.frombytes("RGBA", (w, h), bytes(rgba))
        elif code_byte == 0x7d:  # 32-bit ARGB
            raw = dec[o+16 : o+16+count*4]
            if len(raw) == count * 4:
                rgba = bytearray(count * 4)
                for px in range(count):
                    rgba[px*4 : px*4+4] = bytes([raw[px*4+2], raw[px*4+1], raw[px*4], raw[px*4+3]])
                img_data = Image.frombytes("RGBA", (w, h), bytes(rgba))
        elif code_byte == 0x7f:  # 24-bit RGB
            raw = dec[o+16 : o+16+count*3]
            if len(raw) == count * 3:
                rgb = bytearray(count * 3)
                for px in range(count):
                    rgb[px*3 : px*3+3] = bytes([raw[px*3+2], raw[px*3+1], raw[px*3]])
                img_data = Image.frombytes("RGB", (w, h), bytes(rgb)).convert("RGBA")
                
        entries.append({
            "name": name, "w": w, "h": h, "ox": ox, "oy": oy, "m1": m1, "m2": m2, "img": img_data
        })
    return entries

def assemble_chronology_fsh(fsh_file: Path) -> list:
    dec = decompress_qfs(fsh_file.read_bytes())
    entries = decode_fsh_entries(dec)
    if not entries:
        return []
        
    stem = fsh_file.stem
    assembled = []
    
    # Verifica se os dois primeiros são botões/ícones de navegação (bi, ci, etc.)
    start_idx = 0
    if len(entries) > 2 and entries[0]["w"] < 50 and entries[1]["w"] < 50:
        start_idx = 2
        
    tiles = entries[start_idx:]
    if not tiles:
        return []
        
    # Verifica se há offsets negativos de posicionamento absoluto direto
    has_neg = any(t["ox"] < 0 or t["oy"] < 0 for t in tiles)
    
    if has_neg:
        # Modo absoluto (ex: p-files como pA481a):
        # Mapeia as posições relativas x = -ox, y = -oy
        min_x = min(-t["ox"] for t in tiles)
        min_y = min(-t["oy"] for t in tiles)
        max_x = max(-t["ox"] + t["w"] for t in tiles)
        max_y = max(-t["oy"] + t["h"] for t in tiles)
        
        full_w = max_x - min_x
        full_h = max_y - min_y
        
        canvas = Image.new("RGBA", (full_w, full_h), (0, 0, 0, 0))
        for t in tiles:
            if t["img"]:
                canvas.paste(t["img"], (-t["ox"] - min_x, -t["oy"] - min_y))
        assembled.append((f"{stem}.png", canvas))
    else:
        # Modo grid canônico (FEChroniclePictureControl VA 0x00508350):
        # Descobre colunas contando os tiles consecutivos com mesmo nome de linha ou calculando
        # a soma da largura que atinge ~458 ou ~549
        cols = 0
        w_sum = 0
        for t in tiles:
            w_sum += t["w"]
            cols += 1
            if w_sum in (458, 549) or (cols >= 4 and t["w"] < 50):
                break
        if cols == 0:
            cols = 4
            
        num_tiles = len(tiles)
        rows = num_tiles // cols
        if rows * cols != num_tiles:
            # Fallback seguro: se não bater certinho, pega o total
            rows = max(1, num_tiles // cols)
            
        row_heights = [tiles[r * cols]["h"] for r in range(rows)]
        col_widths = [tiles[c]["w"] for c in range(cols)]
        total_w = sum(col_widths)
        total_h = sum(row_heights)
        
        canvas = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
        y = 0
        for r in range(rows):
            x = 0
            rh = row_heights[r]
            for c in range(cols):
                tile_idx = r * cols + c
                if tile_idx < len(tiles):
                    t = tiles[tile_idx]
                    if t["img"]:
                        canvas.paste(t["img"], (x, y))
                    x += t["w"]
            y += rh
        assembled.append((f"{stem}.png", canvas))
        
    return assembled

def assemble_showcase_fsh(fsh_file: Path) -> list:
    dec = decompress_qfs(fsh_file.read_bytes())
    entries = decode_fsh_entries(dec)
    if not entries:
        return []
        
    stem = fsh_file.stem
    assembled = []
    
    # Cada Showcase FSH tem normalmente 8 tiles (2 fotos x 4 quadrantes 2x2 de 255x181)
    if len(entries) == 8:
        sets = [entries[0:4], entries[4:8]]
    elif len(entries) == 4:
        sets = [entries[0:4]]
    else:
        sets = [entries]
        
    same_names = (len(sets) == 2 and sets[0][0]["name"].lower() == sets[1][0]["name"].lower())
    
    for set_idx, s in enumerate(sets):
        img_name = s[0]["name"] if s[0]["name"] else f"photo_{set_idx+1}"
        if same_names:
            # Verifica se os pixels do set 0 e set 1 são diferentes
            p0 = sets[0][0]["img"].tobytes() if sets[0][0]["img"] else b""
            p1 = sets[1][0]["img"].tobytes() if sets[1][0]["img"] else b""
            if p0 == p1 and set_idx == 1:
                # É uma cópia idêntica exata, não precisa duplicar
                continue
            elif p0 != p1:
                img_name = f"{img_name}_{set_idx+1}"
                
        has_neg = any(t["ox"] < 0 or t["oy"] < 0 for t in s)
        canvas = Image.new("RGBA", (255, 181), (0, 0, 0, 0))
        if has_neg:
            for t in s:
                if t["img"]:
                    canvas.paste(t["img"], (-t["ox"], -t["oy"]))
        else:
            base_m1 = min(t["m1"] for t in s)
            base_m2 = min(t["m2"] for t in s)
            for t in s:
                if t["img"]:
                    canvas.paste(t["img"], (t["m1"] - base_m1, t["m2"] - base_m2))
        out_name = f"{stem}_{img_name}.png"
        assembled.append((out_name, canvas))
        
    return assembled

def main():
    print("=" * 70)
    print("MONTADOR DE QUEBRA-CABEÇAS DE FOTOS (NEED FOR SPEED: PORSCHE UNLEASHED)")
    print("=" * 70)
    
    OUT_CHRON.mkdir(parents=True, exist_ok=True)
    OUT_SHOWCASE.mkdir(parents=True, exist_ok=True)
    
    # Limpa arquivos fragmentados antigos
    for f in OUT_CHRON.glob("*.png"):
        try: f.unlink()
        except: pass
    for f in OUT_SHOWCASE.glob("*.png"):
        try: f.unlink()
        except: pass

    # 1. Montagem da Cronologia
    chron_fsh = sorted(CHRON_DIR.glob("*.fsh"))
    chron_saved = 0
    print(f"\n[1/2] Processando {len(chron_fsh)} arquivos FSH da Cronologia...")
    for fsh in chron_fsh:
        if fsh.stem.startswith("icons"):
            continue
        results = assemble_chronology_fsh(fsh)
        for name, img in results:
            out_file = OUT_CHRON / name
            img.save(out_file)
            chron_saved += 1
            print(f"  [CHRON OK] {fsh.name} -> {name} ({img.width}x{img.height})")

    # 2. Montagem do Showcase
    showcase_fsh = sorted(SHOWCASE_DIR.glob("*.fsh"))
    showcase_saved = 0
    print(f"\n[2/2] Processando {len(showcase_fsh)} arquivos FSH do Showcase dos Carros...")
    for fsh in showcase_fsh:
        results = assemble_showcase_fsh(fsh)
        for name, img in results:
            out_file = OUT_SHOWCASE / name
            img.save(out_file)
            showcase_saved += 1
            print(f"  [SHOWCASE OK] {fsh.name} -> {name} ({img.width}x{img.height})")

    print("\n" + "=" * 70)
    print(f"Concluído com sucesso!")
    print(f"Fotos completas da Cronologia: {chron_saved} imagens salvas em local/media/chronology/")
    print(f"Fotos completas do Showcase:   {showcase_saved} imagens salvas em local/media/showcase/")
    print("=" * 70)

if __name__ == "__main__":
    main()
