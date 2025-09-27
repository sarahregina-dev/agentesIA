# Instruções para o Trabalho - Agentes Racionais

## Objetivo do Trabalho
Implementar e comparar o desempenho de quatro tipos de agentes racionais em um ambiente simulado: Robô Aspirador Inteligente.

## O que foi implementado

### ✅ Ambiente Simulado
- **Grid 5x5** representando uma casa com diferentes tipos de sujeira
- **Tipos de sujeira**: Poeira (1 ponto), Líquido (2 pontos), Detritos (3 pontos)
- **Obstáculos**: Móveis fixos em posições específicas
- **Bateria limitada**: 30 unidades de energia
- **Geração aleatória** do ambiente com seeds controláveis

### ✅ Percepção do Agente
- Conteúdo da casa atual e das quatro casas vizinhas
- Localização [x, y] do agente
- Nível de bateria atual

### ✅ Ações Possíveis
- Mover Norte (N), Sul (S), Leste (L), Oeste (O)
- Aspirar (ASPIRAR)
- Parar (PARAR)

### ✅ Custos de Ação
- Mover: 1 unidade de energia
- Aspirar: 2 unidades de energia
- Parar: 0 unidades de energia

## Agentes Implementados

### 1. Agente Reativo Simples ✅
- **Característica**: Reage diretamente às percepções atuais
- **Comportamento**: Se há sujeira, aspira; senão, move aleatoriamente
- **Sem memória** ou planejamento

### 2. Agente Baseado em Modelo ✅
- **Característica**: Mantém um modelo interno do ambiente
- **Comportamento**: Lembra posições visitadas e sujeira conhecida
- **Estratégia**: Exploração sistemática de posições não visitadas

### 3. Agente Baseado em Objetivos ✅
- **Característica**: Planeja para alcançar objetivos específicos
- **Comportamento**: Cria planos para limpar sujeira de maior valor
- **Estratégia**: Busca orientada por objetivos com priorização

### 4. Agente Baseado em Utilidade ✅
- **Característica**: Maximiza utilidade considerando custos e benefícios
- **Comportamento**: Calcula utilidade de cada ação possível
- **Estratégia**: Otimização baseada em função de utilidade

### 5. Agente BDI ✅
- **Característica**: Arquitetura cognitiva com crenças, desejos e intenções
- **Comportamento**: Estado emocional influencia decisões
- **Estratégia**: Comportamento adaptativo e sofisticado

## Sistema de Avaliação

### Métricas Implementadas
- **Pontos Coletados**: Total de pontos obtidos pela limpeza
- **Eficiência Energética**: Pontos por unidade de energia gasta
- **Percentual de Limpeza**: Porcentagem do ambiente limpo
- **Taxa de Sucesso**: Porcentagem de simulações que limparam >95% do ambiente
- **Movimentos Inválidos**: Número de tentativas de movimento bloqueadas
- **Ciclos Executados**: Número total de ciclos antes de parar

## Como Executar o Trabalho

### 1. Instalação
```bash
pip install -r requirements.txt
```

### 2. Execução Interativa
```bash
python main.py
```

### 3. Opções Disponíveis
1. **Simulação Completa**: Executa múltiplas simulações para todos os agentes
2. **Demonstração Individual**: Mostra o comportamento de um agente específico
3. **Gerar Relatório**: Cria relatório detalhado dos resultados
4. **Gerar Gráficos**: Produz gráficos comparativos
5. **Simulação Rápida**: Execução rápida com 5 testes por agente

### 4. Exemplo de Uso Rápido
```bash
python exemplo_uso.py
```

## Resultados dos Testes

### Ranking por Eficiência Energética (pontos/energia):
1. **Agente Reativo Simples**: 0.472
2. **Agente Baseado em Utilidade**: 0.460
3. **Agente Baseado em Modelo**: 0.443
4. **Agente BDI**: 0.389
5. **Agente Baseado em Objetivos**: 0.274

### Ranking por Percentual de Limpeza:
1. **Agente Baseado em Utilidade**: 77.3%
2. **Agente Baseado em Modelo**: 76.0%
3. **Agente Reativo Simples**: 74.7%
4. **Agente Baseado em Objetivos**: 62.7%
5. **Agente BDI**: 52.0%

## Arquivos do Projeto

- `environment.py` - Classe do ambiente simulado
- `agent_base.py` - Classe base e agentes reativo/modelo
- `agents.py` - Agentes baseados em objetivos/utilidade/BDI
- `simulador.py` - Sistema de simulação e comparação
- `main.py` - Programa principal com interface
- `exemplo_uso.py` - Exemplos de uso
- `requirements.txt` - Dependências
- `README.md` - Documentação completa

## Para a Apresentação (07/10/2025)

### Demonstração Recomendada:
1. **Mostrar o ambiente**: Executar `python main.py` → Opção 2 → Agente BDI → Modo passo a passo
2. **Comparação rápida**: Opção 5 (Simulação rápida)
3. **Relatório completo**: Opção 1 (Simulação completa) → Opção 3 (Gerar relatório)
4. **Gráficos**: Opção 4 (Gerar gráficos) - se matplotlib estiver disponível

### Pontos para Destacar:
- **Diferentes arquiteturas** de agentes implementadas
- **Métricas de comparação** objetivas
- **Comportamentos distintos** observados
- **Eficiência vs Efetividade** dos diferentes agentes
- **Complexidade vs Performance** trade-offs

### Resultados Esperados:
- **Agente Reativo**: Rápido mas menos eficiente
- **Agente Baseado em Modelo**: Mais sistemático na exploração
- **Agente Baseado em Objetivos**: Melhor em tarefas específicas
- **Agente Baseado em Utilidade**: Balanceamento entre eficiência e efetividade
- **Agente BDI**: Comportamento mais sofisticado e adaptativo

## Observações Técnicas

- **Seeds controláveis** para reprodutibilidade
- **Estatísticas detalhadas** para análise
- **Interface amigável** para demonstrações
- **Código modular** e bem documentado
- **Tratamento de erros** robusto

O projeto está completo e pronto para apresentação!
