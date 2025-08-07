@echo off
echo ========================================
echo  Universal Video Downloader
echo ========================================
echo.

echo Iniciando aplicativo...
python main.py

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao executar o aplicativo.
    echo.
    echo Possiveis solucoes:
    echo 1. Execute install.bat para instalar dependencias
    echo 2. Verifique se o Python esta instalado
    echo 3. Execute: pip install -r requirements.txt
    echo.
    pause
)
