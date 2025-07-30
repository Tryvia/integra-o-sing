# API de Integrações Ativas

Esta API Flask permite consultar integrações ativas de clientes através de seus CNPJs, integrando com o Supabase e APIs externas.

## Deploy no Render

### Pré-requisitos
1. Conta no [Render](https://render.com)
2. Repositório Git com este código

### Passos para Deploy

1. **Conectar Repositório**
   - Faça login no Render
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório Git

2. **Configurar Serviço**
   - **Name**: `integracoes-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`

3. **Configurar Variáveis de Ambiente**
   No painel do Render, adicione as seguintes variáveis:

   ```
   SUPABASE_URL=https://mzjdmhgkrroajmsfwryu.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16amRtaGdrcnJvYWptc2Z3cnl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyMzMwMzUsImV4cCI6MjA2MzgwOTAzNX0.tQCwUfFCV7sD-IexQviU0XEPcbn9j5uK9NSUbH-OeBc
   API_BASE_URL=http://192.168.40.11:50231
   API_USER=integracaoportal
   API_PASSWORD=cadeadoNG1
   ```

4. **Deploy**
   - Clique em "Create Web Service"
   - Aguarde o build e deploy automático

### Endpoints Disponíveis

- `GET /` - Status da API
- `GET /health` - Health check
- `GET /api/integracoes/teste-conectividade` - Testa conectividade
- `POST /api/integracoes/consultar-por-cnpj` - Consulta por CNPJ
- `GET /api/integracoes/consultar-por-cliente/{id}` - Consulta por ID do cliente
- `GET /api/integracoes/clientes` - Lista clientes do Supabase

### Exemplo de Uso

```bash
# Testar conectividade
curl https://sua-api.onrender.com/api/integracoes/teste-conectividade

# Consultar por CNPJ
curl -X POST https://sua-api.onrender.com/api/integracoes/consultar-por-cnpj \
  -H "Content-Type: application/json" \
  -d '{"cnpj": "11810190000129"}'
```

### Integração com Frontend

No seu arquivo HTML, altere a URL da API para a URL do Render:

```javascript
// Substituir localhost pela URL do Render
const response = await fetch(`https://sua-api.onrender.com/api/integracoes/consultar-por-cnpj`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ cnpj: cnpj })
});
```

### Monitoramento

- Logs disponíveis no painel do Render
- Health check em `/health`
- Métricas automáticas de performance

### Troubleshooting

1. **Erro de Build**: Verifique se `requirements.txt` está correto
2. **Erro de Start**: Confirme o comando de start
3. **Erro de API**: Verifique as variáveis de ambiente
4. **Timeout**: APIs externas podem estar inacessíveis do Render

### Estrutura do Projeto

```
integracoes-api/
├── src/
│   ├── main.py              # Aplicação Flask principal
│   ├── routes/
│   │   ├── integracoes.py   # Rotas de integração
│   │   └── ...
│   └── models/
├── requirements.txt         # Dependências Python
├── render.yaml             # Configuração do Render (opcional)
└── README.md               # Este arquivo
```

