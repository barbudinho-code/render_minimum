# Hello World Application for Render 🚀

Aplicação web simples "Hello, World!" configurada para rodar na plataforma Render usando Git deployments.

## ✅ Estrutura do Projeto

```
render-minimum/
├── app.py                 # Aplicação Flask com rotas Hello World
├── render.yaml            # Configuração de deploy no Render
├── requirements.txt       # Dependências Python
├── .gitignore             # Arquivos a ignorar no Git
└── README.md              # Documentação deste projeto
```

## 🚀 Como Rodar Localmente

```bash
# Instale as dependências
pip install -r requirements.txt

# Execute localmente (porta padrão 5000)
python app.py

# Abra no navegador: http://localhost:5000
```

### Testando com Gunicorn (ambiente mais próximo do Render):

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 app:app
```

## 🌐 Deploy na Render

### Método 1: Criar novo projeto no Render via Web UI

1. Acesse [dashboard.render.com](https://dashboard.render.com) e faça login
2. Clique em **"New +"** → **"Web Service"**
3. Selecione "Link to existing repository" ou use GitHub/GitLab

4. Configure as opções:
   - **Name**: `hello-world-app` (pode alterar depois nas configurações)
   - **Region**: US (ou Brasil se disponível em sua região)
   - **Environment**: Python
   - **Root Directory**: deixe em branco (use a raiz do repositório)

5. Na aba **Build & Deploy**:
   - **Build Command**: `pip install -r requirements.txt --quiet`
   - **Start Command**: `gunicorn --bind 0.0.0.0:${PORT} app:app`

6. Em **Environment Variables**, adicione:
   - `PYTHON_VERSION`: `3.12.x` (ou sua versão)
   - `FLASK_ENV`: `production`

7. Clique em **"Create Web Service"** para publicar

### Método 2: Push via Git

Se você já conectou o repositório com o Render:

```bash
git add .
git commit -m "Prepare for deployment"
git push render production
```

O Render detectará automaticamente:
- ✅ Tipo de ambiente: Python
- ✅ Dependências do `requirements.txt`
- ✅ Aplicação Flask pronta para rodar

## 🌍 Rotas Disponíveis

Após o deploy, teste estas rotas no link da sua aplicação (ex: `https://hello-world-app.onrender.com`):

| Rota | Descrição |
|------|-----------|
| `/` | Hello World básico - retorna texto simples |
| `/greeting` | Página Hello World com HTML e CSS estilizado |
| `/status` | Informações sobre o status da aplicação |
| `/ws` | Teste de simulação WebSocket |

## 📋 Arquivo render.yaml

O arquivo `render.yaml` define as configurações recomendadas para deploy no Render:

```yaml
services:
  - type: web
    name: hello-world-app
    env: python
    build_cmd: |
      pip install flask gunicorn > /dev/null 2>&1
    run: gunicorn --bind 0.0.0.0:${PORT} app:app
    
    # Configurações básicas para produção no Render
    disk: 512
    memory: 512
```

> **Nota**: O Render pode não usar `render.yaml` diretamente, mas segue as mesmas configurações do Build Command e Start Command nas configurações da Web Service.

## 🔄 Atualizações Contínuas (Git Deployments)

O Render usa o conceito de **Continuous Deployment via Git**:

1. Faça alterações no código
2. Faça commit com mensagem descritiva
3. Push ao branch `main` ou à branch remota que você configurou
4. O Render detecta automaticamente as alterações
5. Após 2-5 minutos, sua atualização estará online!

## 🔧 Troubleshooting

### Aplicação não inicia?

Verifique:
- ✅ O comando `run` está correto no arquivo `render.yaml`
- ✅ A porta `${PORT}` é definida pelo Render (geralmente `10000`)
- ✅ Sua aplicação retorna algo em cada rota Flask

### Erro de dependência?

Adicione as dependências ao `requirements.txt`:
```
flask>=2.3.0
gunicorn>=21.0.0
```

### Logs do Render

Os logs ajudam a debugar:
- Acesse **Dashboard** → Selecione seu projeto → **Logs**
- Verifique erros durante o build e start

## 📦 O que vem incluso

- ✅ Aplicação Flask simples "Hello, World!"
- ✅ 3 rotas diferentes para testar
- ✅ Configuração otimizada para Render
- ✅ Instruções detalhadas de deploy
- ✅ Guia completo de troubleshooting

## 🔗 Recursos Adicionais

- [Documentação do Render](https://render.com/docs)
- [Flask Docs](https://flask.palletsprojects.com/)
- [Guia de Deploy](./deploy-guide.md) - instruções passo a passo

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
