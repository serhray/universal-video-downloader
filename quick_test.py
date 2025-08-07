import yt_dlp
import tempfile
import os
from pathlib import Path

# Teste ultra-simples
test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
temp_dir = tempfile.mkdtemp()

print(f"🔍 Testando download YouTube")
print(f"URL: {test_url}")
print(f"Diretório: {temp_dir}")

# PRIMEIRO: Investigar formatos disponíveis
print("\n=== INVESTIGANDO FORMATOS DISPONÍVEIS ===")

try:
    # Configuração para obter informações
    info_opts = {
        'quiet': False,
        'no_warnings': False,
    }
    
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        print("Obtendo informações do vídeo...")
        info = ydl.extract_info(test_url, download=False)
        
        print(f"Título: {info.get('title', 'N/A')}")
        print(f"Duração: {info.get('duration', 'N/A')} segundos")
        print(f"Uploader: {info.get('uploader', 'N/A')}")
        
        # Analisar formatos disponíveis
        formats = info.get('formats', [])
        print(f"\n📊 TOTAL DE FORMATOS DISPONÍVEIS: {len(formats)}")
        
        if len(formats) == 0:
            print("❌ PROBLEMA: Nenhum formato disponível!")
        elif len(formats) == 1:
            print("⚠️ PROBLEMA: Apenas 1 formato disponível!")
        else:
            print("✅ Múltiplos formatos disponíveis")
        
        # Mostrar todos os formatos
        print("\n� LISTA COMPLETA DE FORMATOS:")
        video_formats = []
        audio_formats = []
        
        for i, fmt in enumerate(formats):
            format_id = fmt.get('format_id', 'N/A')
            ext = fmt.get('ext', 'N/A')
            resolution = fmt.get('resolution', 'N/A')
            height = fmt.get('height', 'N/A')
            vcodec = fmt.get('vcodec', 'N/A')
            acodec = fmt.get('acodec', 'N/A')
            filesize = fmt.get('filesize', 'N/A')
            
            print(f"{i+1:2d}. ID: {format_id:8s} | Ext: {ext:4s} | Res: {resolution:10s} | "
                  f"Height: {height:4s} | VCodec: {vcodec:12s} | ACodec: {acodec:12s}")
            
            # Categorizar formatos
            if vcodec != 'none' and vcodec != 'N/A':
                video_formats.append(fmt)
            if acodec != 'none' and acodec != 'N/A':
                audio_formats.append(fmt)
        
        print(f"\n📹 Formatos de vídeo: {len(video_formats)}")
        print(f"🔊 Formatos de áudio: {len(audio_formats)}")
        
        # Verificar se há formatos de alta qualidade
        high_quality = [f for f in video_formats if f.get('height', 0) >= 720]
        print(f"🎯 Formatos HD (>=720p): {len(high_quality)}")
        
        if len(high_quality) == 0:
            print("❌ PROBLEMA: Nenhum formato HD disponível!")
            print("   Possíveis causas:")
            print("   - Restrições regionais do YouTube")
            print("   - Limitações de rede/proxy")
            print("   - Vídeo não tem qualidade HD")
            print("   - yt-dlp precisa de atualização")

except Exception as e:
    print(f"❌ Erro ao obter informações: {e}")

# SEGUNDO: Testar download com diferentes seletores
print("\n=== TESTANDO DIFERENTES SELETORES ===")

selectors_to_test = [
    ('best', 'Melhor qualidade disponível'),
    ('best[height<=1080]', 'Melhor até 1080p'),
    ('best[height<=720]', 'Melhor até 720p'),
    ('worst', 'Pior qualidade'),
    ('bestvideo+bestaudio', 'Melhor vídeo + melhor áudio'),
    ('bestvideo[height<=1080]+bestaudio', 'Vídeo 1080p + áudio'),
]

for selector, description in selectors_to_test:
    print(f"\n🧪 Testando: {selector} ({description})")
    
    test_opts = {
        'outtmpl': os.path.join(temp_dir, f'test_{selector.replace("[", "_").replace("]", "_").replace("+", "_")}_%(title)s.%(ext)s'),
        'format': selector,
        'quiet': True,
        'simulate': True,  # Não baixar, apenas simular
    }
    
    try:
        with yt_dlp.YoutubeDL(test_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            selected_format = info.get('format_id', 'N/A')
            resolution = info.get('resolution', 'N/A')
            ext = info.get('ext', 'N/A')
            
            print(f"   ✅ Selecionado: {selected_format} | {resolution} | {ext}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n🏁 Diagnóstico concluído")
