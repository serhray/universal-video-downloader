#!/usr/bin/env python3
"""
Teste específico para investigar thumbnails do Instagram
"""

import yt_dlp
import json

def test_instagram_thumbnail():
    """Testar extração de thumbnail do Instagram"""
    
    # URL de teste do Instagram (post público)
    test_url = "https://www.instagram.com/p/C2example/"  # Substitua por uma URL real
    
    print("🔍 TESTANDO THUMBNAIL DO INSTAGRAM")
    print(f"URL: {test_url}")
    
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\n--- Extraindo informações ---")
            info = ydl.extract_info(test_url, download=False)
            
            print(f"\n📋 INFORMAÇÕES EXTRAÍDAS:")
            print(f"Título: {info.get('title', 'N/A')}")
            print(f"Uploader: {info.get('uploader', 'N/A')}")
            print(f"Duração: {info.get('duration', 'N/A')}")
            
            # Investigar thumbnails
            thumbnail = info.get('thumbnail')
            print(f"\n🖼️ THUMBNAIL PRINCIPAL:")
            print(f"URL: {thumbnail}")
            print(f"Tipo: {type(thumbnail)}")
            
            # Verificar se há múltiplas thumbnails
            thumbnails = info.get('thumbnails', [])
            print(f"\n📸 LISTA DE THUMBNAILS ({len(thumbnails)} encontradas):")
            
            for i, thumb in enumerate(thumbnails):
                print(f"{i+1}. URL: {thumb.get('url', 'N/A')}")
                print(f"   ID: {thumb.get('id', 'N/A')}")
                print(f"   Width: {thumb.get('width', 'N/A')}")
                print(f"   Height: {thumb.get('height', 'N/A')}")
                print(f"   Preference: {thumb.get('preference', 'N/A')}")
                print()
            
            # Verificar se é carrossel (múltiplas entradas)
            entries = info.get('entries', [])
            if entries:
                print(f"\n🎠 CARROSSEL DETECTADO ({len(entries)} itens):")
                for i, entry in enumerate(entries):
                    entry_thumb = entry.get('thumbnail')
                    print(f"{i+1}. Thumbnail: {entry_thumb}")
                    print(f"   Título: {entry.get('title', 'N/A')}")
                    print(f"   Tipo: {entry.get('_type', 'N/A')}")
                    print()
            
            # Salvar informações completas para análise
            with open('instagram_debug.json', 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2, ensure_ascii=False, default=str)
            
            print("📄 Informações completas salvas em 'instagram_debug.json'")
            
            # Verificar qual thumbnail usar
            best_thumbnail = None
            if thumbnails:
                # Priorizar thumbnail com maior preferência ou resolução
                best_thumbnail = max(thumbnails, key=lambda x: (
                    x.get('preference', 0),
                    x.get('width', 0) * x.get('height', 0)
                ))
                print(f"\n✅ MELHOR THUMBNAIL SELECIONADA:")
                print(f"URL: {best_thumbnail.get('url')}")
                print(f"Resolução: {best_thumbnail.get('width')}x{best_thumbnail.get('height')}")
            
            return best_thumbnail
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None

def test_instagram_downloader():
    """Testar o downloader do Instagram diretamente"""
    
    from instagram_downloader import InstagramDownloader
    
    print("\n" + "="*50)
    print("🧪 TESTANDO INSTAGRAM DOWNLOADER")
    
    downloader = InstagramDownloader()
    test_url = "https://www.instagram.com/p/C2example/"  # Substitua por uma URL real
    
    try:
        info = downloader.get_video_info(test_url)
        
        if info:
            print(f"✅ Informações obtidas:")
            print(f"Título: {info.get('title')}")
            print(f"Uploader: {info.get('uploader')}")
            print(f"Thumbnail: {info.get('thumbnail')}")
            
            # Verificar se thumbnail está vazia ou inválida
            thumbnail = info.get('thumbnail')
            if not thumbnail:
                print("⚠️ PROBLEMA: Thumbnail vazia!")
            elif not thumbnail.startswith('http'):
                print(f"⚠️ PROBLEMA: Thumbnail inválida: {thumbnail}")
            else:
                print("✅ Thumbnail parece válida")
                
        else:
            print("❌ Não foi possível obter informações")
            
    except Exception as e:
        print(f"❌ Erro no downloader: {e}")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE THUMBNAIL DO INSTAGRAM")
    print("=" * 50)
    
    print("⚠️ IMPORTANTE: Substitua a URL de teste por uma URL real do Instagram")
    print("Exemplo: https://www.instagram.com/p/CODIGO_DO_POST/")
    print()
    
    # Executar testes
    test_instagram_thumbnail()
    test_instagram_downloader()
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNÓSTICO CONCLUÍDO")
    print("Verifique o arquivo 'instagram_debug.json' para análise detalhada")
