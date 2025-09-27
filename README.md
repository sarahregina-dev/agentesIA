# Robô Aspirador Inteligente - Comparação de Agentes Racionais

Este projeto implementa e compara o desempenho de cinco tipos diferentes de agentes racionais em um ambiente simulado de robô aspirador inteligente.

## Objetivo

Implementar e comparar o desempenho de quatro tipos de agentes racionais em um ambiente simulado:
- **Agente Reativo Simples**: Reage diretamente às percepções
- **Agente Baseado em Modelo**: Mantém um modelo interno do ambiente
- **Agente Baseado em Objetivos**: Planeja para alcançar objetivos específicos
- **Agente Baseado em Utilidade**: Maximiza utilidade considerando custos e benefícios
- **Agente BDI**: Arquitetura cognitiva com crenças, desejos e intenções

## Cenário

### Ambiente
- Grid 5x5 representando uma casa
- Tipos de sujeira: Poeira (1 ponto), Líquido (2 pontos), Detritos (3 pontos)
- Obstáculos fixos em posições específicas
- Bateria limitada: 30 unidades de energia

### Percepção do Agente
- Conteúdo da casa atual e das quatro casas vizinhas
- Localização [x, y]
- Nível de bateria

### Ações Possíveis
- Mover Norte (N), Sul (S), Leste (L), Oeste (O)
- Aspirar (ASPIRAR)
- Parar (PARAR)

### Custos de Ação
- Mover: 1 unidade de energia
- Aspirar: 2 unidades de energia
- Parar: 0 unidades de energia

## Estrutura do Projeto

```
agentesIA/
├── environment.py      # Classe do ambiente simulado
├── agent_base.py       # Classe base e agentes reativo/modelo
├── agents.py          # Agentes baseados em objetivos/utilidade/BDI
├── simulador.py       # Sistema de simulação e comparação
├── main.py           # Programa principal com interface
├── requirements.txt   # Dependências do projeto
└── README.md         # Este arquivo
```

## Como Usar

### 1. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o Programa

```bash
python main.py
```

### 3. Opções Disponíveis

1. **Simulação Completa**: Executa múltiplas simulações para todos os agentes
2. **Demonstração Individual**: Mostra o comportamento de um agente específico
3. **Gerar Relatório**: Cria relatório detalhado dos resultados
4. **Gerar Gráficos**: Produz gráficos comparativos (requer matplotlib)
5. **Simulação Rápida**: Execução rápida com 5 testes por agente

### 4. Exemplo de Uso Programático

```python
from simulador import SimuladorAgentes

# Criar simulador
simulador = SimuladorAgentes(num_simulacoes=10)

# Executar simulações
simulador.executar_todas_simulacoes()

# Gerar relatório
relatorio = simulador.gerar_relatorio()
print(relatorio)

# Gerar gráficos
simulador.gerar_graficos()
```

## Métricas de Avaliação

- **Pontos Coletados**: Total de pontos obtidos pela limpeza
- **Eficiência Energética**: Pontos por unidade de energia gasta
- **Percentual de Limpeza**: Porcentagem do ambiente limpo
- **Taxa de Sucesso**: Porcentagem de simulações que limparam >95% do ambiente
- **Movimentos Inválidos**: Número de tentativas de movimento bloqueadas

## Características dos Agentes

### Agente Reativo Simples
- Reage diretamente às percepções atuais
- Sem memória ou planejamento
- Comportamento previsível e rápido

### Agente Baseado em Modelo
- Mantém modelo interno do ambiente
- Lembra posições visitadas e sujeira conhecida
- Estratégia de exploração sistemática

### Agente Baseado em Objetivos
- Planeja sequências de ações para alcançar objetivos
- Prioriza sujeira de maior valor
- Estratégia de busca orientada por objetivos

### Agente Baseado em Utilidade
- Calcula utilidade de cada ação possível
- Considera custos e benefícios
- Otimização baseada em função de utilidade

### Agente BDI
- Arquitetura cognitiva com crenças, desejos e intenções
- Estado emocional influencia decisões
- Comportamento mais complexo e adaptativo

## Resultados Esperados

Os diferentes agentes devem apresentar características distintas:

- **Agente Reativo**: Rápido mas menos eficiente
- **Agente Baseado em Modelo**: Mais sistemático na exploração
- **Agente Baseado em Objetivos**: Melhor em tarefas específicas
- **Agente Baseado em Utilidade**: Balanceamento entre eficiência e efetividade
- **Agente BDI**: Comportamento mais sofisticado e adaptativo

## Contribuições

Este projeto foi desenvolvido como trabalho acadêmico para comparação de arquiteturas de agentes racionais. Contribuições e melhorias são bem-vindas!

## Licença

Projeto acadêmico para fins educacionais.