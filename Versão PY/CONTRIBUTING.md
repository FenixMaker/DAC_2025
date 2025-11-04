# Guia de Contribuição - Sistema DAC

## Visão Geral

Este documento estabelece as diretrizes para contribuições ao Sistema DAC, um projeto acadêmico para análise de exclusão digital no Brasil. Seguir estas diretrizes garante a qualidade e consistência do código.

## 🚀 Primeiros Passos

### Configuração do Ambiente

1. **Fork e Clone**:
```bash
git clone https://github.com/[seu-usuario]/DAC-Sistema-Analise-Exclusao-Digital.git
cd DAC-Sistema-Analise-Exclusao-Digital
```

2. **Ambiente Virtual**:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Dependências**:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dependências de desenvolvimento
```

4. **Configuração Inicial**:
```bash
# Copiar configurações template
cp config/database_config.template.json config/database_config.json
cp config/logging_config.template.json config/logging_config.json
```

## 📝 Padrões de Desenvolvimento

### Estrutura de Código

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: [nome_do_modulo]
Descrição: [descrição_breve]
Autor: [seu_nome]
Data: [data_criacao]
"""

import os
import sys
from typing import Optional, List, Dict

class ExemploClasse:
    """
    Classe exemplo seguindo padrões do DAC.
    
    Attributes:
        atributo_exemplo (str): Descrição do atributo
    """
    
    def __init__(self, parametro: str) -> None:
        """
        Inicializa a classe.
        
        Args:
            parametro (str): Descrição do parâmetro
        """
        self.atributo_exemplo = parametro
    
    def metodo_exemplo(self, entrada: str) -> Optional[str]:
        """
        Método exemplo com documentação completa.
        
        Args:
            entrada (str): Dados de entrada
            
        Returns:
            Optional[str]: Resultado processado ou None
            
        Raises:
            ValueError: Quando entrada é inválida
        """
        if not entrada:
            raise ValueError("Entrada não pode ser vazia")
        
        return entrada.upper()
```

### Convenções de Nomenclatura

- **Arquivos**: `snake_case.py`
- **Classes**: `PascalCase`
- **Funções/Métodos**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Variáveis**: `snake_case`

### Documentação

```python
def processar_dados_dac(dados: pd.DataFrame, filtros: Dict[str, Any]) -> pd.DataFrame:
    """
    Processa dados do DAC aplicando filtros específicos.
    
    Esta função realiza limpeza, validação e transformação dos dados
    de acordo com os padrões estabelecidos pelo DAC.
    
    Args:
        dados (pd.DataFrame): DataFrame com dados brutos
        filtros (Dict[str, Any]): Dicionário com critérios de filtro
            - 'data_inicio': Data inicial para filtro temporal
            - 'data_fim': Data final para filtro temporal
            - 'regiao': Lista de regiões para incluir
    
    Returns:
        pd.DataFrame: DataFrame processado e filtrado
        
    Raises:
        ValueError: Quando dados estão em formato inválido
        KeyError: Quando filtros obrigatórios estão ausentes
        
    Example:
        >>> dados = pd.read_csv('dados_dac.csv')
        >>> filtros = {'data_inicio': '2024-01-01', 'regiao': ['SP', 'RJ']}
        >>> resultado = processar_dados_dac(dados, filtros)
    """
```

## 🔄 Fluxo de Trabalho Git

### Branches

```
main
├── develop
│   ├── feature/nova-funcionalidade
│   ├── feature/melhorar-interface
│   └── hotfix/corrigir-bug-critico
└── release/v2.0.0
```

### Nomenclatura de Branches

- `feature/[descrição]`: Novas funcionalidades
- `bugfix/[descrição]`: Correção de bugs
- `hotfix/[descrição]`: Correções urgentes
- `release/[versão]`: Preparação de releases
- `docs/[descrição]`: Atualizações de documentação

### Commits Semânticos

```bash
# Formato
tipo(escopo): descrição

# Tipos permitidos
feat:     Nova funcionalidade
fix:      Correção de bug
docs:     Documentação
style:    Formatação (sem mudança de lógica)
refactor: Refatoração de código
test:     Adição ou correção de testes
chore:    Tarefas de manutenção

# Exemplos
feat(ui): adicionar janela de configurações avançadas
fix(db): corrigir problema de conexão PostgreSQL
docs(readme): atualizar instruções de instalação
test(utils): adicionar testes para validador de dados
```

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── unit/           # Testes unitários
├── integration/    # Testes de integração
├── performance/    # Testes de performance
├── fixtures/       # Dados de teste
└── utils/          # Utilitários de teste
```

### Executando Testes

```bash
# Todos os testes
python -m pytest tests/

# Testes específicos
python -m pytest tests/unit/test_database_manager.py

# Com cobertura
python -m pytest --cov=src tests/

# Testes de performance
python -m pytest tests/performance/ --benchmark-only
```

### Escrevendo Testes

```python
import pytest
import pandas as pd
from unittest.mock import Mock, patch

from src.modules.data_importer import DataImporter

