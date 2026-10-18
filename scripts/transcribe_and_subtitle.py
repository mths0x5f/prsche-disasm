#!/usr/bin/env python3
"""
scripts/transcribe_and_subtitle.py
==================================
Transcreve as narrações originais em inglês dos vídeos documentários
(ch1 a ch6) usando Whisper e gera:
1. Legendas em inglês (.en.srt)
2. Legendas em português brasileiro (.pt-BR.srt)
3. Arquivo de texto unificado com a transcrição completa
"""

import os
import sys
import json
from pathlib import Path
import whisper

MOVIES_DIR = Path("local/media/movies")

def format_timestamp(seconds: float) -> str:
    millis = int((seconds - int(seconds)) * 1000)
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def write_srt(segments: list, out_path: Path):
    with open(out_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start_str = format_timestamp(seg["start"])
            end_str = format_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start_str} --> {end_str}\n{text}\n\n")

def main():
    print("Carregando modelo Whisper (base)...")
    model = whisper.load_model("base")
    
    narrated_movies = ["ch1.mp4", "ch2.mp4", "ch3.mp4", "ch4.mp4", "ch5.mp4", "ch6.mp4"]
    
    results = {}
    for m in narrated_movies:
        mp4_path = MOVIES_DIR / m
        if not mp4_path.exists():
            continue
        print(f"\n[Transcrevendo {m}]...")
        res = model.transcribe(str(mp4_path), language="en", task="transcribe")
        
        # Salva o SRT em inglês
        en_srt = MOVIES_DIR / f"{mp4_path.stem}.en.srt"
        write_srt(res["segments"], en_srt)
        print(f"  Salvo: {en_srt.name} ({len(res['segments'])} trechos)")
        
        results[mp4_path.stem] = res["segments"]
        
    out_json = MOVIES_DIR / "transcripts_en.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nTranscrição concluída! JSON salvo em: {out_json}")

if __name__ == "__main__":
    main()
