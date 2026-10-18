import os
import json
import re

chron_dir = 'local/media/chronology'
showcase_dir = 'local/media/showcase'

chron_files = sorted([f for f in os.listdir(chron_dir) if f.endswith('.png')]) if os.path.exists(chron_dir) else []
showcase_files = sorted([f for f in os.listdir(showcase_dir) if f.endswith('.png')]) if os.path.exists(showcase_dir) else []

html_path = 'local/media/index.html'

def parse_srt(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    cues = []
    blocks = text.strip().split('\n\n')
    for b in blocks:
        lines = [l.strip() for l in b.strip().split('\n') if l.strip()]
        if len(lines) >= 3:
            timing = lines[1]
            content = ' '.join(lines[2:])
            m = re.match(r'(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)', timing)
            if m:
                g = [int(x) for x in m.groups()]
                start = g[0]*3600 + g[1]*60 + g[2] + g[3]/1000.0
                end = g[4]*3600 + g[5]*60 + g[6] + g[7]/1000.0
                cues.append({'s': round(start, 3), 'e': round(end, 3), 't': content})
    return cues

all_subs = {}
for i in range(1, 6):
    all_subs[f'ch{i}'] = {
        'pt': parse_srt(f'local/media/movies/ch{i}.pt-BR.srt'),
        'en': parse_srt(f'local/media/movies/ch{i}.en.srt')
    }

html_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Need for Speed: Porsche Unleashed - Galeria Histórica & Vídeos</title>
  <style>
    :root {
      --bg: #090d13;
      --card: #161b22;
      --border: #30363d;
      --accent: #d29922;
      --text: #c9d1d9;
      --text-bright: #f0f6fc;
      --hover: #21262d;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      padding: 24px;
    }
    header {
      max-width: 1200px;
      margin: 0 auto 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
    }
    h1 { font-size: 24px; color: var(--text-bright); }
    .tabs {
      display: flex;
      gap: 12px;
      max-width: 1200px;
      margin: 0 auto 24px;
    }
    .tab-btn {
      background: var(--card);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 10px 20px;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      font-size: 14px;
      transition: all 0.2s ease;
    }
    .tab-btn:hover { background: var(--hover); color: var(--text-bright); }
    .tab-btn.active { background: var(--accent); color: #000; border-color: var(--accent); }
    .content-area { max-width: 1200px; margin: 0 auto; }
    .video-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 20px;
    }
    .video-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .video-wrapper {
      position: relative;
      width: 100%;
      height: 240px;
      background: #000;
    }
    .video-wrapper video {
      width: 100%;
      height: 100%;
      outline: none;
      display: block;
    }
    .sub-overlay {
      position: absolute;
      bottom: 42px;
      left: 12px;
      right: 12px;
      text-align: center;
      pointer-events: none;
      display: none;
      justify-content: center;
      align-items: center;
      z-index: 5;
    }
    .sub-overlay.active {
      display: flex;
    }
    .sub-text {
      background: rgba(0, 0, 0, 0.82);
      color: #fff;
      font-size: 13.5px;
      line-height: 1.4;
      padding: 4px 10px;
      border-radius: 4px;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
      max-width: 92%;
    }
    .video-info {
      padding: 14px;
    }
    .video-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-bright);
      margin-bottom: 4px;
    }
    .video-sub { font-size: 12px; color: #8b949e; }
    
    .sub-controls {
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid rgba(255,255,255,0.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11.5px;
      color: #8b949e;
      flex-wrap: wrap;
      gap: 6px;
    }
    .sub-lang-btn {
      background: #21262d;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 3px 8px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 11px;
      transition: all 0.15s ease;
    }
    .sub-lang-btn:hover {
      border-color: #8b949e;
    }
    .sub-lang-btn.active {
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
      font-weight: 600;
    }

    .photo-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 14px;
    }
    .photo-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      cursor: pointer;
      transition: transform 0.15s ease, border-color 0.15s ease;
      display: flex;
      flex-direction: column;
    }
    .photo-card:hover {
      transform: translateY(-3px);
      border-color: var(--accent);
    }
    .photo-card img {
      width: 100%;
      height: 150px;
      object-fit: cover;
      background: #000;
    }
    .photo-title {
      padding: 8px 10px;
      font-size: 12px;
      color: #8b949e;
      text-overflow: ellipsis;
      overflow: hidden;
      white-space: nowrap;
    }
    /* Lightbox */
    .lightbox {
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.85);
      z-index: 999;
      justify-content: center;
      align-items: center;
      flex-direction: column;
      cursor: pointer;
    }
    .lightbox img {
      max-width: 90%;
      max-height: 80vh;
      border-radius: 8px;
      border: 2px solid var(--border);
      box-shadow: 0 10px 30px rgba(0,0,0,0.8);
      cursor: default;
    }
    .lightbox-caption {
      margin-top: 14px;
      color: var(--text-bright);
      font-size: 16px;
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Porsche Unleashed (2000) - Arquivo Histórico & Multimídia</h1>
      <p style="color:#8b949e; font-size:13px; margin-top:4px;">10 Documentários Originais em Vídeo (.mp4) e __TOTAL_PHOTOS__ Fotografias de Época da Marca (.png)</p>
    </div>
  </header>

  <div class="tabs">
    <button class="tab-btn active" onclick="showTab('movies', this)">Vídeos Documentários (10)</button>
    <button class="tab-btn" onclick="showTab('chronology', this)">Cronologia Histórica (__CHRON_COUNT__ Fotos)</button>
    <button class="tab-btn" onclick="showTab('showcase', this)">Showcase dos Carros (__SHOWCASE_COUNT__ Fotos)</button>
  </div>

  <div class="content-area">
    <!-- MOVIES TAB -->
    <div id="tab-movies" class="video-grid"></div>

    <!-- CHRONOLOGY TAB -->
    <div id="tab-chronology" class="photo-grid" style="display:none;"></div>

    <!-- SHOWCASE TAB -->
    <div id="tab-showcase" class="photo-grid" style="display:none;"></div>
  </div>

  <!-- LIGHTBOX -->
  <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
    <img id="lightbox-img" src="" alt="Imagem Ampliada" onclick="event.stopPropagation()">
    <div class="lightbox-caption" id="lightbox-caption"></div>
  </div>

  <script>
    const movies = [
      { id: "ch1", file: "movies/ch1.mp4", title: "Capítulo 1: O Começo (1948 - 1954)", sub: "Origem do 356 e primeiros anos em Gmünd" },
      { id: "ch2", file: "movies/ch2.mp4", title: "Capítulo 2: A Revolução Transaxle (1975 - 1995)", sub: "A era de ouro dos 924, 944 e o auge com o 968" },
      { id: "ch3", file: "movies/ch3.mp4", title: "Capítulo 3: O Ícone 911 (1963 - 2000)", sub: "Nascimento do 911, Carrera RS 2.7, Targa e Turbo" },
      { id: "ch4", file: "movies/ch4.mp4", title: "Capítulo 4: As Raízes & Weissach (1900 - 2000)", sub: "Lohner-Porsche, Ferdinand, o Fusca e o centro de Weissach" },
      { id: "ch5", file: "movies/ch5.mp4", title: "Capítulo 5: A Glória nas Pistas (1953 - 1998)", sub: "550 Spyder, Targa Florio, o monstro 917 e 911 GT1 em Le Mans" },
      { id: "ch6", file: "movies/ch6.mp4", title: "Capítulo 6: O Novo Milênio (1994 - 2000)", sub: "Clipe cinematográfico de celebração da marca Porsche" },
      { id: "er1", file: "movies/er1pc-av.mp4", title: "Introdução: Era Clássica", sub: "Vídeo de abertura do modo Evolution Clássico" },
      { id: "er2", file: "movies/er2pc-av.mp4", title: "Introdução: Era Dourada", sub: "Vídeo de abertura do modo Evolution Dourado" },
      { id: "er3", file: "movies/er3pc-av.mp4", title: "Introdução: Era Moderna", sub: "Vídeo de abertura do modo Evolution Moderno" },
      { id: "er4", file: "movies/er4pc-av.mp4", title: "Evolução da Marca Porsche", sub: "Vídeo geral de transição e conquistas da marca" }
    ];

    const subtitles = __SUBTITLES_JSON__;
    const activeSubLang = {}; // videoId -> 'pt' | 'en' | 'off'

    const chronPhotos = __CHRON_DATA__;
    const showcasePhotos = __SHOWCASE_DATA__;

    function renderMovies() {
      const container = document.getElementById('tab-movies');
      container.innerHTML = movies.map((m, idx) => {
        const hasSubs = !!subtitles[m.id];
        if (hasSubs && !activeSubLang[m.id]) {
          activeSubLang[m.id] = 'pt'; // padrão: Português
        }
        return `
          <div class="video-card">
            <div class="video-wrapper">
              <video id="vid-${m.id}" controls preload="metadata" ontimeupdate="onVideoTimeUpdate('${m.id}')">
                <source src="${m.file}" type="video/mp4">
              </video>
              <div class="sub-overlay" id="overlay-${m.id}">
                <div class="sub-text" id="subtext-${m.id}"></div>
              </div>
            </div>
            <div class="video-info">
              <div class="video-title">${m.title}</div>
              <div class="video-sub">${m.sub}</div>
              ${hasSubs ? `
                <div class="sub-controls">
                  <div style="display:flex; align-items:center; gap:6px;">
                    <span>Legenda:</span>
                    <button class="sub-lang-btn active" id="btn-pt-${m.id}" onclick="setSubLang('${m.id}', 'pt')">PT-BR</button>
                    <button class="sub-lang-btn" id="btn-en-${m.id}" onclick="setSubLang('${m.id}', 'en')">EN</button>
                    <button class="sub-lang-btn" id="btn-off-${m.id}" onclick="setSubLang('${m.id}', 'off')">Desativar</button>
                  </div>
                  <div style="display:flex; gap:8px;">
                    <a href="movies/${m.id}.pt-BR.srt" download style="color:#d29922; text-decoration:none;">.srt (PT)</a>
                    <a href="movies/${m.id}.en.srt" download style="color:#58a6ff; text-decoration:none;">.srt (EN)</a>
                  </div>
                </div>
              ` : ''}
            </div>
          </div>
        `;
      }).join('');
    }

    function setSubLang(vidId, lang) {
      activeSubLang[vidId] = lang;
      ['pt', 'en', 'off'].forEach(l => {
        const btn = document.getElementById(`btn-${l}-${vidId}`);
        if (btn) btn.classList.toggle('active', l === lang);
      });
      onVideoTimeUpdate(vidId);
    }

    function onVideoTimeUpdate(vidId) {
      const vid = document.getElementById(`vid-${vidId}`);
      const overlay = document.getElementById(`overlay-${vidId}`);
      const subtext = document.getElementById(`subtext-${vidId}`);
      if (!vid || !overlay || !subtext) return;

      const lang = activeSubLang[vidId];
      if (!lang || lang === 'off' || !subtitles[vidId]) {
        overlay.classList.remove('active');
        return;
      }

      const cues = subtitles[vidId][lang];
      if (!cues) {
        overlay.classList.remove('active');
        return;
      }

      const t = vid.currentTime;
      const activeCue = cues.find(c => t >= c.s && t <= c.e);

      if (activeCue) {
        subtext.textContent = activeCue.t;
        overlay.classList.add('active');
      } else {
        overlay.classList.remove('active');
      }
    }

    function renderPhotos(tabId, folder, photos) {
      const container = document.getElementById(tabId);
      container.innerHTML = photos.map(item => `
        <div class="photo-card" onclick="openLightbox('${folder}/${item}', '${item}')">
          <img src="${folder}/${item}" loading="lazy" alt="${item}">
          <div class="photo-title">${item}</div>
        </div>
      `).join('');
    }

    function showTab(name, btnElement) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      if (btnElement) {
        btnElement.classList.add('active');
      }
      
      document.getElementById('tab-movies').style.display = name === 'movies' ? 'grid' : 'none';
      document.getElementById('tab-chronology').style.display = name === 'chronology' ? 'grid' : 'none';
      document.getElementById('tab-showcase').style.display = name === 'showcase' ? 'grid' : 'none';
    }

    function openLightbox(src, caption) {
      document.getElementById('lightbox-img').src = src;
      document.getElementById('lightbox-caption').textContent = caption;
      document.getElementById('lightbox').style.display = 'flex';
    }

    function closeLightbox(event) {
      document.getElementById('lightbox').style.display = 'none';
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.getElementById('lightbox').style.display = 'none';
      }
    });

    renderMovies();
    renderPhotos('tab-chronology', 'chronology', chronPhotos);
    renderPhotos('tab-showcase', 'showcase', showcasePhotos);
  </script>
</body>
</html>
"""

total_photos = len(chron_files) + len(showcase_files)

html_content = html_template.replace("__TOTAL_PHOTOS__", str(total_photos))
html_content = html_content.replace("__CHRON_COUNT__", str(len(chron_files)))
html_content = html_content.replace("__SHOWCASE_COUNT__", str(len(showcase_files)))
html_content = html_content.replace("__CHRON_DATA__", json.dumps(chron_files))
html_content = html_content.replace("__SHOWCASE_DATA__", json.dumps(showcase_files))
html_content = html_content.replace("__SUBTITLES_JSON__", json.dumps(all_subs))

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated {html_path} with embedded subtitle overlay engine!")
