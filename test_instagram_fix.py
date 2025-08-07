#!/usr/bin/env python3
"""
Teste para validar correção das thumbnails do Instagram
"""

from instagram_downloader import InstagramDownloader
import requests

def test_instagram_thumbnail_fix():
    """Testar se a correção das thumbnails do Instagram funciona"""
    
    print("🔍 TESTANDO CORREÇÃO DE THUMBNAIL DO INSTAGRAM")
    print("=" * 50)
    
    # URLs de teste (substitua por URLs reais)
    test_urls = [
        "https://www.instagram.com/p/EXEMPLO1/",  # Post normal
        "https://www.instagram.com/reel/EXEMPLO2/",  # Reel
        # Adicione URLs reais do Instagram aqui para testar
    ]
    
    downloader = InstagramDownloader()
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📱 TESTE {i}: {url}")
        
        try:
            # Obter informações
            info = downloader.get_video_info(url)
            
            if info:
                print(f"✅ Informações obtidas:")
                print(f"   Título: {info.get('title', 'N/A')}")
                print(f"   Uploader: {info.get('uploader', 'N/A')}")
                
                # Verificar thumbnail
                thumbnail = info.get('thumbnail')
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
                    
            else:
                print(f"❌ Não foi possível obter informações")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")
    print("\n💡 DICAS:")
    print("1. Substitua as URLs de exemplo por URLs reais do Instagram")
    print("2. Use posts públicos para garantir acesso")
    print("3. Se ainda houver problemas, verifique:")
    print("   - Se o yt-dlp está atualizado")
    print("   - Se há restrições de rede/proxy")
    print("   - Se o Instagram mudou sua estrutura de dados")

def test_thumbnail_extraction_logic():
    """Testar a lógica de extração de thumbnail isoladamente"""
    
    print("\n🧪 TESTANDO LÓGICA DE EXTRAÇÃO")
    print("=" * 30)
    
    # Simular dados do Instagram com diferentes estruturas
    test_cases = [
        {
            'name': 'Thumbnail principal válida',
            'data': {
                'thumbnail': 'https://example.com/thumb1.jpg',
                'thumbnails': []
            }
        },
        {
            'name': 'Sem thumbnail principal, com lista',
            'data': {
                'thumbnail': None,
                'thumbnails': [
                    {'url': 'https://example.com/thumb2.jpg', 'width': 640, 'height': 640, 'preference': 1},
                    {'url': 'https://example.com/thumb3.jpg', 'width': 320, 'height': 320, 'preference': 0}
                ]
            }
        },
        {
            'name': 'Carrossel com múltiplas entradas',
            'data': {
                'thumbnail': None,
                'thumbnails': [],
                'entries': [
                    {'thumbnail': 'https://example.com/carousel1.jpg'},
                    {'thumbnail': 'https://example.com/carousel2.jpg'}
                ]
            }
        }
    ]
    
    def get_best_thumbnail(info_dict):
        """Lógica de extração (copiada do downloader)"""
        main_thumbnail = info_dict.get('thumbnail')
        if main_thumbnail and main_thumbnail.startswith('http'):
            return main_thumbnail
        
        thumbnails = info_dict.get('thumbnails', [])
        if thumbnails:
            valid_thumbnails = [
                thumb for thumb in thumbnails 
                if thumb.get('url') and thumb['url'].startswith('http')
            ]
            
            if valid_thumbnails:
                best_thumb = max(valid_thumbnails, key=lambda x: (
                    x.get('preference', 0),
                    (x.get('width', 0) or 0) * (x.get('height', 0) or 0)
                ))
                return best_thumb.get('url')
        
        entries = info_dict.get('entries', [])
        if entries:
            for entry in entries:
                entry_thumbnail = get_best_thumbnail(entry)
                if entry_thumbnail:
                    return entry_thumbnail
        
        return None
    
    for case in test_cases:
        print(f"\n📋 {case['name']}:")
        result = get_best_thumbnail(case['data'])
        print(f"   Resultado: {result}")
        print(f"   Status: {'✅ OK' if result else '❌ Falhou'}")

if __name__ == "__main__":
    test_instagram_thumbnail_fix()
    test_thumbnail_extraction_logic()
