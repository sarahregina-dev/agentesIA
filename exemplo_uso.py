"""
Exemplo de uso do sistema de simulação de agentes racionais
"""

from simulador import SimuladorAgentes
from environment import Environment
from agent_base import AgenteReativoSimples

def exemplo_basico():
    """Exemplo básico de uso do sistema"""
    print("=== EXEMPLO BÁSICO ===")
    
    # Criar um ambiente
    ambiente = Environment(seed=42)
    print("Ambiente criado:")
    ambiente.imprimir_grid()
    
    # Criar um agente
    agente = AgenteReativoSimples()
    
    # Executar alguns ciclos
    print("\nExecutando 5 ciclos...")
    for i in range(5):
        print(f"\nCiclo {i+1}:")
        continuar = agente.executar_ciclo(ambiente)
        ambiente.imprimir_grid()
        
        if not continuar:
            print("Agente parou de executar.")
            break
    
    # Mostrar estatísticas
    stats = agente.obter_estatisticas()
    print(f"\nEstatísticas do agente:")
    print(f"Pontos coletados: {stats['pontos_coletados']}")
    print(f"Energia gasta: {stats['energia_gasta']}")
    print(f"Total de ações: {stats['total_acoes']}")

def exemplo_simulacao_completa():
    """Exemplo de simulação completa"""
    print("\n=== SIMULAÇÃO COMPLETA ===")
    
    # Criar simulador com poucas simulações para exemplo
    simulador = SimuladorAgentes(num_simulacoes=3, seed_base=100)
    
    # Executar simulações
    print("Executando simulações...")
    simulador.executar_todas_simulacoes()
    
    # Gerar relatório
    print("\nGerando relatório...")
    relatorio = simulador.gerar_relatorio()
    
    # Mostrar apenas uma parte do relatório
    linhas = relatorio.split('\n')
    print("\nResultados resumidos:")
    for linha in linhas:
        if "RANKING" in linha or "º -" in linha:
            print(linha)

def exemplo_agente_individual():
    """Exemplo de demonstração de agente individual"""
    print("\n=== DEMONSTRAÇÃO DE AGENTE INDIVIDUAL ===")
    
    simulador = SimuladorAgentes()
    
    # Demonstrar agente BDI (índice 4)
    print("Demonstrando Agente BDI...")
    resultado = simulador.demonstrar_agente_individual(
        agente_index=4, 
        seed=123, 
        mostrar_passos=False  # Não mostrar cada passo para ser mais rápido
    )
    
    print(f"\nResultado da demonstração:")
    print(f"Agente: {resultado['agente']}")
    print(f"Ciclos executados: {resultado['ciclos']}")
    print(f"Pontos coletados: {resultado['stats_agente']['pontos_coletados']}")
    print(f"Eficiência energética: {resultado['stats_agente']['pontos_por_energia']:.3f}")

def exemplo_comparacao_rapida():
    """Exemplo de comparação rápida entre agentes"""
    print("\n=== COMPARAÇÃO RÁPIDA ===")
    
    # Criar simulador
    simulador = SimuladorAgentes(num_simulacoes=2, seed_base=200)
    
    # Executar simulações
    simulador.executar_todas_simulacoes()
    
    # Análise rápida
    analise = simulador.analisar_resultados()
    
    print("\nComparação de eficiência energética:")
    for agente, dados in analise.items():
        print(f"{agente}: {dados['eficiencia_energetica_media']:.3f} pontos/energia")
    
    print("\nComparação de taxa de sucesso:")
    for agente, dados in analise.items():
        print(f"{agente}: {dados['taxa_sucesso']*100:.1f}%")

if __name__ == "__main__":
    print("EXEMPLOS DE USO DO SISTEMA DE AGENTES RACIONAIS")
    print("=" * 60)
    
    # Executar exemplos
    exemplo_basico()
    exemplo_agente_individual()
    exemplo_comparacao_rapida()
    exemplo_simulacao_completa()
    
    print("\n" + "=" * 60)
    print("Exemplos concluídos!")
    print("Para uso interativo, execute: python main.py")
