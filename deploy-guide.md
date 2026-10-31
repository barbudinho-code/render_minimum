# Guia de Deploy na Render

## Passo a Passo Completo

### 1. Preparação do Repositório

Certifique-se que seu repositório Git contém:
- `app.py` - Sua aplicação Flask
- `requirements.txt` - Dependências Python
- `render.yaml` - Configuração de deploy (opcional, o Render pode detectar automaticamente)

### 2. Criando Novo Projeto na Render

1. Acesse [dashboard.render.com](https://dashboard.render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Escolha sua opção:

#### Opção A: Usar repositório existente (GitHub, GitLab, Bitbucket)
- **Name**: `hello-world-app` (pode mudar depois)
- **Region**: US (ou Brasil se disponível)
- **Environment**: Python
- **Root Directory**: deixem em branco
- **Build Command**: `pip install -r requirements.txt --quiet`
- **Start Command**: `gunicorn --bind 0.0.0.0:${PORT} app:app`

#### Opção B: Link direto ao repositório Git
- Cole o link do seu GitHub/GitLab

4. Configure as variáveis de ambiente:
   - **PYTHON_VERSION**: `3.12.x` (ou sua versão)

5. Clique em **"Create Web Service"**

### 3. Alternativa: Deploy via Push ao Git

Se você já conectou o repositório com o Render:

```bash
git push render production
```

O Render detectará automaticamente e iniciará o deploy.

### 4. Verificando o Deploy

Depois de alguns minutos, sua aplicação estará no link:
- `https://hello-world-app.onrender.com` (ou nome que você escolheu)

Teste acessando:
- `/` → Hello World básico
- `/greeting` → Página com HTML estilizado
- `/status` → Informações da aplicação

## Atualização Contínua

O Render usa **Git deployments**:
1. Faça alterações no código
2. Commit e push ao branch principal (`main`)
3. O Render detecta automaticamente e reinicia o deploy
4. Após 2-5 minutos, sua atualização está no ar!

## Troubleshooting

### Aplicação não inicia?
Verifique:
- O comando `run` está correto no arquivo
- A porta `$PORT` é definida pelo Render (geralmente 10000)

### Erro de dependência?
Adicione ao `requirements.txt`:
```
flask>=2.3.0
gunicorn>=21.0.0
```

## Próximos Passos

- Adicione um banco de dados
- Configure variáveis de ambiente seguras
- Implemente autenticação
- Use logs do Render para debug

---

Para mais informações: [Render Docs](https://render.com/docs)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
