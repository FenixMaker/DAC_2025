# Projeto DAC — Documentação Geral (Web + Python)

**Autor:** Alejandro Alexandre  
**RA:** 197890  
**Curso:** Análise e Desenvolvimento de Sistemas  
**Ano:** 2025  

Este documento explica como o projeto DAC está estruturado e funcionando tanto na camada Python (aplicação desktop/UI e serviços de dados) quanto na camada Web (backend FastAPI e frontend Next.js). Também cobre como executar o sistema em modo de desenvolvimento com um único comando e como o banco de dados é gerenciado.

O Sistema DAC foi desenvolvido como trabalho de conclusão de curso pelo aluno Alejandro Alexandre (RA: 197890), implementando uma solução completa para análise de exclusão digital no Brasil.

## Visão Geral
- Arquitetura em três camadas:
  - Python ("Versão PY"): núcleo de dados, UI desktop (Tkinter), utilitários e testes.
  - Backend Web (FastAPI): APIs HTTP que reutilizam o `DatabaseManager` do projeto Python.
  - Frontend Web (Next.js): dashboard e páginas que consomem as APIs.
- Banco de dados SQLite centralizado em `d:\Sites\DAC\Banco de dados\dac_database.db`.
- Execução simplificada: `npm run dev` inicia backend FastAPI e frontend Next.js automaticamente.

## Estrutura de Pastas (resumo)
- `d:\Sites\DAC\Versão PY\src\database\` — Modelos, `DatabaseManager` e consultas otimizadas.
- `d:\Sites\DAC\Versão PY\web\backend\app\` — FastAPI (`main.py`, routers, serviços).
- `d:\Sites\DAC\Versão Web\` — Frontend Next.js, rotas internas (`app/api/*`) e componentes.
- `d:\Sites\DAC\Banco de dados\` — Banco central (`dac_database.db`) e arquivos WAL/SHM.

## Banco de Dados
- Tipo: SQLite, otimizado com pragmas e cache em memória.
- Caminho central: `d:\Sites\DAC\Banco de dados\dac_database.db`.
- Arquivos relacionados: `dac_database.db-wal`, `dac_database.db-shm`, `db_integrity_report.json`.
- Inicialização e integridade:
  - `DatabaseManager.initialize_database()` cria tabelas/índices e realiza otimizações.
  - `check_database_integrity()` executa `PRAGMA integrity_check`, `foreign_key_check`, `quick_check`.
- Origem do caminho no backend:
  - `d:\Sites\DAC\Versão PY\web\backend\app\services\db.py` define explicitamente o `db_path` para o diretório central `Banco de dados`.

## Backend Web (FastAPI)
- App principal: `d:\Sites\DAC\Versão PY\web\backend\app\main.py`.
- Rotas:
  - `GET /api/health` — status do backend.
  - `GET /api/estatisticas/resumo` — estatísticas agregadas: `regioes`, `domicilios`, `individuos`, `dispositivos`, `internet`.
  - `GET /api/individuos` — lista paginada com filtros (`page`, `limit`, `regiao_id`, `idade`, `genero`).
- Serviço de banco:
  - `app/services/db.py` importa `DatabaseManager` do Python e inicializa com `db_path` centralizado.
- Execução direta (opcional):
  - `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

## Frontend Web (Next.js)
- Rotas internas que proxy para o backend (exemplos):
  - `d:\Sites\DAC\Versão Web\app\api\estatisticas\resumo\route.ts`
  - `d:\Sites\DAC\Versão Web\app\api\individuos\route.ts`
  - `d:\Sites\DAC\Versão Web\app\api\health\route.ts`
- Configuração de API base via ambiente:
  - `.env.local`: `NEXT_PUBLIC_DAC_API_URL=http://localhost:8000`
- Componente `StatsCards` foi fortalecido contra dados indefinidos e formatação de números para evitar erros de `toLocaleString`.

## Fluxo de Dados
1. Frontend chama rotas Next.js (`/app/api/*`).
2. Rotas Next.js usam `NEXT_PUBLIC_DAC_API_URL` para consultar o FastAPI.
3. FastAPI usa `get_db_manager()` que instancia `DatabaseManager` apontando para `d:\Sites\DAC\Banco de dados\dac_database.db`.
4. Respostas são sanitizadas e mapeadas para chaves esperadas pelo frontend.

## Como Executar (Desenvolvimento — Windows/PowerShell)
- Pré-requisito: Node.js e Python instalados.
- Passos:
  1) No diretório `d:\Sites\DAC\Versão Web`, verifique `.env.local`:
  
     `NEXT_PUBLIC_DAC_API_URL=http://localhost:8000`
  
  2) Inicie tudo com um único comando:
  
     `npm run dev`
  
  - Isso inicia:
    - Backend FastAPI em `http://localhost:8000` usando `uvicorn`.
    - Frontend Next.js em `http://localhost:3002`.
  - Logs exibem inicialização do banco apontando para `d:\Sites\DAC\Banco de dados\dac_database.db`.

## Execução (Python — UI Desktop)
- Inicialização pela aplicação principal:
  - `d:\Sites\DAC\Versão PY\main.py`
- Comando:
  
  `./.venv/Scripts/python.exe ./main.py`
  
- A UI carrega, inicializa o banco, e exibe KPIs com base em `get_database_stats()`.

## Scripts Úteis (Python)
- `scripts/seed_sample_data.py` — insere dados mínimos de teste.
- `scripts/populate_sample_data.py` — população completa de amostra.
- `scripts/check_db_connection.py` — valida conexão (`SELECT 1`).
- `scripts/db_integrity_report.py` — gera `data/db_integrity_report.json`.

## Troca ou Ajuste do Caminho do Banco
- O backend FastAPI já usa o caminho centralizado. Caso precise tornar configurável:
  - Adicionar suporte a variável `DAC_DB_PATH` e ler `os.environ.get("DAC_DB_PATH")` em `app/services/db.py`.
- Certifique-se de que a pasta tem permissões de escrita (Windows) e que WAL/SHM são co-localizados.

## Troubleshooting
- Frontend sem dados:
  - Verifique `http://localhost:8000/api/health` e `.env.local`.
- Erro de formatação numérica:
  - O `StatsCards` já valida entradas; garantir que resposta do backend tem chaves esperadas.
- Conflito de portas:
  - Ajuste porta do Next com `next dev --port 3002` em `package.json`.

## Referências Técnicas
- `src/database/database_manager.py` — define padrão do caminho e inicializa engine SQLite.
- `web/backend/app/services/db.py` — integração com `DatabaseManager` (caminho centralizado).
- `Versão Web/package.json` — script `dev` com `concurrently` para subir backend e frontend.
- `.env.local` — define URL base da API para o Next.js.

---
Mantemos a organização alinhada com os documentos do projeto e validamos o funcionamento end-to-end: ao executar `npm run dev`, o frontend consome o backend FastAPI, que por sua vez usa o banco centralizado em `d:\Sites\DAC\Banco de dados`.