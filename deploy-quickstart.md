# Quickstart para Deploy na Render ⚡

Guia rápido para publicar sua aplicação Hello World na Render em 5 minutos!

## 📋 Pré-requisitos

- ✅ Conta no [Render.com](https://render.com) (gratuita)
- ✅ Repositório Git com o projeto atualizado
- ✅ Código testado localmente

## 🚀 Publicar - Passo a Passo Rápido

### 1. Prepare seu repositório

```bash
# Verifique os arquivos importantes
ls -la
# Deve conter: app.py, requirements.txt, render.yaml
```

### 2. No Dashboard do Render

1. Acesse [render.com/dashboard](https://dashboard.render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Escolha seu repositório GitHub (ou crie novo)

### 3. Configure a Web Service

```
Name: hello-world-app
Region: US
Environment: Python
Root Directory: [deixe em branco]
Build Command: pip install -r requirements.txt --quiet
Start Command: gunicorn --bind 0.0.0.0:${PORT} app:app
```

4. Em **Environment Variables**, adicione:
   ```
   PYTHON_VERSION = 3.12.x
   FLASK_ENV = production
   ```

### 4. Clique em "Create Web Service"

Agora aguarde 5-10 minutos enquanto o Render:
- Clona seu repositório
- Instala as dependências
- Constrói a imagem Docker (opcional)
- Lanza sua aplicação

## ✅ Verificando se está funcionando

Após ~5-10 minutos, você terá um URL como:
```
https://hello-world-app.onrender.com
```

Teste as rotas:
- `https://seu-app.onrender.com/` → Hello World básico
- `https://seu-app.onrender.com/greeting` → Página HTML bonita
- `https://seu-app.onrender.com/status` → Status do app

## 🎉 Pronto!

Sua aplicação está online e rodando na Render gratuitamente!

---

### Próximos passos:

1. **Customize**: Mude o nome da aplicação nas configurações
2. **Variáveis de ambiente**: Adicione segredos sensíveis
3. **Logs**: Monitore em Dashboard → Logs

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
