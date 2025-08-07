# Universal Video Downloader

Um aplicativo moderno e intuitivo para baixar vídeos de múltiplas plataformas, começando com o YouTube.

## 🚀 Características

- **Interface Gráfica Moderna**: Interface escura e elegante usando CustomTkinter
- **Download do YouTube**: Suporte completo para vídeos e playlists do YouTube
- **Múltiplas Qualidades**: Escolha entre diferentes qualidades (4K, 1080p, 720p, etc.)
- **Formatos Variados**: Suporte para MP4, WebM, MKV, MP3, M4A e mais
- **Barra de Progresso**: Acompanhe o progresso do download em tempo real
- **Informações do Vídeo**: Visualize detalhes do vídeo antes de baixar
- **Log de Atividades**: Histórico completo das operações

## 🎯 Plataformas Suportadas

### ✅ Implementado
- **YouTube** - Vídeos, playlists, canais

### 🔄 Em Desenvolvimento
- **Twitch** - Clips e VODs
- **Kick** - Streams e clips
- **Instagram** - Posts e stories
- **Facebook** - Vídeos públicos
- **TikTok** - Vídeos curtos

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Windows 10/11 (testado)
- Conexão com a internet

## 🛠️ Instalação

1. **Clone ou baixe o projeto**:
   ```bash
   git clone <url-do-repositorio>
   cd download-universal
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o aplicativo**:
   ```bash
   python main.py
   ```

## 📖 Como Usar

### Download Básico do YouTube

1. **Abra o aplicativo** executando `python main.py`
2. **Cole a URL** do vídeo do YouTube no campo "URL do Vídeo"
3. **Escolha a qualidade** desejada (best, 1080p, 720p, etc.)
4. **Selecione o formato** (MP4 recomendado para vídeo, MP3 para áudio)
5. **Defina a pasta de destino** ou use a padrão
6. **Clique em "Baixar Vídeo"** e aguarde a conclusão

### Obter Informações do Vídeo

- Clique em **"Info do Vídeo"** para ver detalhes como título, duração, canal e visualizações antes de baixar

### Configurações Avançadas

- **Qualidade**: 
  - `best` - Melhor qualidade disponível
  - `worst` - Menor qualidade (menor arquivo)
  - `720p`, `1080p`, etc. - Qualidade específica

- **Formatos de Vídeo**: MP4, WebM, MKV
- **Formatos de Áudio**: MP3, M4A, AAC

## 🎛️ Configurações

O arquivo `config.py` contém todas as configurações personalizáveis:

- Qualidades e formatos suportados
- Configurações de rede (timeout, tentativas)
- Configurações da interface
- Configurações específicas do YouTube

## 📁 Estrutura do Projeto

```
download-universal/
├── main.py                 # Aplicativo principal com interface gráfica
├── youtube_downloader.py   # Classe para download do YouTube
├── config.py              # Configurações do aplicativo
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## 🔧 Dependências

- **yt-dlp**: Biblioteca para download de vídeos
- **customtkinter**: Interface gráfica moderna
- **requests**: Requisições HTTP
- **Pillow**: Manipulação de imagens

## ⚠️ Avisos Importantes

- **Respeite os direitos autorais**: Use apenas para conteúdo que você tem permissão para baixar
- **Termos de serviço**: Verifique os termos de serviço das plataformas antes de usar
- **Uso responsável**: Não use para pirataria ou violação de direitos autorais

## 🐛 Solução de Problemas

### Erro de instalação do yt-dlp
```bash
pip install --upgrade yt-dlp
```

### Erro de "módulo não encontrado"
```bash
pip install -r requirements.txt --force-reinstall
```

### Vídeo não baixa
- Verifique se a URL está correta
- Teste com outro vídeo
- Verifique sua conexão com a internet

## 🚀 Próximas Funcionalidades

- [ ] Suporte para Twitch
- [ ] Suporte para Instagram
- [ ] Suporte para TikTok
- [ ] Download de playlists
- [ ] Agendamento de downloads
- [ ] Conversão automática de formatos
- [ ] Download simultâneo múltiplo

## 📝 Changelog

### v1.0.0 (Atual)
- ✅ Interface gráfica completa
- ✅ Download do YouTube
- ✅ Múltiplas qualidades e formatos
- ✅ Barra de progresso
- ✅ Informações do vídeo
- ✅ Log de atividades

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Reportar bugs
2. Sugerir novas funcionalidades
3. Enviar pull requests
4. Melhorar a documentação

## 📄 Licença

Este projeto é para uso educacional e pessoal. Respeite os direitos autorais e termos de serviço das plataformas.

---

**Desenvolvido com ❤️ para a comunidade**
