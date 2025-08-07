#!/usr/bin/env python3
"""
Script de teste para diagnosticar problema de downloads .mhtml no YouTube
"""

import yt_dlp
import os
import tempfile
from pathlib import Path

def test_youtube_download():
    """Teste simples para diagnosticar o problema"""
    
    # URL de teste (vídeo curto do YouTube)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - vídeo conhecido
    
    # Criar diretório temporário
    temp_dir = tempfile.mkdtemp()
    print(f"Diretório de teste: {temp_dir}")
    
    # Configurações ULTRA-BÁSICAS
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'format': 'best[height<=720]',  # Formato simples
    }
    
    print("=== TESTE 1: Configuração Ultra-Básica ===")
    print(f"URL: {test_url}")
    print(f"Formato: {ydl_opts['format']}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Primeiro, obter informações
            print("\n--- Obtendo informações do vídeo ---")
            info = ydl.extract_info(test_url, download=False)
            print(f"Título: {info.get('title', 'N/A')}")
            print(f"Duração: {info.get('duration', 'N/A')} segundos")
            
            # Mostrar formatos disponíveis
            print("\n--- Formatos disponíveis ---")
            formats = info.get('formats', [])
            for i, fmt in enumerate(formats[:10]):  # Mostrar apenas os primeiros 10
                print(f"{i+1}. ID: {fmt.get('format_id')}, "
                      f"Ext: {fmt.get('ext')}, "
                      f"Resolução: {fmt.get('height', 'N/A')}p, "
                      f"Vcodec: {fmt.get('vcodec', 'N/A')}, "
                      f"Acodec: {fmt.get('acodec', 'N/A')}")
            
            # Agora fazer o download
            print("\n--- Iniciando download ---")
            ydl.download([test_url])
            
        # Verificar arquivos baixados
        print("\n--- Arquivos baixados ---")
        files = list(Path(temp_dir).glob('*'))
        for file in files:
            print(f"Arquivo: {file.name}")
            print(f"Tamanho: {file.stat().st_size} bytes")
            print(f"Extensão: {file.suffix}")
            
            # Verificar se é .mhtml (problema)
            if file.suffix.lower() == '.mhtml':
                print("❌ PROBLEMA: Arquivo .mhtml detectado!")
                # Ler primeiras linhas para diagnóstico
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(500)
                    print("Conteúdo (primeiros 500 chars):")
                    print(content)
            else:
                print("✅ Arquivo com extensão correta")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def test_different_formats():
    """Testar diferentes seletores de formato"""
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    temp_dir = tempfile.mkdtemp()
    
    # Diferentes seletores para testar
    selectors = [
        'best',
        'worst', 
        'best[height<=720]',
        'best[ext=mp4]',
        'bestvideo+bestaudio',
        'bestvideo[height<=720]+bestaudio'
    ]
    
    print("=== TESTE 2: Diferentes Seletores ===")
    
    for i, selector in enumerate(selectors):
        print(f"\n--- Teste {i+1}: {selector} ---")
        
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, f'test_{i+1}_%(title)s.%(ext)s'),
            'format': selector,
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([test_url])
            
            # Verificar resultado
            files = list(Path(temp_dir).glob(f'test_{i+1}_*'))
            if files:
                file = files[0]
                print(f"✅ Sucesso: {file.name} ({file.suffix})")
                if file.suffix.lower() == '.mhtml':
                    print("❌ PROBLEMA: .mhtml gerado!")
            else:
                print("❌ Nenhum arquivo gerado")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE PROBLEMA .MHTML NO YOUTUBE")
    print("=" * 50)
    
    # Verificar versão do yt-dlp
    print(f"Versão yt-dlp: {yt_dlp.version.__version__}")
    
    # Executar testes
    test_youtube_download()
    test_different_formats()
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNÓSTICO CONCLUÍDO")
