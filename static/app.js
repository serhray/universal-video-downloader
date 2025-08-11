// Universal Video Downloader Web App - Frontend JavaScript
class VideoDownloaderApp {
    constructor() {
        // FORÇAR MODO HTTP - SEM SOCKETIO (backend limpo)
        this.isVercel = true; // Forçar modo HTTP sempre
        this.socket = null; // Nunca usar SocketIO
        
        console.log(' Modo HTTP forçado - SocketIO desabilitado');
        
        this.currentDownloadId = null;
        this.selectedTweet = null;
        this.tweets = [];
        this.downloadFiles = [];
        this.initializeElements();
        this.bindEvents();
        
        // Apply default theme
        this.applyPlatformTheme('Instagram');
        
        this.log(' Aplicação web carregada');
        this.log(' Plataformas: Instagram, Facebook, TikTok, X/Twitter');
        this.log(' Modo HTTP: usando endpoints REST');
        this.log(' Sistema de temas ativado');
        this.log(' Selecione uma plataforma e cole a URL para começar');
    }
    
    initializeElements() {
        // Platform elements
        this.platformSelect = document.getElementById('platformSelect');
        this.platformIndicator = document.getElementById('platformIndicator');
        
        // Interface elements
        this.standardInterface = document.getElementById('standardInterface');
        this.xTwitterInterface = document.getElementById('xTwitterInterface');
        
        // Standard interface elements
        this.videoUrl = document.getElementById('videoUrl');
        this.validateBtn = document.getElementById('validateBtn');
        this.optionsCard = document.getElementById('optionsCard');
        this.qualitySelect = document.getElementById('qualitySelect');
        this.formatSelect = document.getElementById('formatSelect');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.infoBtn = document.getElementById('infoBtn');
        
        // X/Twitter interface elements
        this.xTwitterUsername = document.getElementById('xTwitterUsername');
        this.tweetCount = document.getElementById('tweetCount');
        this.searchTweetsBtn = document.getElementById('searchTweetsBtn');
        this.tweetsListCard = document.getElementById('tweetsListCard');
        this.tweetsList = document.getElementById('tweetsList');
        
        // Twitch interface elements
        this.twitchUsername = document.getElementById('twitchUsername');
        this.vodCount = document.getElementById('vodCount');
        this.searchVodsBtn = document.getElementById('searchVodsBtn');
        this.vodsListCard = document.getElementById('vodsListCard');
        this.vodsList = document.getElementById('vodsList');
        this.startTime = document.getElementById('startTime');
        this.endTime = document.getElementById('endTime');
        this.downloadSegmentBtn = document.getElementById('downloadSegmentBtn');
        
        // Progress elements
        this.progressCard = document.getElementById('progressCard');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.downloadFileBtn = document.getElementById('downloadFileBtn');
        
        // Info elements
        this.videoInfoCard = document.getElementById('videoInfoCard');
        this.videoInfoContent = document.getElementById('videoInfoContent');
        
        // CORREÇÃO: Verificar se elementos essenciais existem
        const essentialElements = [
            'platformSelect', 'downloadBtn', 'infoBtn', 'videoUrl'
        ];
        
        for (const elementName of essentialElements) {
            if (!this[elementName]) {
                console.error(`[ERROR] Elemento essencial não encontrado: ${elementName}`);
                console.error(`[ERROR] Verifique se o elemento com ID '${elementName}' existe no HTML`);
            } else {
                console.log(`[DEBUG] Elemento encontrado: ${elementName}`);
            }
        }
    }
    
