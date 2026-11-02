# Internacionalização (i18n) - Sistema Multilíngue

## 🌍 Visão Geral

A aplicação agora suporta **4 idiomas** automaticamente baseados na seleção do país:

- **pt_BR** - Português (Brasil)
- **en_US** - Inglês (EUA/Portugal)
- **es_ES** - Espanhol (Espanha)
- **es_MX** - Espanhol (México/Argentina)

## 📁 Arquivos Criados

```
static/
├── index.html              # Frontend principal
├── i18n.js                 # Sistema de internacionalização
└── icon.ico                # Ícone do sistema
```

## 🔧 Como Funciona

### 1. Seleção de País → Troca de Idioma

Ao selecionar um país no dropdown, o sistema:

1. Detecta automaticamente a localidade (locale) correspondente
2. Atualiza todo o conteúdo da página para o idioma do país selecionado
3. Configura o timezone correto para a localização
4. Aplica estilos CSS específicos por idioma (se aplicável)

### 2. API de Traduções (`/api/i18n`)

Retorna um objeto JSON com todas as traduções:

```json
{
  "pt_BR": { "title": "...", "subtitle": "..." },
  "en_US": { "title": "...", "subtitle": "..." },
  "es_ES": { "title": "...", "subtitle": "..." },
  "es_MX": { "title": "...", "subtitle": "..." }
}
```

### 3. Cabeçalhos HTTP

As rotas da API retornam cabeçalhos adicionais:

- `X-Locale`: O locale atual (pt-BR, en-US, es-ES, es-MX)
- `X-Timezone`: Timezone correspondente ao país

## 🎨 Interface Minimalista

A complexidade está apenas nos "catálogos" de tradução - a interface permanece limpa:

```html
<h1 data-i18n="title"></h1>      <!-- Tradução dinâmica -->
<label data-i18n="countryLabel"></label>  <!-- Labels traduzidos -->
```

## 📦 Instalação e Execução

### Local (Desenvolvimento)

```bash
# Instalar Flask-Babel (opcional, não é usado atualmente)
pip install Flask-Babel

# Rodar na porta 8000
python app.py

# Acesse http://localhost:8000
```

### Produção (Render/Gunicorn)

```bash
gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:application
```

A porta é configurada via ambiente:
- `PORT=3000` → roda na 3000
- Sem PORT → usa 8000 por padrão

## 🌐 Testando Internacionalização

```bash
# Testar todas as localizações
curl "http://localhost:8000/api/i18n?locale=pt_BR"
curl "http://localhost:8000/api/i18n?locale=en_US"
curl "http://localhost:8000/api/i18n?locale=es_ES"
curl "http://localhost:8000/api/i18n?locale=es_MX"

# Testar rota de países (mostra timezone e localizacao)
curl "http://localhost:8000/api/carrega_paises"

# Selecionar país Brasil → Idioma Português
# Selecionar país Portugal → Idioma Inglês
# Selecionar país Espanha → Idioma Espanhol
# etc.
```

## 🚀 Funcionalidades Implementadas

✅ **Auto-translação**: Mudança automática de idioma ao selecionar país  
✅ **Timezone automática**: Configuração por localidade do país  
✅ **Cache inteligente**: Dados cacheados para evitar chamadas desnecessárias  
✅ **Breadcrumb multilíngue**: Navegação visual traduzida  
✅ **Dropdowns dinâmicos**: Labels e opções adaptadas ao idioma atual  
✅ **Interface responsiva**: Funciona em todos os dispositivos  
✅ **Minimalista**: Design limpo com complexidade apenas nos dados  

## 📝 Notas Importantes

- Flask-Babel foi instalado mas não é necessário (usa implementação customizada)
- Todas as traduções estão embutidas no arquivo `i18n.js`
- O sistema pode facilmente adicionar mais idiomas editando o dicionário em `i18n.js`
- A API `/api/i18n` centraliza todas as traduções para manutenção fácil

---

🤖 Gerado com [Claude Code](https://claude.com/claude-code)
