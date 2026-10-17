#!/usr/bin/env python3
"""
coverage.py - Verifica o status e a cobertura das traduções para pt-BR dos arquivos .md
"""

import os
import sys

EXCLUDE_DIRS = {'.git', 'local', '.cursor', '__pycache__', '.pytest_cache', 'target'}

def scan_markdown_files(root_dir='.'):
    source_mds = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclui pastas irrelevantes
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        for f in filenames:
            if f.endswith('.md') and not f.endswith('.pt-BR.md'):
                source_mds.append(os.path.join(dirpath, f))
    return sorted(source_mds)

def main():
    root = '.'
    files = scan_markdown_files(root)
    
    total = len(files)
    translated = 0
    missing = []
    outdated = []
    up_to_date = []
    
    for src in files:
        base, ext = os.path.splitext(src)
        pt_br = f"{base}.pt-BR.md"
        
        if not os.path.exists(pt_br):
            missing.append(src)
        else:
            translated += 1
            src_mtime = os.path.getmtime(src)
            trans_mtime = os.path.getmtime(pt_br)
            if src_mtime > trans_mtime:
                outdated.append((src, pt_br))
            else:
                up_to_date.append((src, pt_br))
                
    pct = (translated / total * 100) if total > 0 else 0
    print(f"\n=== Relatório de Cobertura de Tradução (pt-BR) ===")
    print(f"Total de arquivos .md encontrados: {total}")
    print(f"Arquivos traduzidos: {translated} ({pct:.1f}%)")
    print(f"Arquivos pendentes: {len(missing)}")
    print(f"Arquivos possivelmente desatualizados: {len(outdated)}\n")
    
    if up_to_date:
        print("[OK] Arquivos com tradução em dia:")
        for s, t in up_to_date:
            print(f"  ✓ {s} -> {t}")
        print()
        
    if outdated:
        print("[ATENÇÃO] Traduções desatualizadas (original mais recente):")
        for s, t in outdated:
            print(f"  ⚠ {s} (atualize {t})")
        print()
        
    if missing:
        print("[PENDENTE] Arquivos sem tradução pt-BR:")
        for m in missing[:30]:  # Limita para não inundar o terminal
            print(f"  ✗ {m}")
        if len(missing) > 30:
            print(f"  ... e mais {len(missing) - 30} arquivos.")
        print()

if __name__ == '__main__':
    main()