    bindEvents() {
        // Platform selection
        if (this.platformSelect) {
            this.platformSelect.addEventListener('change', () => this.onPlatformChange());
        }
        
        // Standard interface events
        if (this.validateBtn) {
            this.validateBtn.addEventListener('click', () => this.validateUrl());
        }
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => this.downloadVideo());
        }
        if (this.infoBtn) {
            this.infoBtn.addEventListener('click', () => this.getVideoInfo());
        }
        
        // X/Twitter interface events
        if (this.searchTweetsBtn) {
            this.searchTweetsBtn.addEventListener('click', () => this.searchTweets());
        }
        if (this.downloadSegmentBtn) {
            this.downloadSegmentBtn.addEventListener('click', () => this.downloadSegment());
        }
        
        // Progress events
        if (this.downloadFileBtn) {
            this.downloadFileBtn.addEventListener('click', () => this.downloadFile());
        }
        
        // Enter key support
        if (this.videoUrl) {
            this.videoUrl.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.validateUrl();
            });
        }
        
        // Hide video info when URL is cleared
        if (this.videoUrl) {
            this.videoUrl.addEventListener('input', (e) => {
                if (e.target.value.trim() === '') {
                    this.hideVideoInfo();
                }
            });
        }
        
        if (this.xTwitterUsername) {
            this.xTwitterUsername.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.searchTweets();
            });
        }
    }
    
    onPlatformChange() {
        const platform = this.platformSelect.value;
        this.log(` Plataforma selecionada: ${platform}`);
        
        // Apply platform theme to body
        this.applyPlatformTheme(platform);
        
        // Update platform indicator
        const indicators = {
            'Instagram': {
                text: 'Instagram: Download no formato original',
                class: 'platform-instagram',
                emoji: ''
            },
            'Facebook': {
                text: 'Facebook: Download no formato original',
                class: 'platform-facebook',
                emoji: ''
            },
            'TikTok': {
                text: 'TikTok (requer login): Download no formato original',
                class: 'platform-tiktok',
                emoji: ''
            },
            'X/Twitter': {
                text: 'X/Twitter: Download no formato original',
                class: 'platform-twitter',
                emoji: ''
            }
        };
        
        const indicator = indicators[platform];
        this.platformIndicator.textContent = `${indicator.emoji} ${indicator.text}`;
        this.platformIndicator.className = `platform-indicator ${indicator.class}`;
        
        // CORREÇÃO: Todas as plataformas usam a interface padrão
        // Remover lógica de interface especial para X/Twitter
        this.showStandardInterface();
        
        // Update options visibility
        this.updateOptionsVisibility(platform);
        
        // Log platform theme change
        this.log(` Tema ${platform} aplicado`);
    }
    
    applyPlatformTheme(platform) {
        // Remove all existing theme classes
        document.body.classList.remove(
            'theme-instagram', 
            'theme-facebook',
            'theme-tiktok',
            'theme-twitter'
        );
        
        // Apply new theme class
        const themeClass = `theme-${platform.toLowerCase()}`;
        document.body.classList.add(themeClass);
        
        // Update page title with platform emoji
        const platformEmojis = {
            'Instagram': '',
            'Facebook': '',
            'TikTok': '',
            'X/Twitter': ''
        };
        
        const emoji = platformEmojis[platform] || '';
        document.title = `${emoji} Universal Video Downloader - ${platform}`;
        
        // Add subtle animation effect
        document.body.style.animation = 'themeTransition 0.5s ease-out';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 500);
    }
    
    showStandardInterface() {
        this.standardInterface.style.display = 'block';
        this.xTwitterInterface.style.display = 'none';
        this.log(' Interface padrão ativada');
    }
    
    showXTwitterInterface() {
        this.standardInterface.style.display = 'none';
        this.xTwitterInterface.style.display = 'block';
        this.log(' Interface X/Twitter ativada');
    }
    
    updateOptionsVisibility(platform) {
        if (platform === 'Instagram') {
            this.optionsCard.style.display = 'block';
        } else {
            this.optionsCard.style.display = 'none';
        }
    }
    
    async validateUrl() {
        const url = this.videoUrl.value.trim();
        const platform = this.platformSelect.value;
        
        if (!url) {
            this.showAlert('Por favor, digite uma URL', 'warning');
            return;
        }
        
        // Validação simples por URL (sem endpoint backend)
        const platformPatterns = {
            'Instagram': /instagram\.com/i,
            'Facebook': /(facebook\.com|fb\.watch)/i,
            'TikTok': /tiktok\.com/i,
            'X/Twitter': /(twitter\.com|x\.com)/i
        };
        
        const pattern = platformPatterns[platform];
        if (pattern && pattern.test(url)) {
            this.log(` URL ${platform} válida`);
            this.showAlert(`URL ${platform} válida`, 'success');
        } else {
            this.log(` URL não é válida para ${platform}`);
            this.showAlert(`URL não é válida para ${platform}`, 'danger');
        }
    }

    async getVideoInfo() {
        const url = this.videoUrl.value.trim();
        const platform = this.platformSelect.value;
        
        if (!url) {
            this.showAlert('Por favor, digite uma URL', 'warning');
            return;
        }
        
        this.setButtonLoading(this.infoBtn, true);
        this.log(` Buscando informações reais do vídeo ${platform}...`);
        
        try {
            // Chamar endpoint real do backend com yt-dlp
            const response = await fetch('/api/get_video_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    platform: platform
                })
            });
            
            // CORREÇÃO: Verificar se resposta é JSON válido
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error(`${platform} retornou erro do servidor (HTML em vez de JSON)`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Exibir informações reais do vídeo
                this.displayRealVideoInfo(result);
                this.log(` Informações reais obtidas: ${result.title}`);
            } else {
                this.log(` Erro ao obter informações: ${result.error}`);
                this.showAlert(`Erro: ${result.error}`, 'danger');
            }
        } catch (error) {
            this.log(` Erro de conexão: ${error.message}`);
            this.showAlert(`Erro de conexão: ${error.message}`, 'danger');
        } finally {
            this.setButtonLoading(this.infoBtn, false);
        }
    }
    
    displayRealVideoInfo(info) {
        // Mostrar card de informações reais do vídeo
        this.videoInfoCard.style.display = 'block';
        
        // Formatar duração
        const duration = info.duration ? this.formatDuration(info.duration) : 'N/A';
        
        this.videoInfoContent.innerHTML = `
            <div class="row">
                <div class="col-md-4 mb-3">
                    <img src="${info.thumbnail || 'https://via.placeholder.com/320x180/333/fff?text=' + info.platform + '+Video'}" 
                         class="img-fluid rounded shadow-sm" alt="Thumbnail">
                </div>
                <div class="col-md-8">
                    <h5 class="text-light mb-3">${info.title || 'Título não disponível'}</h5>
                    
                    <div class="row">
                        <div class="col-sm-4"><strong class="text-light">Plataforma:</strong></div>
                        <div class="col-sm-8"><span class="badge bg-primary fs-6">${info.platform || 'N/A'}</span></div>
                    </div>
                    
                    <div class="row">
                        <div class="col-sm-4"><strong class="text-light">Duração:</strong></div>
                        <div class="col-sm-8"><span class="text-warning fw-bold fs-5">${duration}</span></div>
                    </div>
                </div>
            </div>
        `;
        
        this.log(` Informações reais exibidas: ${info.title}`);
    }
    
    getPlatformIcon(platform) {
        const icons = {
            'Instagram': '',
            'Facebook': '',
            'TikTok': '',
            'X/Twitter': ''
        };
        return icons[platform] || '';
    }
    
    formatDuration(seconds) {
        // Converter para inteiro para evitar casas decimais
        const totalSeconds = Math.floor(seconds);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const secs = totalSeconds % 60;
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }
    
    formatViews(count) {
        if (count >= 1000000) {
            return (count / 1000000).toFixed(1) + 'M visualizações';
        } else if (count >= 1000) {
            return (count / 1000).toFixed(1) + 'K visualizações';
        } else {
            return count + ' visualizações';
        }
    }
    
    async downloadVideo() {
        const url = this.videoUrl.value.trim();
        const platform = this.platformSelect.value;
        const quality = this.qualitySelect.value;
        const format = this.formatSelect.value;
        
        if (!url) {
            this.showAlert('Por favor, digite uma URL', 'warning');
            return;
        }
        
        // NOVA LÓGICA: Se for Twitter ou Instagram, usar download direto ultra-simples
        if (platform === 'X/Twitter' || platform === 'Instagram') {
            console.log(`[DEBUG] Usando download direto para ${platform}`);
            await this.downloadDirect(platform);
            return;
        }
        
        // Lógica original para outras plataformas (Facebook, TikTok)
        this.setButtonLoading(this.downloadBtn, true);
        this.progressCard.style.display = 'block';
        this.updateProgress(0, 'starting');
        
        try {
            // Mostrar progresso simulado no Vercel
            if (this.isVercel) {
                this.log(' Processando download no servidor...');
                this.updateProgress(50, 'processing');
            }
            
            const response = await fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, platform, quality, format })
            });
            
            // CORREÇÃO: Verificar se resposta é JSON válido
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error(`${platform} retornou erro do servidor (HTML em vez de JSON)`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.currentDownloadId = data.download_id;
                this.downloadFiles = data.files; // Armazenar arquivos para download
                
                this.log(` ${data.message}`);
                this.log(` Plataforma: ${platform}`);
                if (platform === 'Instagram') {
                    this.log(` Qualidade: ${quality}`);
                    this.log(` Formato: ${format}`);
                }
                
                // AGUARDAR o download terminar usando polling
                this.log(' Aguardando download terminar...');
                this.updateProgress(25, 'processing');
                await this.waitForDownloadComplete(data.download_id);
                
                // Atualizar progresso para todos os ambientes (local e Vercel)
                this.log(' Download concluído com sucesso!');
                this.updateProgress(100, 'completed');
                this.downloadFileBtn.style.display = 'block';
                
                // Mostrar informações dos arquivos
                if (data.files && data.files.length > 0) {
                    data.files.forEach(file => {
                        this.log(` Arquivo: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
                    });
                }
            } else {
                // Melhorar tratamento de erro para evitar "undefined"
                const errorMessage = data.message || data.error || 'Erro desconhecido no download';
                this.log(` ${errorMessage}`);
                this.showAlert(errorMessage, 'danger');
                this.progressCard.style.display = 'none';
            }
        } catch (error) {
            // Melhorar tratamento de erro de rede/parsing
            const errorMessage = error.message || 'Erro de conexão ou resposta inválida';
            this.log(` Erro no download: ${errorMessage}`);
            this.showAlert(`Erro no download: ${errorMessage}`, 'danger');
            this.progressCard.style.display = 'none';
        } finally {
            this.setButtonLoading(this.downloadBtn, false);
        }
    }
    
    async searchTweets() {
        // X/Twitter search não implementado no backend atual
        this.showAlert('Funcionalidade X/Twitter em desenvolvimento. Use a interface padrão para URLs diretas.', 'info');
        this.log(' X/Twitter search não implementado - use interface padrão');
    }

    displayTweets(tweets) {
        // Função mantida para compatibilidade, mas não usada
        this.log(' displayTweets não implementado');
    }

    selectTweet(index) {
        // Função mantida para compatibilidade, mas não usada
        this.log(' selectTweet não implementado');
    }

    async downloadSegment() {
        // X/Twitter segment download não implementado no backend atual
        this.showAlert('Funcionalidade X/Twitter em desenvolvimento. Use a interface padrão para URLs diretas.', 'info');
        this.log(' X/Twitter segment download não implementado - use interface padrão');
    }

    downloadFile() {
        console.log('[DEBUG] Botão "Baixar Arquivo" clicado!');
        console.log('[DEBUG] currentDownloadId:', this.currentDownloadId);
        
        if (this.currentDownloadId) {
            // Usar endpoint correto /file/ com o download_id
            const downloadUrl = `/file/${this.currentDownloadId}`;
            console.log('[DEBUG] URL de download:', downloadUrl);
            
            this.log(` Tentando baixar arquivo: ${downloadUrl}`);
            
            // Tentar abrir em nova aba
            const newWindow = window.open(downloadUrl, '_blank');
            
            if (newWindow) {
                this.log(` Nova aba aberta para download: ${downloadUrl}`);
            } else {
                this.log(` Falha ao abrir nova aba - popup bloqueado?`);
                // Fallback: tentar download direto
                window.location.href = downloadUrl;
            }
        } else {
            console.log('[DEBUG] Erro: currentDownloadId é null/undefined');
            this.log(' Erro: Nenhum download_id disponível');
            this.showAlert('Erro: Nenhum arquivo disponível para download', 'danger');
        }
    }
    
    async waitForDownloadComplete(downloadId) {
        const interval = 2000; // 2 segundos
        const timeout = 300000; // 5 minutos
        
        const startTime = Date.now();
        
        while (true) {
            const response = await fetch(`/status/${downloadId}`);
            const data = await response.json();
            
            if (data.status === 'completed') {
                break;
            } else if (data.status === 'error') {
                this.log(` Erro no download: ${data.error}`);
                this.showAlert(`Erro no download: ${data.error}`, 'danger');
                this.progressCard.style.display = 'none';
                return;
            }
            
            const elapsed = Date.now() - startTime;
            if (elapsed > timeout) {
                this.log(' Tempo limite excedido. Cancelando download...');
                this.showAlert('Tempo limite excedido. Cancelando download...', 'danger');
                this.progressCard.style.display = 'none';
                return;
            }
            
            await new Promise(resolve => setTimeout(resolve, interval));
        }
    }
    
    updateProgress(percentage, status) {
        const roundedPercentage = Math.round(percentage);
        this.progressBar.style.width = `${roundedPercentage}%`;
        this.progressText.textContent = `${roundedPercentage}%`;
        
        if (status === 'completed') {
            this.progressBar.classList.remove('bg-primary');
            this.progressBar.classList.add('bg-success');
        } else if (status === 'error') {
            this.progressBar.classList.remove('bg-primary');
            this.progressBar.classList.add('bg-danger');
        }
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.setAttribute('data-original-text', originalText);
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Carregando...';
        } else {
            button.disabled = false;
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.innerHTML = originalText;
            }
        }
    }
    
    showAlert(message, type) {
        // Create alert element with platform-specific styling
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show platform-alert`;
        
        // Add platform-specific icon
        const currentPlatform = this.platformSelect.value;
        const platformIcons = {
            'Instagram': '',
            'Facebook': '',
            'TikTok': '',
            'X/Twitter': ''
        };
        
        const icon = platformIcons[currentPlatform] || '';
        
        alertDiv.innerHTML = `
            <strong>${icon} ${currentPlatform}:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of main container
        const mainContainer = document.querySelector('.main-container');
        mainContainer.insertBefore(alertDiv, mainContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        
        logEntry.className = 'text-light';
        logEntry.innerHTML = `[${timestamp}] ${message}`;
        
        // this.logContainer.appendChild(logEntry);
        
        // Auto-scroll to bottom
        // this.logContainer.scrollTop = this.logContainer.scrollHeight;
        
        // Keep only last 100 log entries
        // while (this.logContainer.children.length > 100) {
        //     this.logContainer.removeChild(this.logContainer.firstChild);
        // }
    }
    
    hideVideoInfo() {
        this.videoInfoCard.style.display = 'none';
    }
    
    async downloadDirect(platform) {
        const url = this.videoUrl.value.trim();
        
        if (!url) {
            this.showAlert('Por favor, digite uma URL', 'warning');
            return;
        }
        
        console.log('[DEBUG] Download direto iniciado');
        this.setButtonLoading(this.downloadBtn, true);
        this.log(` Iniciando download direto do ${platform}...`);
        
        try {
            // Fazer requisição POST para o endpoint correto
            const response = await fetch('/download_direct', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    url: url,
                    platform: platform 
                })
            });
            
            console.log('[DEBUG] Response status:', response.status);
            console.log('[DEBUG] Response headers:', response.headers);
            
            if (response.ok) {
                // Se a resposta for um arquivo, fazer download direto
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('video/')) {
                    const blob = await response.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = downloadUrl;
                    a.download = `${platform}_video_${Date.now()}.mp4`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(downloadUrl);
                    
                    this.log(` Download concluído com sucesso!`);
                    this.showAlert('Download concluído!', 'success');
                } else {
                    // Se for JSON, verificar resultado
                    const data = await response.json();
                    if (data.success) {
                        this.log(` Download preparado: ${data.message || 'Sucesso'}`);
                        this.showAlert('Download iniciado!', 'success');
                    } else {
                        // Tratamento específico para bloqueio do Instagram no cloud
                        if (data.error_type === 'instagram_cloud_blocked') {
                            this.log(` Instagram bloqueado no ambiente cloud`);
                            this.log(` Dica: ${data.suggestion}`);
                            this.showAlert(` Instagram Cloud: ${data.error}`, 'warning');
                            
                            // Mostrar dica adicional
                            setTimeout(() => {
                                this.showAlert(' Dica: Instagram funciona perfeitamente no ambiente local devido às limitações de rate limiting em datacenters.', 'info');
                            }, 3000);
                        } else {
                            this.log(` Erro: ${data.error}`);
                            this.showAlert(`Erro: ${data.error}`, 'danger');
                        }
                    }
                }
            } else {
                const errorText = await response.text();
                console.log('[DEBUG] Error response:', errorText);
                this.log(` Erro HTTP ${response.status}: ${errorText}`);
                this.showAlert(`Erro HTTP ${response.status}`, 'danger');
            }
            
        } catch (error) {
            console.log('[DEBUG] Erro no download direto:', error);
            this.log(` Erro no download direto: ${error.message}`);
            this.showAlert(`Erro: ${error.message}`, 'danger');
        } finally {
            this.setButtonLoading(this.downloadBtn, false);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new VideoDownloaderApp();
});
