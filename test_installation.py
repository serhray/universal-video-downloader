#!/usr/bin/env python3
"""
Script de teste para verificar se todas as dependências estão instaladas corretamente
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Testar importação de um módulo"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - ERRO: {e}")
        return False

def main():
    print("=" * 50)
    print("  TESTE DE INSTALAÇÃO - Universal Video Downloader")
    print("=" * 50)
    print()
    
    print(f"Python versão: {sys.version}")
    print()
    
    print("Testando dependências:")
    print("-" * 30)
    
    # Lista de dependências para testar
    dependencies = [
        ("yt_dlp", "yt-dlp"),
        ("requests", "requests"),
        ("customtkinter", "customtkinter"),
        ("PIL", "Pillow"),
        ("tkinter", "tkinter (built-in)"),
        ("threading", "threading (built-in)"),
        ("os", "os (built-in)"),
        ("pathlib", "pathlib (built-in)"),
        ("re", "re (built-in)")
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for module, display_name in dependencies:
        if test_import(module, display_name):
            success_count += 1
    
    print()
    print("-" * 30)
    print(f"Resultado: {success_count}/{total_count} dependências OK")
    
    if success_count == total_count:
        print("🎉 Todas as dependências estão instaladas!")
        print("Você pode executar o aplicativo com: python main.py")
        
        # Teste adicional - verificar se consegue importar nossos módulos
        print("\nTestando módulos do projeto:")
        try:
            from youtube_downloader import YouTubeDownloader
            print("✅ youtube_downloader.py - OK")
            
            # Teste básico da classe
            downloader = YouTubeDownloader()
            print("✅ YouTubeDownloader class - OK")
            
        except Exception as e:
            print(f"❌ Erro ao importar módulos do projeto: {e}")
            
    else:
        print("⚠️  Algumas dependências estão faltando!")
        print("Execute: pip install -r requirements.txt")
        return 1
    
    print()
    print("=" * 50)
    return 0

if __name__ == "__main__":
    exit(main())
