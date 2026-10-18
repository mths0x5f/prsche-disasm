import os
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIV_PATH = ROOT / "local/game/GameData/Music/zzzymus.viv"
OUTPUT_DIR = ROOT / "local/soundtrack"

def get_ffmpeg_path():
    # Check PATH or standard winget location
    for path in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(path) / "ffmpeg.exe"
        if candidate.is_file():
            return str(candidate)
    return "ffmpeg"

def parse_viv(viv_path):
    tracks = []
    with open(viv_path, "rb") as f:
        magic, total_size, count, header_end = struct.unpack(">4sIII", f.read(16))
        assert magic == b"BIGF", f"Invalid magic: {magic}"
        for i in range(count):
            offset, file_len = struct.unpack(">II", f.read(8))
            name_bytes = bytearray()
            while True:
                c = f.read(1)
                if c == b"\x00" or not c:
                    break
                name_bytes += c
            name = name_bytes.decode("latin1", "ignore").strip()
            tracks.append((i + 1, name, offset, file_len))
    return tracks

def convert_track(track_info, ffmpeg_bin):
    num, name, offset, file_len = track_info
    clean_name = f"{num:02d} - {name}"
    asf_path = OUTPUT_DIR / f"{clean_name}.asf"
    mp3_path = OUTPUT_DIR / f"{clean_name}.mp3"
    
    if mp3_path.is_file() and mp3_path.stat().st_size > 0:
        return f"[SKIP] {clean_name} already exists."
        
    with open(VIV_PATH, "rb") as f:
        f.seek(offset)
        data = f.read(file_len)
        asf_path.write_bytes(data)
        
    # Convert with ffmpeg
    cmd = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(asf_path),
        "-metadata", f"title={name}",
        "-metadata", "album=Need for Speed: Porsche Unleashed (2000)",
        "-metadata", "genre=Electronic",
        str(mp3_path)
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode == 0:
        asf_path.unlink(missing_ok=True)
        return f"[OK]   {clean_name}.mp3 ({mp3_path.stat().st_size:,} bytes)"
    else:
        return f"[FAIL] {clean_name}: {res.stderr.decode('utf8', 'ignore')}"

def main():
    if not VIV_PATH.is_file():
        print(f"Error: {VIV_PATH} not found.")
        sys.exit(1)
        
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_path()
    print(f"Reading soundtrack archive: {VIV_PATH}...")
    tracks = parse_viv(VIV_PATH)
    print(f"Found {len(tracks)} tracks. Extracting and converting to MP3 in parallel...")
    print("-" * 65)
    
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(convert_track, t, ffmpeg_bin) for t in tracks]
        for f in futures:
            print(f.result())
            
    print("-" * 65)
    print(f"Soundtrack extraction complete! Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
