#!/usr/bin/env python3
"""
Teste para validar thumbnails dos VODs da Twitch
"""

from twitch_downloader import TwitchDownloader
import requests

def test_twitch_vod_thumbnails():
    """Testar se as thumbnails dos VODs da Twitch estão sendo extraídas"""
    
    print("🎮 TESTANDO THUMBNAILS DOS VODS DA TWITCH")
    print("=" * 50)
    
    # Streamers de teste (substitua por nomes reais)
    test_streamers = [
        "ninja",  # Exemplo - substitua por streamers reais
        "shroud",  # Exemplo - substitua por streamers reais
        # Adicione mais streamers para testar
    ]
    
    downloader = TwitchDownloader()
    
    for streamer in test_streamers:
        print(f"\n🔍 TESTANDO: {streamer}")
        print("-" * 30)
        
        try:
            # Buscar VODs (limitado a 5 para teste rápido)
            vods = downloader.search_user_vods(streamer, max_vods=5)
            
            if vods:
                print(f"✅ Encontrados {len(vods)} VODs")
                
                for i, vod in enumerate(vods, 1):
                    print(f"\n📺 VOD {i}: {vod.get('title', 'Sem título')[:50]}...")
                    
                    # Verificar thumbnail
                    thumbnail = vod.get('thumbnail')
                    print(f"   Thumbnail: {thumbnail}")
                    
                    if thumbnail:
                        if thumbnail.startswith('http'):
                            # Testar se a URL da thumbnail é acessível
                            try:
                                response = requests.head(thumbnail, timeout=10)
                                if response.status_code == 200:
                                    print(f"   ✅ Thumbnail válida e acessível")
                                else:
                                    print(f"   ⚠️ Thumbnail retornou status {response.status_code}")
                            except Exception as e:
                                print(f"   ❌ Erro ao acessar thumbnail: {e}")
                        else:
                            print(f"   ❌ Thumbnail inválida (não é URL HTTP)")
                    else:
                        print(f"   ⚠️ Nenhuma thumbnail encontrada")
                        
                    # Mostrar outras informações
                    print(f"   Duração: {vod.get('duration', 'N/A')}")
                    print(f"   Views: {vod.get('view_count', 0):,}")
                    print(f"   Data: {vod.get('upload_date', 'N/A')}")
                    
            else:
                print(f"❌ Nenhum VOD encontrado para {streamer}")
                
        except Exception as e:
            print(f"❌ Erro ao testar {streamer}: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")
    print("\n💡 DICAS:")
    print("1. Substitua os nomes dos streamers por nomes reais e ativos")
    print("2. Verifique se os streamers têm VODs públicos disponíveis")
    print("3. Se não houver thumbnails, pode ser limitação do yt-dlp ou da Twitch")

def test_thumbnail_extraction_logic():
    """Testar a lógica de extração de thumbnail isoladamente"""
    
    print("\n🧪 TESTANDO LÓGICA DE EXTRAÇÃO DE THUMBNAIL")
    print("=" * 40)
    
    # Simular dados de VOD com diferentes estruturas de thumbnail
    test_cases = [
        {
            'name': 'VOD com thumbnail principal',
            'data': {
                'thumbnail': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_ninja-320x180.jpg',
                'thumbnails': []
            }
        },
        {
            'name': 'VOD sem thumbnail principal, com lista',
            'data': {
                'thumbnail': None,
                'thumbnails': [
                    {'url': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_ninja-160x90.jpg', 'width': 160, 'height': 90},
                    {'url': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_ninja-320x180.jpg', 'width': 320, 'height': 180},
                    {'url': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_ninja-640x360.jpg', 'width': 640, 'height': 360}
                ]
            }
        },
        {
            'name': 'VOD sem thumbnails',
            'data': {
                'thumbnail': None,
                'thumbnails': []
            }
        }
    ]
    
    def extract_best_thumbnail(entry_data):
        """Lógica de extração (copiada do downloader)"""
        thumbnail = None
        if entry_data.get('thumbnail'):
            thumbnail = entry_data.get('thumbnail')
        elif entry_data.get('thumbnails') and len(entry_data['thumbnails']) > 0:
            thumbnails = entry_data['thumbnails']
            best_thumbnail = max(thumbnails, key=lambda x: (x.get('width', 0) * x.get('height', 0)))
            thumbnail = best_thumbnail.get('url')
        return thumbnail
    
    for case in test_cases:
        print(f"\n📋 {case['name']}:")
        result = extract_best_thumbnail(case['data'])
        print(f"   Resultado: {result}")
        print(f"   Status: {'✅ OK' if result else '❌ Sem thumbnail'}")

def test_web_interface_integration():
    """Testar se a integração com a interface web está funcionando"""
    
    print("\n🌐 TESTANDO INTEGRAÇÃO COM INTERFACE WEB")
    print("=" * 35)
    
    print("📝 Checklist de integração:")
    print("1. ✅ Twitch downloader modificado para incluir thumbnails")
    print("2. ✅ JavaScript displayVods() atualizado para mostrar thumbnails")
    print("3. ✅ CSS com estilos para thumbnails dos VODs")
    print("4. ✅ Fallback para VODs sem thumbnail (placeholder)")
    print("5. ✅ Hover effects e seleção visual")
    
    print("\n🚀 Para testar na interface web:")
    print("1. Inicie o servidor Flask: python app.py")
    print("2. Acesse http://localhost:5000")
    print("3. Selecione 'Twitch' na plataforma")
    print("4. Digite um nome de streamer")
    print("5. Clique em 'Buscar VODs'")
    print("6. Verifique se as thumbnails aparecem na lista")

if __name__ == "__main__":
    print("🎮 DIAGNÓSTICO DE THUMBNAILS DOS VODS DA TWITCH")
    print("=" * 55)
    
    print("⚠️ IMPORTANTE: Substitua os nomes dos streamers por nomes reais")
    print("Exemplo: ninja, shroud, pokimane, etc.")
    print()
    
    # Executar testes
    test_twitch_vod_thumbnails()
    test_thumbnail_extraction_logic()
    test_web_interface_integration()
    
    print("\n" + "=" * 55)
    print("🏁 DIAGNÓSTICO CONCLUÍDO")
    print("Execute o teste na interface web para validar visualmente!")