class TestDataImporter:
    """Testes para o módulo DataImporter."""
    
    @pytest.fixture
    def sample_data(self):
        """Fixture com dados de exemplo."""
        return pd.DataFrame({
            'id': [1, 2, 3],
            'nome': ['João', 'Maria', 'Pedro'],
            'idade': [25, 30, 35]
        })
    
    @pytest.fixture
    def data_importer(self):
        """Fixture com instância do DataImporter."""
        return DataImporter()
    
    def test_importar_csv_sucesso(self, data_importer, tmp_path):
        """Testa importação bem-sucedida de arquivo CSV."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,nome,idade\n1,João,25\n2,Maria,30")
        
        # Act
        resultado = data_importer.importar_csv(str(csv_file))
        
        # Assert
        assert len(resultado) == 2
        assert 'id' in resultado.columns
        assert resultado.iloc[0]['nome'] == 'João'
    
    def test_importar_csv_arquivo_inexistente(self, data_importer):
        """Testa comportamento com arquivo inexistente."""
        with pytest.raises(FileNotFoundError):
            data_importer.importar_csv("arquivo_inexistente.csv")
    
    @patch('src.modules.data_importer.pd.read_csv')
    def test_importar_csv_com_mock(self, mock_read_csv, data_importer, sample_data):
        """Testa importação usando mock."""
        # Arrange
        mock_read_csv.return_value = sample_data
        
        # Act
        resultado = data_importer.importar_csv("qualquer_arquivo.csv")
        
        # Assert
        mock_read_csv.assert_called_once_with("qualquer_arquivo.csv")
        assert len(resultado) == 3
```

## 📋 Pull Requests

### Checklist Obrigatório

- [ ] **Código**: Segue padrões de estilo do projeto
- [ ] **Testes**: Todos os testes passam (unitários e integração)
- [ ] **Cobertura**: Cobertura de testes mantida ou melhorada
- [ ] **Documentação**: Docstrings atualizadas
- [ ] **Segurança**: Sem credenciais ou dados sensíveis
- [ ] **Performance**: Sem degradação significativa
- [ ] **Compatibilidade**: Funciona com Python 3.8+

### Template de PR

```markdown
## 📋 Descrição

Breve descrição das mudanças implementadas.

## 🔄 Tipo de Mudança

- [ ] Bug fix (correção que resolve um problema)
- [ ] Nova funcionalidade (mudança que adiciona funcionalidade)
- [ ] Breaking change (mudança que quebra compatibilidade)
- [ ] Documentação (mudanças apenas na documentação)

## 🧪 Como Testar

1. Passos para reproduzir/testar
2. Dados de teste necessários
3. Comportamento esperado

## 📸 Screenshots (se aplicável)

## 📋 Checklist

- [ ] Meu código segue os padrões do projeto
- [ ] Realizei auto-revisão do código
- [ ] Comentei código complexo
- [ ] Atualizei documentação relevante
- [ ] Testes passam localmente
- [ ] Adicionei testes para novas funcionalidades
```

## 🔍 Code Review

### Para Revisores

- ✅ **Funcionalidade**: O código faz o que deveria fazer?
- ✅ **Legibilidade**: O código é claro e bem documentado?
- ✅ **Performance**: Há otimizações óbvias possíveis?
- ✅ **Segurança**: Não há vulnerabilidades introduzidas?
- ✅ **Testes**: A cobertura é adequada?

### Para Autores

- 📝 Responda a todos os comentários
- 🔄 Faça commits adicionais para correções
- 📋 Marque como resolvido após implementar sugestões
- 🤝 Seja receptivo ao feedback

## 🛠️ Ferramentas de Desenvolvimento

### Linting e Formatação

```bash
# Instalar ferramentas
pip install black flake8 isort mypy

# Formatação automática
black src/ tests/

# Ordenação de imports
isort src/ tests/

# Verificação de estilo
flake8 src/ tests/

# Verificação de tipos
mypy src/
```

### Pre-commit Hooks

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Executar manualmente
pre-commit run --all-files
```

## 📊 Monitoramento de Qualidade

### Métricas Importantes

- **Cobertura de Testes**: Mínimo 80%
- **Complexidade Ciclomática**: Máximo 10 por função
- **Duplicação de Código**: Máximo 3%
- **Vulnerabilidades**: Zero tolerância

### Ferramentas de Análise

```bash
# Cobertura
coverage run -m pytest tests/
coverage report
coverage html

# Complexidade
radon cc src/ --min B

# Duplicação
pylint src/ --disable=all --enable=duplicate-code
```

## 🚨 Resolução de Problemas

### Problemas Comuns

1. **Testes Falhando**:
   ```bash
   # Limpar cache
   pytest --cache-clear
   
   # Executar teste específico
   pytest tests/unit/test_specific.py::test_function -v
   ```

2. **Problemas de Dependências**:
   ```bash
   # Reinstalar dependências
   pip install --force-reinstall -r requirements.txt
   ```

3. **Conflitos de Merge**:
   ```bash
   # Atualizar branch
   git fetch origin
   git rebase origin/develop
   ```

## 📞 Suporte

### Canais de Comunicação

- 📧 **Email**: dev.dac@[dominio]
- 💬 **Chat**: Canal #dac-desenvolvimento
- 📋 **Issues**: GitHub Issues com labels apropriadas
- 📚 **Wiki**: Documentação técnica detalhada

### Labels para Issues

- `bug`: Problemas no código
- `enhancement`: Melhorias
- `documentation`: Documentação
- `good first issue`: Bom para iniciantes
- `help wanted`: Precisa de ajuda
- `priority-high`: Alta prioridade
- `security`: Questões de segurança

---

## 🎯 Objetivos de Qualidade

Nosso compromisso é manter:
- 📈 **Alta qualidade** de código
- 🔒 **Segurança** em primeiro lugar
- 📚 **Documentação** completa
- 🧪 **Cobertura** de testes adequada
- 🤝 **Colaboração** efetiva

**Obrigado por contribuir com o Sistema DAC!** 🚀

---

*Última atualização: [Data] | Versão: 1.0 | Mantido por: Equipe de Desenvolvimento DAC*