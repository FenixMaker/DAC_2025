# Banco de Dados do Projeto DAC — Documentação Técnica

> **Documento explicativo**: Como o banco de dados foi implementado, como funciona a conexão com Python e Web, e quais tecnologias foram utilizadas.

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Arquitetura do Banco de Dados](#-arquitetura-do-banco-de-dados)
3. [Implementação - Versão Python](#-implementação---versão-python)
4. [Implementação - Versão Web](#-implementação---versão-web)
5. [Como Executar Localmente](#-como-executar-localmente)
6. [Scripts e Ferramentas](#-scripts-e-ferramentas)
7. [Manutenção e Monitoramento](#-manutenção-e-monitoramento)
8. [Considerações Técnicas](#-considerações-técnicas)

---

## 🎯 Visão Geral

### Objetivo do Sistema

O banco de dados armazena informações sobre **inclusão digital no Brasil**, organizando dados de:
- **Regiões geográficas** (Norte, Nordeste, Sudeste, Sul, Centro-Oeste)
- **Domicílios** (localização, renda, acesso à internet)
- **Indivíduos** (idade, gênero, escolaridade, deficiência)
- **Uso de dispositivos** (computador, celular, tablet)
- **Uso de internet** (frequência, atividades, barreiras)

### Resumo das Tecnologias

| Componente | Tecnologia | Localização |
|------------|-----------|-------------|
| **Versão Python** | SQLite + SQLAlchemy ORM | `Versão PY/data/dac_database.db` |
| **Versão Web** | PostgreSQL/MySQL/SQLite (adapter) | `Versão Web/lib/db.ts` |
| **Configuração** | Variável `DATABASE_URL` | Ambiente (.env) |
| **Scripts** | Python (inicialização/seed) | `Versão PY/scripts/` |

### Fluxo de Dados

```
CSV/Dados externos → Scripts Python → SQLite/PostgreSQL → API Web → Dashboard
```

---

## 🗄️ Arquitetura do Banco de Dados

### Diagrama Estrutural

![Diagrama do Banco de Dados](./db_diagram.svg)

*Caso tenha o arquivo SVG do diagrama, coloque em `documentacao/db_diagram.svg`*

### Tabelas Principais

#### 1. **regions** (Regiões)
Armazena as macrorregiões do Brasil.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | Identificador único |
| `code` | String(10) | Código da região (ex: "SE", "N") |
| `name` | String(100) | Nome completo (ex: "Sudeste") |
| `state` | String(50) | Estado (usado para subdivisões) |
| `macro_region` | String(20) | Macrorregião |
| `description` | String(200) | Descrição adicional |

**Relacionamentos**: Uma região possui muitos domicílios.

---

#### 2. **households** (Domicílios)
Representa as residências e suas características.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | Identificador único |
| `region_id` | Integer (FK) | Referência para `regions.id` |
| `city` | String(100) | Cidade |
| `area_type` | String(20) | "urbana" ou "rural" |
| `income_range` | String(50) | Faixa de renda |
| `household_size` | Integer | Número de moradores |
| `has_internet` | Boolean | Se possui internet |

**Índices otimizados**:
- `idx_household_region_area` (region_id + area_type)
- `idx_household_internet_area` (has_internet + area_type)

**Relacionamentos**: 
- Pertence a uma região
- Possui muitos indivíduos

---

#### 3. **individuals** (Indivíduos)
Dados demográficos das pessoas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | Identificador único |
| `household_id` | Integer (FK) | Referência para `households.id` |
| `age` | Integer | Idade |
| `gender` | String(10) | Gênero (masculino/feminino/outro) |
| `education_level` | String(50) | Nível de escolaridade |
| `has_disability` | Boolean | Se possui deficiência |
| `employment_status` | String(30) | Situação de emprego |
| `created_at` | DateTime | Data de registro |

**Índices otimizados**:
- `idx_individual_age_gender` (age + gender)
- `idx_individual_disability_age` (has_disability + age)

**Relacionamentos**: 
- Pertence a um domicílio
- Possui registros de uso de dispositivos
- Possui registros de uso de internet

---

#### 4. **device_usage** (Uso de Dispositivos)
Registra posse e uso de equipamentos tecnológicos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | Identificador único |
| `individual_id` | Integer (FK) | Referência para `individuals.id` |
| `device_type` | String(30) | Tipo (computador/celular/tablet) |
| `has_device` | Boolean | Se possui o dispositivo |
| `usage_frequency` | String(20) | Frequência de uso |
| `access_location` | String(30) | Onde usa (casa/trabalho/escola) |
| `created_at` | DateTime | Data de registro |

**Índices otimizados**:
- `idx_device_type_access` (device_type + has_device)

---

#### 5. **internet_usage** (Uso de Internet)
Registra padrões de acesso à internet.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer (PK) | Identificador único |
| `individual_id` | Integer (FK) | Referência para `individuals.id` |
| `uses_internet` | Boolean | Se usa internet |
| `access_frequency` | String(30) | Frequência de acesso |
| `main_activities` | Text | Atividades principais (JSON) |
| `barriers_to_access` | Text | Barreiras de acesso |
| `created_at` | DateTime | Data de registro |

**Índices otimizados**:
- `idx_internet_access_frequency` (uses_internet + access_frequency)

---

### Decisões de Design

✅ **Por que usar Foreign Keys?**
- Garante integridade referencial (não permitir indivíduos sem domicílio)
- Facilita consultas com JOINs

✅ **Por que tantos índices?**
- Consultas típicas: "Quantas pessoas com deficiência têm internet?"
- Índices compostos aceleram filtros combinados (ex: região + área urbana)

✅ **Por que DateTime em created_at?**
- Permite análise temporal dos dados
- Facilita auditorias e versionamento

---

## 🐍 Implementação - Versão Python

### Tecnologias Utilizadas

- **ORM**: SQLAlchemy (mapeamento objeto-relacional)
- **Banco de Dados**: SQLite 3
- **Arquivo físico**: `Versão PY/data/dac_database.db`
- **Modelos**: `Versão PY/src/database/models.py`
- **Gerenciador**: `Versão PY/src/database/database_manager.py`

### Como Funciona

#### 1. Definição dos Modelos (models.py)

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Region(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, index=True)
    name = Column(String(100), nullable=False)
    # ... outros campos
    
    households = relationship("Household", back_populates="region")
```

**O que isso faz?**
- Define a estrutura da tabela em Python (não precisa escrever SQL CREATE TABLE)
- Cria relacionamentos automáticos entre tabelas
- Adiciona validações e constraints

---

#### 2. Gerenciamento (DatabaseManager)

A classe `DatabaseManager` em `database_manager.py` cuida de:

##### ✅ Inicialização do Banco

```python
def initialize_database(self):
    # 1. Criar engine SQLite
    self.engine = create_engine(f"sqlite:///{self.db_path}", 
                                echo=False,
                                pool_pre_ping=True)
    
    # 2. Configurar otimizações (PRAGMAs)
    with self.engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))
        conn.execute(text("PRAGMA cache_size=10000"))
        conn.execute(text("PRAGMA foreign_keys=ON"))
    
    # 3. Criar todas as tabelas
    Base.metadata.create_all(self.engine)
```

**Otimizações Aplicadas**:

| PRAGMA | Valor | Benefício |
|--------|-------|-----------|
| `journal_mode` | WAL | Write-Ahead Logging: leituras não bloqueiam escritas |
| `synchronous` | NORMAL | Balanceamento entre segurança e performance |
| `cache_size` | 10000 | Cache de ~10MB para páginas frequentes |
| `temp_store` | MEMORY | Tabelas temporárias na RAM |
| `foreign_keys` | ON | Valida integridade referencial |

---

##### ✅ Gerenciamento de Sessões

```python
def get_session(self):
    """Retorna uma sessão configurada"""
    if self.Session is None:
        raise RuntimeError("Banco não inicializado")
    
    session = self.Session()
    session.execute(text("SELECT 1"))  # Testa conexão
    return session
```

**Por que sessions?**
- Gerencia transações (BEGIN/COMMIT/ROLLBACK automático)
- Pool de conexões eficiente
- Proteção contra SQL injection (queries parametrizadas)

---

##### ✅ Verificação de Integridade

```python
def check_database_integrity(self):
    """Verifica saúde do banco"""
    results = {
        'integrity_check': None,      # PRAGMA integrity_check
        'foreign_key_check': None,    # PRAGMA foreign_key_check
        'quick_check': None,          # PRAGMA quick_check
        'errors': []
    }
    # ... executa checks e retorna relatório
```

**Quando usar?**
- Após importação de dados grandes
- Antes de backups
- Em caso de erros inexplicáveis

---

##### ✅ Métricas de Performance

```python
def get_performance_metrics(self):
    """Retorna estatísticas do banco"""
    return {
        'page_count': ...,       # Número de páginas
        'page_size': ...,        # Tamanho da página (bytes)
        'database_size_bytes': ...,
        'journal_mode': 'WAL',
        'cache_size': 10000
    }
```

---

### Por Que SQLite?

| ✅ Vantagens | ⚠️ Limitações |
|-------------|---------------|
| Arquivo único (fácil distribuir) | Concorrência limitada de escrita |
| Zero configuração | Não ideal para +100 escritas/segundo |
| Performance excelente para leitura | Arquivo pode crescer muito |
| Funciona offline | Necessita VACUUM periódico |

**Quando migrar para PostgreSQL?**
- Mais de 5 usuários simultâneos escrevendo
- Necessidade de replicação
- Queries muito complexas (CTEs recursivas)

---

## 🌐 Implementação - Versão Web

### Tecnologias Utilizadas

- **Framework**: Next.js (TypeScript)
- **Adapter de BD**: `Versão Web/lib/db.ts` (multi-banco)
- **Bancos Suportados**: PostgreSQL, MySQL/MariaDB, SQLite
- **Configuração**: Variável de ambiente `DATABASE_URL`

### Arquitetura do Adapter

#### Como Funciona o db.ts

```typescript
// lib/db.ts - Adapter inteligente
function getAdapter(): DBAdapter {
  if (isPostgres()) return createPostgresAdapter()
  if (isMysql()) return createMysqlAdapter()
  if (isSqlite()) return createSqliteAdapter()
  throw new Error('DATABASE_URL inválida')
}

export async function query<T>(sql: string, params: any[]) {
  const adapter = getAdapter()
  const client = await adapter.connect()
  const res = await client.query(sql, params)
  return { rows: res.rows as T[] }
}
```

**Detecção Automática**:
- `postgres://...` → Usa driver `pg`
- `mysql://...` → Usa driver `mysql2`
- `sqlite://...` → Usa driver `better-sqlite3`

---

#### Adapter PostgreSQL

```typescript
function createPostgresAdapter(): DBAdapter {
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.DATABASE_SSL === 'true' 
         ? { rejectUnauthorized: false } 
         : undefined
  })
  
  return {
    connect: async () => {
      const client = await pool.connect()
      return {
        query: (sql, params) => client.query(sql, params),
        release: () => client.release()
      }
    },
    // ... transações com BEGIN/COMMIT/ROLLBACK
  }
}
```

**Recursos**:
- ✅ Pool de conexões automático
- ✅ Suporte SSL para produção
- ✅ Transações com rollback automático em caso de erro

---

#### Adapter SQLite (Web)

```typescript
function createSqliteAdapter(): DBAdapter {
  let dbPath = process.env.DATABASE_URL
  dbPath = dbPath.replace(/^sqlite:\/\/\//, '') // Remove prefixo
  
  const db = new sqlite(dbPath)
  
  return {
    connect: async () => ({
      query: async (sql, params) => {
        const stmt = db.prepare(sql)
        return { rows: stmt.all(...params) }
      }
    })
  }
}
```

**Observação**: Trata caminhos do Windows corretamente (`C:\Users\...`)

---

### Configuração do Ambiente

#### Exemplo 1: Usar SQLite Local

```powershell
# .env ou .env.local
DATABASE_URL=sqlite:///C:/Users/FenixPosts/Desktop/DAC_2025/Versão PY/data/dac_database.db
```

#### Exemplo 2: Usar PostgreSQL (Produção)

```powershell
# .env.production
DATABASE_URL=postgres://user:senha@localhost:5432/dac_db
DATABASE_SSL=true
```

#### Exemplo 3: Usar MySQL/MariaDB

```powershell
# .env
DATABASE_URL=mysql://user:senha@localhost:3306/dac_db
```

---

### Fluxo de Requisição

```
1. Cliente Web → GET /api/consultas
2. API Route → import { query } from '@/lib/db'
3. db.ts → Detecta tipo de banco via DATABASE_URL
4. Adapter → Executa SQL parametrizado
5. Resposta → JSON para o cliente
```

**Exemplo de API Route**:

```typescript
// app/api/consultas/route.ts
import { query } from '@/lib/db'

export async function GET() {
  const { rows } = await query(
    'SELECT * FROM regions WHERE macro_region = $1',
    ['Sudeste']
  )
  return Response.json(rows)
}
```

---

### Instalação de Drivers Opcionais

Os adapters só carregam o driver quando necessário:

```powershell
# PostgreSQL (já vem por padrão via 'pg')
pnpm add pg

# MySQL (opcional)
pnpm add mysql2

# SQLite para web (opcional)
pnpm add better-sqlite3
```

**Se o driver não estiver instalado**: O adapter lança erro explicativo.

---

### Vantagens do Design Multi-Banco

| Benefício | Descrição |
|-----------|-----------|
| 🔄 **Flexibilidade** | Troca de banco sem reescrever código |
| 🧪 **Testes** | SQLite em desenvolvimento, Postgres em produção |
| 📦 **Otimização** | Só instala drivers necessários |
| 🔒 **Segurança** | Queries parametrizadas em todos os adapters |

---

## 🚀 Como Executar Localmente

### Pré-requisitos

- Python 3.8+ instalado
- Node.js 18+ e pnpm instalado
- Git (opcional, para clonar o repositório)

---

### Versão Python (Desktop)

#### Passo 1: Configurar Ambiente Python

```powershell
# Navegar para a pasta da versão Python
cd "C:\Users\FenixPosts\Desktop\DAC_2025\Versão PY"

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

---

#### Passo 2: Inicializar o Banco de Dados

```powershell
# Opção A: Executar o main.py (inicializa automaticamente)
python main.py

# Opção B: Inicializar manualmente via Python
python -c "from src.database.database_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database(); print('Banco inicializado!')"
```

**Resultado esperado**:
- Arquivo criado: `Versão PY/data/dac_database.db`
- Tabelas criadas: regions, households, individuals, device_usage, internet_usage
- Dados iniciais inseridos (5 regiões)

---

#### Passo 3: Popular com Dados de Exemplo

```powershell
# Executar script de seed
python scripts/seed_sample_data.py

# Ou script de população completa
python scripts/populate_sample_data.py
```

---

#### Passo 4: Verificar Integridade

```powershell
# Checar saúde do banco
python scripts/db_integrity_report.py

# Verificar conexão PostgreSQL (se usar Postgres)
python scripts/check_postgres_connection.py
```

---

### Versão Web (Next.js)

#### Passo 1: Configurar Ambiente

```powershell
# Navegar para a pasta web
cd "C:\Users\FenixPosts\Desktop\DAC_2025\Versão Web"

# Instalar dependências
pnpm install
```

---

#### Passo 2: Configurar Banco de Dados

**Opção A: Usar SQLite Local (Desenvolvimento)**

```powershell
# Criar arquivo .env.local
echo "DATABASE_URL=sqlite:///C:/Users/FenixPosts/Desktop/DAC_2025/Versão PY/data/dac_database.db" > .env.local

# Instalar driver SQLite
pnpm add better-sqlite3
```

**Opção B: Usar PostgreSQL (Produção)**

```powershell
# Criar arquivo .env.local
@"
DATABASE_URL=postgres://usuario:senha@localhost:5432/dac_db
DATABASE_SSL=false
"@ | Out-File -FilePath .env.local -Encoding utf8
```

---

#### Passo 3: Iniciar Servidor de Desenvolvimento

```powershell
# Rodar servidor Next.js
pnpm dev

# Servidor estará disponível em: http://localhost:3000
```

---

#### Passo 4: Testar Conexão

Acesse no navegador:
- **Dashboard**: http://localhost:3000
- **Status do Banco**: http://localhost:3000/status-banco
- **API de Consultas**: http://localhost:3000/api/consultas

---

### Scripts de Inicialização Rápida

#### Windows (Desktop + Web)

```powershell
# Executar launcher desktop
.\Iniciar-Desktop.bat

# Executar launcher web
.\Iniciar-Web.bat
```

Esses scripts estão na raiz do projeto e automatizam a inicialização.

---

### Troubleshooting

| Problema | Solução |
|----------|---------|
| ❌ `ModuleNotFoundError: No module named 'sqlalchemy'` | Execute `pip install -r requirements.txt` |
| ❌ `Error: Cannot find module 'pg'` | Execute `pnpm add pg` |
| ❌ `PRAGMA journal_mode failed` | Arquivo do banco corrompido, delete e reinicialize |
| ❌ `Connection refused (PostgreSQL)` | Verifique se o PostgreSQL está rodando: `pg_ctl status` |
| ❌ Caminho SQLite inválido (Windows) | Use barra dupla: `sqlite:///C://caminho//arquivo.db` |

---

## 🛠️ Scripts e Ferramentas

### Scripts Disponíveis (`Versão PY/scripts/`)

| Script | Função | Quando Usar |
|--------|--------|-------------|
| `init_postgres_schema.py` | Criar schema em PostgreSQL | Migração para produção |
| `check_postgres_connection.py` | Testar conexão Postgres | Debug de conexão |
| `check_db_connection.py` | Testar conexão SQLite | Verificar integridade |
| `populate_sample_data.py` | Popular com dados de teste | Desenvolvimento inicial |
| `seed_sample_data.py` | Inserir dados específicos | Testes unitários |
| `db_integrity_report.py` | Gerar relatório de saúde | Manutenção periódica |

---

### Exemplos de Uso

#### 1. Verificar Saúde do Banco

```powershell
cd "Versão PY"
python scripts/db_integrity_report.py
```

**Output esperado**:
```json
{
  "integrity_check": ["ok"],
  "foreign_key_check": [],
  "quick_check": ["ok"],
  "errors": []
}
```

---

#### 2. Migrar para PostgreSQL

```powershell
# Passo 1: Criar banco no Postgres
psql -U postgres -c "CREATE DATABASE dac_db;"

# Passo 2: Executar script de schema
python scripts/init_postgres_schema.py

# Passo 3: Verificar conexão
python scripts/check_postgres_connection.py
```

---

#### 3. Popular Dados de Teste

```powershell
# Inserir 1000 registros de exemplo
python scripts/populate_sample_data.py --records 1000

# Inserir apenas regiões e domicílios
python scripts/seed_sample_data.py --tables regions,households
```

---

### Ferramentas de Linha de Comando

#### Acessar Banco SQLite Manualmente

```powershell
# Abrir shell SQLite
sqlite3 "Versão PY\data\dac_database.db"

# Comandos úteis dentro do shell
.tables                    # Listar tabelas
.schema regions            # Ver estrutura de uma tabela
SELECT COUNT(*) FROM individuals;  # Contar registros
.quit                      # Sair
```

---

#### Backup do Banco

```powershell
# Backup simples (cópia do arquivo)
Copy-Item "Versão PY\data\dac_database.db" "Versão PY\data\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"

# Backup com dump SQL (restaurável em outros BDs)
sqlite3 "Versão PY\data\dac_database.db" .dump > backup.sql
```

---

#### Restaurar Backup

```powershell
# Restaurar de arquivo .db
Copy-Item "backup_20251106.db" "Versão PY\data\dac_database.db" -Force

# Restaurar de dump SQL
sqlite3 "Versão PY\data\dac_database.db" < backup.sql
```

---

## 🔧 Manutenção e Monitoramento

### Verificações Automáticas

#### 1. Status do Servidor

```python
from src.database.database_manager import DatabaseManager

db = DatabaseManager()
db.initialize_database()

status = db.get_server_status()
print(status)
```

**Retorno**:
```json
{
  "connected": true,
  "sqlite_version": "3.42.0",
  "database_path": "C:/Users/.../dac_database.db",
  "file_size_bytes": 1048576,
  "file_size_human": "1.00 MB",
  "uptime_seconds": 3600,
  "uptime_human": "1h 0m 0s",
  "tables_count": 5,
  "indexes_count": 15
}
```

---

#### 2. Métricas de Performance

```python
metrics = db.get_performance_metrics()
print(metrics)
```

**Retorno**:
```json
{
  "page_count": 256,
  "page_size": 4096,
  "database_size_bytes": 1048576,
  "freelist_count": 12,
  "journal_mode": "wal",
  "synchronous": "1",
  "cache_size": 10000
}
```

---

#### 3. Tabelas Maiores

```python
top_tables = db.get_top_tables_by_rows(limit=5)
for table in top_tables:
    print(f"{table['name']}: {table['rows']} registros")
```

**Output**:
```
individuals: 45230 registros
device_usage: 38456 registros
internet_usage: 38456 registros
households: 15000 registros
regions: 5 registros
```

---

### Operações de Manutenção

#### VACUUM (Compactar Banco)

Remove espaço livre e reorganiza o arquivo.

```python
db.run_maintenance('VACUUM')
```

**Quando usar?**
- Após deletar muitos registros
- Mensalmente em produção
- Quando `freelist_count` > 1000

**Resultado**: Reduz tamanho do arquivo em até 50%

---

#### ANALYZE (Atualizar Estatísticas)

Atualiza estatísticas do query planner.

```python
db.run_maintenance('ANALYZE')
```

**Quando usar?**
- Após inserção/atualização em massa
- Semanalmente em produção
- Quando queries ficam lentas

**Resultado**: Queries 2-10x mais rápidas

---

#### REINDEX (Reconstruir Índices)

Reconstrói todos os índices.

```python
db.run_maintenance('REINDEX')
```

**Quando usar?**
- Após corrupção de dados
- Raramente (é pesado)

---

### Monitoramento em Produção

#### Logs Estruturados

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Query executada", extra={
    'query_time': 0.052,
    'table': 'individuals',
    'rows_returned': 1234
})
```

**Arquivos de Log**: `Versão PY/logs/dac_structured_YYYYMMDD.json`

---

#### Alertas Sugeridos

| Métrica | Threshold | Ação |
|---------|-----------|------|
| `file_size_bytes` | > 1 GB | VACUUM + Arquivamento |
| `freelist_count` | > 5000 | VACUUM urgente |
| Query time | > 1s | ANALYZE + revisar índices |
| Conexões falhas | > 5/min | Reiniciar aplicação |

---

### Checklist de Manutenção Periódica

**Diário**:
- [ ] Verificar logs de erro
- [ ] Checar `get_server_status()` via dashboard

**Semanal**:
- [ ] Executar `ANALYZE`
- [ ] Revisar queries lentas (> 100ms)
- [ ] Backup incremental

**Mensal**:
- [ ] Executar `VACUUM`
- [ ] Executar `check_database_integrity()`
- [ ] Backup completo
- [ ] Revisar tamanho das tabelas

**Trimestral**:
- [ ] Revisar índices (adicionar/remover)
- [ ] Migrar dados antigos para arquivo
- [ ] Testar restauração de backup

---

## 📊 Considerações Técnicas

### Decisões de Arquitetura

#### Por Que ORM (SQLAlchemy)?

| ✅ Vantagens | ⚠️ Desvantagens |
|-------------|-----------------|
| Código mais legível | Overhead de performance (~10-15%) |
| Proteção contra SQL injection | Curva de aprendizado |
| Migrations automáticas | Queries complexas ficam verbosas |
| Portável entre BDs | Debug mais difícil |

**Exemplo comparativo**:

```python
# SQL Raw (perigoso!)
query = f"SELECT * FROM users WHERE id = {user_id}"  # ❌ SQL injection

# SQLAlchemy (seguro)
user = session.query(User).filter(User.id == user_id).first()  # ✅
```

---

#### Por Que Múltiplos Índices?

**Sem índice**:
```sql
-- Scan completo: 45.000 registros em 250ms
SELECT * FROM individuals WHERE age > 60 AND has_disability = 1;
```

**Com índice composto**:
```sql
-- Uso de idx_individual_disability_age: 1.200 registros em 5ms
CREATE INDEX idx_individual_disability_age ON individuals(has_disability, age);
```

**Trade-off**:
- ✅ Queries 50-100x mais rápidas
- ⚠️ Escritas 10-15% mais lentas (atualiza índices)
- ⚠️ Tamanho do arquivo +20%

---

### Escalabilidade

#### Limites do SQLite

| Métrica | Limite Teórico | Limite Prático |
|---------|----------------|----------------|
| Tamanho do banco | 281 TB | 1-2 GB (performance) |
| Registros por tabela | Ilimitado | ~10 milhões |
| Escritas concorrentes | 1 | 1 |
| Leituras concorrentes | Ilimitado | ~1000/s |

**Quando migrar para PostgreSQL?**

```
Indicadores de que SQLite não é mais suficiente:
✓ Mais de 100.000 registros/dia
✓ Mais de 5 usuários escrevendo simultaneamente
✓ Necessidade de full-text search avançado
✓ Replicação master-slave
✓ Particionamento de tabelas
```

---

#### Estratégias de Crescimento

**1. Particionamento de Dados**:
```python
# Separar dados por ano
db_2024 = DatabaseManager('data/dac_2024.db')
db_2025 = DatabaseManager('data/dac_2025.db')
```

**2. Arquivamento**:
```sql
-- Mover dados antigos para tabela de arquivo
INSERT INTO individuals_archive SELECT * FROM individuals 
WHERE created_at < '2024-01-01';

DELETE FROM individuals WHERE created_at < '2024-01-01';
```

**3. Cache de Agregações**:
```python
# Pré-calcular estatísticas pesadas
cache = {
    'total_individuals': 45230,
    'avg_age': 32.5,
    'internet_usage_rate': 0.78
}
# Atualizar diariamente
```

---

### Segurança

#### Proteções Implementadas

✅ **Queries Parametrizadas**:
```python
# ❌ Vulnerável
session.execute(f"SELECT * FROM users WHERE name = '{name}'")

# ✅ Seguro
session.execute(text("SELECT * FROM users WHERE name = :name"), {'name': name})
```

✅ **Foreign Keys**:
- Previne órfãos (indivíduos sem domicílio)
- `PRAGMA foreign_keys=ON` ativo

✅ **Validações**:
```python
class Individual(Base):
    age = Column(Integer, CheckConstraint('age >= 0 AND age <= 120'))
```

---

#### Recomendações Adicionais

**Para Desenvolvimento**:
- Banco em `.gitignore` (não commitar dados)
- Seeds deterministicos para testes

**Para Produção**:
- Criptografia do arquivo SQLite (SQLCipher)
- Backup automático (3-2-1: 3 cópias, 2 mídias, 1 offsite)
- SSL obrigatório para Postgres
- Rate limiting em APIs

---

### Performance: Queries Típicas Otimizadas

#### 1. Taxa de Acesso à Internet por Região

```python
# ❌ Lento (3 queries separadas)
regions = session.query(Region).all()
for region in regions:
    households = session.query(Household).filter_by(region_id=region.id).all()
    # ...

# ✅ Rápido (1 query com JOIN)
results = session.query(
    Region.name,
    func.count(Household.id).label('total'),
    func.sum(case((Household.has_internet == True, 1), else_=0)).label('with_internet')
).join(Household).group_by(Region.id).all()
```

**Ganho**: 50ms → 8ms

---

#### 2. Indivíduos com Deficiência por Faixa Etária

```python
# Usa índice idx_individual_disability_age
results = session.query(
    case(
        (Individual.age < 18, '0-17'),
        (Individual.age < 60, '18-59'),
        (Individual.age >= 60, '60+')
    ).label('age_group'),
    func.count(Individual.id)
).filter(Individual.has_disability == True)\
 .group_by('age_group').all()
```

**Ganho**: 120ms → 12ms (índice composto)

---

### Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| **Corrupção de dados** | Baixa | Alto | Backups diários + `check_integrity()` |
| **Crescimento descontrolado** | Média | Médio | VACUUM mensal + alertas de tamanho |
| **Queries lentas** | Alta | Baixo | ANALYZE semanal + monitoring |
| **Concorrência** | Média | Alto | Migrar para Postgres se necessário |
| **Downtime** | Baixa | Alto | Read replicas + failover |

---

### Próximos Passos Sugeridos

**Curto Prazo (1-2 semanas)**:
1. ✅ Adicionar testes automatizados de integridade
2. ✅ Configurar backup automático diário
3. ✅ Implementar monitoring de query performance

**Médio Prazo (1-3 meses)**:
1. ⏳ Migrar para PostgreSQL em staging
2. ⏳ Implementar cache Redis para agregações
3. ⏳ Criar API GraphQL para queries complexas

**Longo Prazo (6+ meses)**:
1. 🔮 Particionar dados por ano
2. 🔮 Implementar full-text search (Elasticsearch)
3. 🔮 Data warehouse para analytics (ClickHouse)

---

## 📚 Referências e Recursos

### Documentação Oficial

- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **SQLite**: https://www.sqlite.org/docs.html
- **Next.js**: https://nextjs.org/docs
- **PostgreSQL**: https://www.postgresql.org/docs/

### Ferramentas Recomendadas

- **DB Browser for SQLite**: GUI para explorar banco
- **pgAdmin**: GUI para PostgreSQL
- **DBeaver**: Cliente universal de banco de dados
- **Postman**: Testar APIs

### Contato e Suporte

Para dúvidas sobre a implementação do banco de dados:
- Repositório: https://github.com/FenixMaker/DAC_2025
- Issues: Abra uma issue no GitHub
- Documentação adicional: Ver pasta `/documentacao`

---

**Última atualização**: 6 de novembro de 2025  
**Autor**: Equipe DAC 2025  
**Versão**: 1.0
