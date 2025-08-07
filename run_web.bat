@echo off
echo ========================================
echo   Universal Video Downloader Web App
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado!
    echo Por favor, instale Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

echo ✓ Python encontrado
echo.

REM Verificar se pip está disponível
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: pip não encontrado!
    echo Por favor, instale pip e tente novamente.
    pause
    exit /b 1
)

echo ✓ pip encontrado
echo.

REM Instalar dependências
echo 📦 Instalando dependências...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ Erro na instalação das dependências!
    echo Verifique sua conexão com a internet e tente novamente.
    pause
    exit /b 1
)

echo.
echo ✅ Dependências instaladas com sucesso!
echo.

REM Criar diretórios necessários
if not exist "static" mkdir static
if not exist "templates" mkdir templates
if not exist "downloads" mkdir downloads

echo 📁 Diretórios criados
echo.

REM Iniciar aplicação web
echo 🚀 Iniciando aplicação web...
echo.
echo ==========================================
echo   Aplicação disponível em:
echo   http://localhost:5000
echo ==========================================
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python app.py

echo.
echo 👋 Aplicação encerrada
pause
