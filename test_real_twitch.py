#!/usr/bin/env python3
"""
Teste com streamer real para verificar thumbnails
"""

from twitch_downloader import TwitchDownloader

def test_real_streamer():
    """Testar com um streamer real"""
    
    print("🎮 TESTE COM STREAMER REAL")
    print("=" * 30)
    
    # Streamers conhecidos e ativos (você pode substituir)
    streamers = ["pokimane", "shroud", "xqc", "summit1g"]
    
    downloader = TwitchDownloader()
    
    for streamer in streamers:
        print(f"\n🔍 Testando: {streamer}")
        
        try:
            vods = downloader.search_user_vods(streamer, max_vods=2)
            
            if vods:
                print(f"✅ {len(vods)} VODs encontrados")
                
                for i, vod in enumerate(vods, 1):
                    print(f"\n📺 VOD {i}:")
                    print(f"   Título: {vod.get('title', 'N/A')[:50]}...")
                    
                    thumbnail = vod.get('thumbnail')
                    if thumbnail:
                        print(f"   ✅ Thumbnail: {thumbnail[:80]}...")
                        break  # Encontrou thumbnail, pode parar
                    else:
                        print(f"   ❌ Sem thumbnail")
                        
                if any(vod.get('thumbnail') for vod in vods):
                    print(f"✅ {streamer} tem thumbnails!")
                    return True
                else:
                    print(f"❌ {streamer} sem thumbnails")
                    
            else:
                print(f"❌ Nenhum VOD para {streamer}")
                
        except Exception as e:
            print(f"❌ Erro com {streamer}: {e}")
    
    return False

if __name__ == "__main__":
    if test_real_streamer():
        print("\n✅ SUCESSO: Thumbnails estão sendo extraídas!")
        print("O problema pode estar no frontend.")
    else:
        print("\n❌ PROBLEMA: Nenhuma thumbnail foi extraída.")
        print("O problema está na extração do backend.")
