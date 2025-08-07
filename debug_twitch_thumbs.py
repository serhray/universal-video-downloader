#!/usr/bin/env python3
"""
Debug rápido para thumbnails dos VODs da Twitch
"""

from twitch_downloader import TwitchDownloader
import json

def debug_twitch_thumbnails():
    """Debug rápido das thumbnails da Twitch"""
    
    print("🔍 DEBUG: THUMBNAILS DOS VODS DA TWITCH")
    print("=" * 45)
    
    # Use um streamer conhecido e ativo (substitua por um real)
    test_username = "ninja"  # Substitua por um streamer real
    
    print(f"🎮 Testando streamer: {test_username}")
    print("⚠️  IMPORTANTE: Substitua 'ninja' por um streamer real e ativo!")
    
    downloader = TwitchDownloader()
    
    try:
        # Buscar apenas 3 VODs para teste rápido
        print("\n🔍 Buscando VODs...")
        vods = downloader.search_user_vods(test_username, max_vods=3)
        
        if vods:
            print(f"✅ Encontrados {len(vods)} VODs")
            
            for i, vod in enumerate(vods, 1):
                print(f"\n📺 VOD {i}:")
                print(f"   Título: {vod.get('title', 'N/A')[:60]}...")
                print(f"   ID: {vod.get('id', 'N/A')}")
                print(f"   URL: {vod.get('url', 'N/A')}")
                
                # FOCO: Verificar thumbnail
                thumbnail = vod.get('thumbnail')
                print(f"   🖼️  THUMBNAIL: {thumbnail}")
                
                if thumbnail:
                    if thumbnail.startswith('http'):
                        print(f"   ✅ Thumbnail é uma URL válida")
                    else:
                        print(f"   ❌ Thumbnail não é uma URL HTTP válida")
                else:
                    print(f"   ❌ PROBLEMA: Nenhuma thumbnail encontrada!")
                
                # Mostrar dados brutos para debug
                print(f"   📊 Dados completos do VOD:")
                print(f"      {json.dumps(vod, indent=6, ensure_ascii=False)}")
                
        else:
            print(f"❌ Nenhum VOD encontrado para {test_username}")
            print("💡 Dicas:")
            print("   - Verifique se o nome do streamer está correto")
            print("   - Certifique-se de que o streamer tem VODs públicos")
            print("   - Teste com streamers conhecidos: ninja, shroud, pokimane")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        print("💡 Possíveis causas:")
        print("   - Problema de conexão")
        print("   - yt-dlp desatualizado")
        print("   - Mudanças na API da Twitch")

def test_raw_ytdlp():
    """Testar yt-dlp diretamente para ver estrutura de dados"""
    
    print("\n" + "=" * 45)
    print("🧪 TESTE DIRETO COM YT-DLP")
    print("=" * 45)
    
    import yt_dlp
    
    # URL de teste (substitua por um canal real)
    test_url = "https://www.twitch.tv/ninja/videos"  # Substitua por um streamer real
    
    print(f"🔗 Testando URL: {test_url}")
    print("⚠️  IMPORTANTE: Substitua por um canal real!")
    
    try:
        ydl_opts = {
            'quiet': False,  # Mostrar logs para debug
            'no_warnings': False,
            'extract_flat': True,
            'playlistend': 2,  # Apenas 2 VODs para teste
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\n🔍 Extraindo informações...")
            info = ydl.extract_info(test_url, download=False)
            
            if info and 'entries' in info:
                print(f"✅ Encontradas {len(info['entries'])} entradas")
                
                for i, entry in enumerate(info['entries'][:2], 1):
                    if entry:
                        print(f"\n📺 Entrada {i}:")
                        print(f"   Título: {entry.get('title', 'N/A')}")
                        print(f"   ID: {entry.get('id', 'N/A')}")
                        print(f"   Thumbnail principal: {entry.get('thumbnail', 'N/A')}")
                        
                        # Verificar lista de thumbnails
                        thumbnails = entry.get('thumbnails', [])
                        print(f"   📸 Lista de thumbnails ({len(thumbnails)} encontradas):")
                        
                        for j, thumb in enumerate(thumbnails[:3], 1):  # Mostrar apenas 3
                            print(f"      {j}. URL: {thumb.get('url', 'N/A')}")
                            print(f"         Resolução: {thumb.get('width', 'N/A')}x{thumb.get('height', 'N/A')}")
                        
                        if len(thumbnails) > 3:
                            print(f"      ... e mais {len(thumbnails) - 3} thumbnails")
                            
            else:
                print("❌ Nenhuma entrada encontrada")
                
    except Exception as e:
        print(f"❌ ERRO no yt-dlp: {e}")

if __name__ == "__main__":
    print("🎮 DEBUG RÁPIDO: THUMBNAILS DOS VODS DA TWITCH")
    print("=" * 55)
    
    debug_twitch_thumbnails()
    test_raw_ytdlp()
    
    print("\n" + "=" * 55)
    print("🏁 DEBUG CONCLUÍDO")
    print("\n📝 PRÓXIMOS PASSOS:")
    print("1. Se as thumbnails aparecem aqui mas não na web, o problema é no frontend")
    print("2. Se não aparecem aqui, o problema é na extração do yt-dlp")
    print("3. Substitua os nomes/URLs de teste por streamers reais e ativos")
