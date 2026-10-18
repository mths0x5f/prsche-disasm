import os
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MOVIES_DIR = ROOT / "local/game/FEData/Movies"
CHRON_DIR = ROOT / "local/game/FEData/Chron"
SHOWCASE_DIR = ROOT / "local/game/FEData/Showcase"
OUTPUT_DIR = ROOT / "local/media"

def get_ffmpeg_path():
    for path in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(path) / "ffmpeg.exe"
        if candidate.is_file():
            return str(candidate)
    return "ffmpeg"

def decompress_qfs(d):
    if len(d) < 5 or d[0] != 0x10 or d[1] != 0xfb:
        return d
    size = (d[2] << 16) | (d[3] << 8) | d[4]
    out = bytearray()
    p = 5
    d_len = len(d)
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

def parse_fsh(data):
    decoded = decompress_qfs(data)
    if len(decoded) < 16 or decoded[:4] != b"SHPI":
        return []
    total_len = struct.unpack("<I", decoded[4:8])[0]
    n = struct.unpack("<I", decoded[8:12])[0]
    images = []
    for i in range(n):
        entry_off = 16 + i * 8
        if entry_off + 8 > len(decoded): break
        name = decoded[entry_off:entry_off+4].decode("latin1", "ignore").strip("\x00 ").lower()
        o = struct.unpack("<I", decoded[entry_off+4:entry_off+8])[0]
        if o + 16 > len(decoded): continue
        code = struct.unpack("<I", decoded[o:o+4])[0]
        width, height = struct.unpack("<HH", decoded[o+4:o+8])
        if width == 0 or height == 0 or width > 4096 or height > 4096:
            continue
        count = width * height
        code_byte = code & 0xff
        img_data = None

        if code_byte == 0x7d: # 32-bit ARGB
            raw = decoded[o+16 : o+16+count*4]
            if len(raw) == count * 4:
                rgba = bytearray(count * 4)
                for px in range(count):
                    b = raw[px*4]
                    g = raw[px*4+1]
                    r = raw[px*4+2]
                    a = raw[px*4+3]
                    rgba[px*4 : px*4+4] = bytes([r, g, b, a])
                img_data = Image.frombytes("RGBA", (width, height), bytes(rgba))

        elif code_byte == 0x7f: # 24-bit RGB
            raw = decoded[o+16 : o+16+count*3]
            if len(raw) == count * 3:
                rgb = bytearray(count * 3)
                for px in range(count):
                    b = raw[px*3]
                    g = raw[px*3+1]
                    r = raw[px*3+2]
                    rgb[px*3 : px*3+3] = bytes([r, g, b])
                img_data = Image.frombytes("RGB", (width, height), bytes(rgb))

        elif code_byte == 0x7b: # Paletted 8-bit
            pixels = decoded[o+16 : o+16+count]
            pal_offset = o + (code >> 8)
            if pal_offset + 16 <= len(decoded):
                pc = decoded[pal_offset]
                pn = struct.unpack("<H", decoded[pal_offset+4:pal_offset+6])[0]
                stride = 4 if pc == 0x2a else (3 if pc == 0x24 else 2)
                pal_bytes = decoded[pal_offset+16 : pal_offset+16+pn*stride]
                
                rgba = bytearray(count * 4)
                for px, idx in enumerate(pixels):
                    idx_off = idx * stride
                    if idx_off + stride <= len(pal_bytes):
                        p = pal_bytes[idx_off : idx_off+stride]
                        if pc == 0x2a:
                            rgba[px*4 : px*4+4] = bytes([p[2], p[1], p[0], p[3]])
                        elif pc == 0x24:
                            rgba[px*4 : px*4+4] = bytes([p[2], p[1], p[0], 255])
                        elif pc == 0x29: # RGB565
                            v = p[0] | (p[1] << 8)
                            r = ((v >> 11) & 31) * 255 // 31
                            g = ((v >> 5) & 63) * 255 // 63
                            b = (v & 31) * 255 // 31
                            rgba[px*4 : px*4+4] = bytes([r, g, b, 255])
                        elif pc == 0x2d: # ARGB1555
                            v = p[0] | (p[1] << 8)
                            r = ((v >> 10) & 31) * 255 // 31
                            g = ((v >> 5) & 31) * 255 // 31
                            b = (v & 31) * 255 // 31
                            a = 255 if (v & 0x8000) else 0
                            rgba[px*4 : px*4+4] = bytes([r, g, b, a])
                img_data = Image.frombytes("RGBA", (width, height), bytes(rgba))

        if img_data:
            images.append((name, img_data))
    return images

def process_fsh_file(fsh_path, out_dir):
    try:
        data = fsh_path.read_bytes()
        images = parse_fsh(data)
        count = 0
        stem = fsh_path.stem
        for idx, (name, img) in enumerate(images):
            # Prefer larger resolution images (ignore tiny icons/masks)
            if img.width < 64 or img.height < 64:
                continue
            suffix = f"_{name}" if name else f"_{idx}"
            out_file = out_dir / f"{stem}{suffix}.png"
            img.save(out_file, "PNG")
            count += 1
        return f"[FSH OK] {fsh_path.name}: {count} image(s)"
    except Exception as e:
        return f"[FSH ERR] {fsh_path.name}: {e}"

def convert_mad_movie(mad_path, out_dir, ffmpeg_bin):
    out_mp4 = out_dir / f"{mad_path.stem}.mp4"
    if out_mp4.is_file() and out_mp4.stat().st_size > 0:
        return f"[MOV SKIP] {mad_path.name} already converted"
    cmd = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(mad_path),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k",
        str(out_mp4)
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode == 0:
        return f"[MOV OK] {mad_path.name} -> {out_mp4.name} ({out_mp4.stat().st_size:,} bytes)"
    else:
        return f"[MOV ERR] {mad_path.name}: {res.stderr.decode('utf8', 'ignore')}"

def main():
    movies_out = OUTPUT_DIR / "movies"
    chron_out = OUTPUT_DIR / "chronology"
    showcase_out = OUTPUT_DIR / "showcase"
    for d in (movies_out, chron_out, showcase_out):
        d.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = get_ffmpeg_path()

    print("=" * 65)
    print("EXTRAÇÃO DOS VÍDEOS HISTÓRICOS (.mad -> .mp4)")
    print("=" * 65)
    mad_files = sorted(MOVIES_DIR.glob("*.mad"))
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = [pool.submit(convert_mad_movie, m, movies_out, ffmpeg_bin) for m in mad_files]
        for f in futs:
            print(f.result())

    print("\n" + "=" * 65)
    print("EXTRAÇÃO DAS FOTOS DA CRONOLOGIA (.fsh -> .png)")
    print("=" * 65)
    chron_files = sorted(CHRON_DIR.glob("*.fsh"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = [pool.submit(process_fsh_file, f, chron_out) for f in chron_files]
        for f in futs:
            print(f.result())

    print("\n" + "=" * 65)
    print("EXTRAÇÃO DAS FOTOS DO SHOWCASE DE CARROS (.fsh -> .png)")
    print("=" * 65)
    showcase_files = sorted(SHOWCASE_DIR.glob("*.fsh"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = [pool.submit(process_fsh_file, f, showcase_out) for f in showcase_files]
        for f in futs:
            print(f.result())

    print("\n" + "=" * 65)
    print("Extração concluída com sucesso!")
    print(f"Vídeos em:    {movies_out}")
    print(f"Cronologia:   {chron_out}")
    print(f"Showcase:     {showcase_out}")

if __name__ == "__main__":
    main()
