# Flask + React Application

## Descrição

Aplicação web moderna que combina **Flask** (Python) como backend com **React** (JavaScript) como frontend.

## Estrutura do Projeto

```
render_minimum/
├── app.py              # Backend Flask - serve API e frontend
├── wsgi.py             # Entry point para deployment na Render
├── static/             # Frontend + Ícones
│   ├── index.html      # Single Page Application com React
│   └── icon.ico        # Favicon (32x32)
└── README.md           # Esta documentação
```

## Endpoints Disponíveis

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Serve a aplicação React (frontend) |
| `/favicon.ico` | GET | Ícone da aplicação (.ico) |
| `/static/<path>` | GET | Arquivos estáticos do frontend |
| `/api/items` | GET | Lista todos os itens da aplicação |
| `/api/items/<id>` | GET | Retorna um item específico pelo ID |
| `/api/profile` | GET | Informações do perfil (nome, email) |
| `/about` | GET | Página sobre a aplicação |
| `/api/health` | GET | Endpoint de saúde do servidor |

## API Response (GET /api/items)

```json
[
  {
    "id": 1,
    "name": "Item Um",
    "description": "Descrição do primeiro item"
  },
  {
    "id": 2,
    "name": "Item Dois",
    "description": "Descrição do segundo item"
  },
  {
    "id": 3,
    "name": "Item Três",
    "description": "Descrição do terceiro item"
  }
]
```

## Como Rodar Localmente

```bash
# Instalar Flask (se necessário)
pip install flask

# Rodar o backend
python app.py

# A aplicação estará disponível em: http://localhost:5000
```

## Recursos da Interface

- ✅ **Design moderno** com gradientes e animações suaves
- ✅ **Hierarquia interativa**: País → Partido → Cargo → Candidato
- ✅ **Breadcrumb** para navegação visual
- ✅ **Cache de dados** evita chamadas HTTP desnecessárias
- ✅ **Responsivo** - funciona em desktop e mobile
- ✅ **API Documentation** integrada na interface

## Tecnologias Utilizadas

- **Backend**: Python 3, Flask
- **Frontend**: React 18 (via CDN)
- **Deployment**: Render.com (suporte via wsgi.py)

---

🤖 Gerado com [Claude Code](https://claude.com/claude-code)
