@echo off
echo ========================================
echo    ATUALIZACAO EXTREMA DO YT-DLP
echo ========================================
echo.

echo 🔥 Atualizando yt-dlp para versao mais recente...
pip install --upgrade yt-dlp

echo.
echo 📦 Verificando versao instalada...
yt-dlp --version

echo.
echo 🧪 Testando extracao de informacoes do YouTube...
echo URL de teste: https://www.youtube.com/watch?v=dQw4w9WgXcQ
yt-dlp --dump-json "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-warnings

echo.
echo 🎯 Testando download de video curto...
yt-dlp --format "best[height<=360]" --output "test_%(title)s.%(ext)s" "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --max-downloads 1

echo.
echo ✅ Teste concluido! Verifique os resultados acima.
echo.
pause
