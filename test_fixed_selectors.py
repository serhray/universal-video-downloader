import yt_dlp
import tempfile
import os

# Teste dos seletores corrigidos
test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
temp_dir = tempfile.mkdtemp()

print("🔧 TESTANDO SELETORES CORRIGIDOS")
print(f"URL: {test_url}")

# Testar os novos seletores
selectors_fixed = [
    ('bestvideo+bestaudio/best', 'Melhor vídeo + áudio (corrigido)'),
    ('bestvideo[height<=1080]+bestaudio/best[height<=1080]', '1080p corrigido'),
    ('bestvideo[height<=720]+bestaudio/best[height<=720]', '720p corrigido'),
    ('bestvideo[height<=480]+bestaudio/best[height<=480]', '480p corrigido'),
]

for selector, description in selectors_fixed:
    print(f"\n🧪 Testando: {description}")
    print(f"   Seletor: {selector}")
    
    test_opts = {
        'outtmpl': os.path.join(temp_dir, f'test_%(title)s.%(ext)s'),
        'format': selector,
        'quiet': True,
        'simulate': True,  # Apenas simular
    }
    
    try:
        with yt_dlp.YoutubeDL(test_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            selected_format = info.get('format_id', 'N/A')
            resolution = info.get('resolution', 'N/A')
            ext = info.get('ext', 'N/A')
            width = info.get('width', 'N/A')
            height = info.get('height', 'N/A')
            
            print(f"   ✅ Formato: {selected_format}")
            print(f"   📺 Resolução: {resolution} ({width}x{height})")
            print(f"   📁 Extensão: {ext}")
            
            # Verificar se conseguiu qualidade HD
            if height != 'N/A' and int(height) >= 720:
                print(f"   🎯 SUCESSO: Qualidade HD detectada!")
            elif height != 'N/A' and int(height) == 360:
                print(f"   ⚠️ AINDA 360p: Seletor pode precisar ajuste")
            else:
                print(f"   ❓ Qualidade: {height}p")
                
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n🏁 Teste concluído")
print("\nSe os seletores mostrarem qualidades HD (>=720p), a correção funcionou!")
print("Se ainda mostrarem 360p, precisamos ajustar mais os seletores.")
