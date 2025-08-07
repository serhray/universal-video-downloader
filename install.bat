@echo off
echo ========================================
echo  Universal Video Downloader - Instalacao
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.8 ou superior.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Atualizando pip...
python -m pip install --upgrade pip

echo.
echo Instalando dependencias...
python -m pip install -r requirements.txt

echo.
echo Verificando instalacao...
python -c "import yt_dlp; import customtkinter; print('Todas as dependencias instaladas com sucesso!')"

if errorlevel 1 (
    echo.
    echo ERRO: Falha na instalacao de algumas dependencias.
    echo Tente executar manualmente: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Instalacao concluida com sucesso!
echo ========================================
echo.
echo Para executar o aplicativo, use:
echo python main.py
echo.
pause
