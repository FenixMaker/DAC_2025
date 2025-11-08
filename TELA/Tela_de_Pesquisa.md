## Versão Web (Next.js)

### Como Funciona
A tela de consultas Web permite pesquisar indivíduos e domicílios através de uma interface moderna e responsiva:

**Componentes:**
- **Filtros** (`ConsultasFilters`): Campo de busca por nome/ID e seleção de região
- **Tabela** (`ConsultasTable`): Exibe resultados paginados (10 por página)
- **Paginação**: Botões "Anterior" e "Próxima" para navegar entre páginas

**Fluxo:**
1. Usuário acessa `/consultas`
2. A tabela carrega automaticamente os primeiros 10 registros
3. Ao clicar em "Próxima", faz nova requisição para `/api/individuos?page=2&limit=10`
4. O endpoint proxy repassa para o backend real (configurado em `NEXT_PUBLIC_DAC_API_URL`)
5. Resultados são exibidos com: ID, Nome, Idade, Região, Domicílio, Dispositivos e Internet (ícone)

**Colunas da Tabela:**
- ID, Nome, Idade, Região, Domicílio, Dispositivos, Internet (✓/✗)

**Limitações Atuais:**
- Filtros ainda não estão conectados ao fetch (apenas visual)
- Não há exportação de resultados
- Busca textual não está implementada

---

## Versão Desktop/Python (Tkinter)

### Como Funciona
A janela de consultas Desktop oferece filtragem avançada com múltiplos critérios e exportação de dados:

**Filtros Disponíveis:**
- 🌍 **Região**: Carregado dinamicamente do banco (Norte, Sul, Nordeste, etc.)
- 📅 **Faixa Etária**: Idade mínima e máxima (validação 0-150 anos)
- 👤 **Gênero**: Todos, Masculino, Feminino
- 💰 **Faixa de Renda**: Carregado dinamicamente do banco
- ♿ **Pessoa com Deficiência**: Todos, Sim, Não
- 🌐 **Acesso à Internet**: Todos, Sim, Não

**Fluxo:**
1. Janela carrega automaticamente as opções de filtros do banco de dados
2. Usuário seleciona critérios desejados (pode combinar vários filtros)
3. Clica em "Aplicar Filtros" (ou Ctrl+F)
4. Sistema valida entradas, constrói query SQL com joins e aplica filtros
5. Resultados aparecem na tabela com paginação (padrão: 100 registros por página)
6. Usuário pode navegar, exportar CSV ou gerar relatório

**Colunas da Tabela:**
- ID, Região, Idade, Gênero, Renda, Deficiência, Internet, Dispositivos

**Funcionalidades:**
- ✅ **Paginação Completa**: Botões <<, <, >, >> e controle de registros por página (50/100/200/500)
- ✅ **Exportação CSV**: Salva resultados filtrados em arquivo
- ✅ **Geração de Relatório**: Abre janela de relatórios com dados filtrados
- ✅ **Validação Robusta**: Verifica idade, coerência de filtros e conexão com BD
- ✅ **Tratamento de Erros**: Mensagens claras e logging detalhado
- ✅ **Atalhos de Teclado**: Ctrl+F (filtrar), Ctrl+R (limpar), Ctrl+E (exportar), F5 (atualizar)

**Botões:**
- Aplicar Filtros / Limpar Filtros
- Exportar Resultados
- Gerar Relatório
- Atualizar (F5)
- Fechar

---


