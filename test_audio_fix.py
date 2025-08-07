import yt_dlp
import tempfile
import os

# Teste da correção de áudio
test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
temp_dir = tempfile.mkdtemp()

print("🔊 TESTANDO CORREÇÃO DE ÁUDIO MP4")
print(f"URL: {test_url}")

# Testar seletores com prioridade para áudio AAC
selectors_audio_fixed = [
    ('bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best', 'MP4 com áudio AAC prioritário'),
    ('bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio', '720p MP4 com AAC'),
    ('bestvideo+bestaudio', 'Seletor original (pode ter Opus)'),
]

for selector, description in selectors_audio_fixed:
    print(f"\n🧪 Testando: {description}")
    print(f"   Seletor: {selector}")
    
    test_opts = {
        'outtmpl': os.path.join(temp_dir, f'test_%(title)s.%(ext)s'),
        'format': selector,
        'quiet': True,
        'simulate': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(test_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
            # Informações do formato selecionado
            format_id = info.get('format_id', 'N/A')
            resolution = info.get('resolution', 'N/A')
            ext = info.get('ext', 'N/A')
            acodec = info.get('acodec', 'N/A')
            vcodec = info.get('vcodec', 'N/A')
            
            print(f"   ✅ Formato: {format_id}")
            print(f"   📺 Resolução: {resolution}")
            print(f"   📁 Extensão: {ext}")
            print(f"   🎵 Áudio Codec: {acodec}")
            print(f"   🎬 Vídeo Codec: {vcodec}")
            
            # Verificar se o áudio é compatível
            if 'aac' in acodec.lower() or 'm4a' in acodec.lower():
                print(f"   ✅ ÁUDIO COMPATÍVEL: {acodec}")
            elif 'opus' in acodec.lower():
                print(f"   ⚠️ ÁUDIO OPUS: Pode ter problemas de compatibilidade")
            else:
                print(f"   ❓ Codec desconhecido: {acodec}")
                
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n" + "="*50)
print("📋 RESUMO:")
print("✅ AAC/M4A = Áudio compatível com a maioria dos players")
print("⚠️ Opus = Pode não funcionar em alguns players/dispositivos")
print("🔧 A correção prioriza AAC para arquivos MP4")
print("\n🏁 Teste de áudio concluído")
